"""Collection & produits — catalogue ERP + images MinIO."""

import plotly.express as px
import streamlit as st

from lib.db import run_query
from lib.images import fetch_product_image, list_bucket_objects
from lib.ui import inject_brand_css, page_header, render_sidebar_header

st.set_page_config(page_title="Collection & produits", layout="wide")
inject_brand_css()
render_sidebar_header()
page_header("Collection & produits", "Referentiel ERP lie aux assets MinIO (product_ref = cle objet)")

categories = run_query("""
    SELECT dp.category,
           COUNT(*) AS ventes,
           SUM(v.amount_eur) AS ca,
           SUM(v.quantity) AS unites
    FROM dwh.v_sales_analytics v
    JOIN dwh.dim_product dp ON v.product_ref = dp.product_ref
    GROUP BY dp.category ORDER BY ca DESC
""")

top_products = run_query("""
    SELECT dp.product_ref, dp.product_name, dp.category,
           dp.image_object_key, dp.image_url,
           SUM(v.quantity) AS unites, SUM(v.amount_eur) AS ca
    FROM dwh.v_sales_analytics v
    JOIN dwh.dim_product dp ON v.product_ref = dp.product_ref
    GROUP BY dp.product_ref, dp.product_name, dp.category, dp.image_object_key, dp.image_url
    ORDER BY ca DESC LIMIT 10
""")

catalog = run_query("""
    SELECT product_ref, product_name, category, price_eur, stock_qty,
           image_object_key, image_url
    FROM dwh.dim_product
    ORDER BY category, product_ref
""")

image_kpi = run_query("""
    SELECT
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE image_object_key IS NOT NULL) AS with_image
    FROM dwh.dim_product
""").iloc[0]

stock = run_query("""
    SELECT category,
           SUM(stock_qty) AS stock_total,
           COUNT(*) AS nb_references,
           ROUND(AVG(price_eur)::numeric, 2) AS prix_moyen
    FROM dwh.dim_product
    GROUP BY category ORDER BY stock_total DESC
""")

bucket_objects = list(list_bucket_objects())
matched_refs: set[str] = set()
for _, row in catalog.iterrows():
    image_bytes, _ = fetch_product_image(row["product_ref"], row["image_object_key"])
    if image_bytes:
        matched_refs.add(row["product_ref"])

pct_images = 100.0 * len(matched_refs) / max(len(catalog), 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Categories actives", categories["category"].nunique())
c2.metric("References produit", int(image_kpi["total"]))
c3.metric("Images MinIO trouvees", f"{len(matched_refs)}/{len(catalog)}")
c4.metric("Unites vendues", f"{int(categories['unites'].sum()):,}".replace(",", " "))

tab1, tab2, tab3, tab4 = st.tabs(["Catalogue visuel", "Categories", "Top 10 articles", "Stocks ERP"])

with tab1:
    st.caption(
        "Nommez vos fichiers MinIO `{product_ref}.jpg` (ex. UC-TS-001.jpg) "
        "dans le bucket **product-images**."
    )
    if not bucket_objects:
        st.warning(
            "Aucun objet detecte dans MinIO. Verifiez que le bucket product-images "
            "est accessible et que run_etl.cmd a ete execute."
        )
    else:
        st.info(f"{len(bucket_objects)} fichier(s) dans MinIO : {', '.join(bucket_objects[:8])}"
                + (" ..." if len(bucket_objects) > 8 else ""))

    cols = st.columns(4)
    for i, row in catalog.iterrows():
        image_bytes, object_key = fetch_product_image(row["product_ref"], row["image_object_key"])
        with cols[i % 4]:
            if image_bytes:
                st.image(image_bytes, use_container_width=True)
            else:
                st.markdown(
                    '<div style="background:#f0f0f0;height:120px;border-radius:8px;'
                    'display:flex;align-items:center;justify-content:center;color:#888;">'
                    "Pas d'image</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(f"**{row['product_name']}**")
            st.caption(f"{row['product_ref']} · {row['price_eur']} EUR")
            if object_key:
                st.caption(f"Cle MinIO : `{object_key}`")

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(
            categories, x="category", y="ca",
            color="ca", color_continuous_scale=["#FFE0E0", "#FF2D2D"],
            labels={"category": "Categorie", "ca": "CA (EUR)"},
        )
        fig.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig2 = px.sunburst(
            categories, path=["category"], values="unites",
            color="ca", color_continuous_scale="Reds",
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.bar(
        top_products.sort_values("ca"),
        x="ca", y="product_name", orientation="h",
        color="category",
        color_discrete_sequence=["#FF2D2D", "#CC0000", "#990000", "#660000", "#330000"],
        labels={"ca": "CA (EUR)", "product_name": "Produit"},
        hover_data=["product_ref", "unites", "image_object_key"],
    )
    fig3.update_layout(height=450, showlegend=True)
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        fig4 = px.bar(
            stock, x="category", y="stock_total",
            color="prix_moyen", color_continuous_scale="Reds",
            labels={"stock_total": "Stock (unites)", "category": "Categorie"},
        )
        fig4.update_layout(height=380)
        st.plotly_chart(fig4, use_container_width=True)
    with col_s2:
        st.dataframe(
            stock.rename(columns={
                "category": "Categorie", "stock_total": "Stock",
                "nb_references": "References", "prix_moyen": "Prix moyen (EUR)",
            }),
            use_container_width=True, hide_index=True,
        )
