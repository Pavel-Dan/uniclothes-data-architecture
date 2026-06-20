"""Performance boutiques — magasins physiques France."""

import plotly.express as px
import streamlit as st

from lib.db import run_query
from lib.ui import inject_brand_css, page_header, render_sidebar_header

st.set_page_config(page_title="Performance boutiques", layout="wide")
inject_brand_css()
render_sidebar_header()
page_header("Performance boutiques", "10 boutiques UNICLOTHES en France — ventes & regions")

stores = run_query("""
    SELECT
        ds.store_name,
        ds.city,
        ds.region,
        COUNT(*) AS transactions,
        SUM(v.amount_eur) AS ca,
        ROUND(AVG(v.amount_eur)::numeric, 2) AS ticket_moyen
    FROM dwh.v_sales_analytics v
    JOIN dwh.dim_store ds ON v.store_name = ds.store_name
    WHERE ds.store_code <> 'ONLINE'
    GROUP BY ds.store_name, ds.city, ds.region
    ORDER BY ca DESC
""")

regions = run_query("""
    SELECT ds.region, SUM(v.amount_eur) AS ca, COUNT(*) AS transactions
    FROM dwh.v_sales_analytics v
    JOIN dwh.dim_store ds ON v.store_name = ds.store_name
    WHERE ds.store_code <> 'ONLINE'
    GROUP BY ds.region ORDER BY ca DESC
""")

if stores.empty:
    st.info("Pas de ventes boutique dans les donnees.")
    st.stop()

top = stores.iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Meilleure boutique", top["store_name"])
c2.metric("CA cumule boutiques", f"{stores['ca'].sum():,.0f} EUR")
c3.metric("Regions couvertes", regions["region"].nunique())

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Classement des boutiques par CA")
    fig = px.bar(
        stores.sort_values("ca"),
        x="ca", y="store_name", orientation="h",
        color="ca", color_continuous_scale=["#FFE0E0", "#FF2D2D"],
        labels={"ca": "CA (EUR)", "store_name": "Boutique"},
        hover_data=["city", "region", "transactions"],
    )
    fig.update_layout(height=500, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("CA par region")
    fig2 = px.pie(
        regions, names="region", values="ca", hole=0.35,
        color_discrete_sequence=px.colors.sequential.Reds_r,
    )
    fig2.update_layout(height=280)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Ticket moyen par boutique")
    fig3 = px.scatter(
        stores, x="transactions", y="ticket_moyen", size="ca",
        color="region", hover_name="store_name",
        color_discrete_sequence=["#FF2D2D", "#CC0000", "#990000", "#660000"],
        labels={"transactions": "Nb transactions", "ticket_moyen": "Ticket (EUR)"},
    )
    fig3.update_layout(height=280)
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Detail par boutique")
st.dataframe(
    stores.rename(columns={
        "store_name": "Boutique", "city": "Ville", "region": "Region",
        "transactions": "Transactions", "ca": "CA (EUR)", "ticket_moyen": "Ticket moyen",
    }),
    use_container_width=True,
    hide_index=True,
)
