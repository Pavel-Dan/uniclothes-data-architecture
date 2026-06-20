"""Ventes omnicanal — web, app, boutique."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib.db import run_query
from lib.ui import inject_brand_css, page_header, render_sidebar_header

st.set_page_config(page_title="Ventes omnicanal", layout="wide")
inject_brand_css()
render_sidebar_header()
page_header("Ventes omnicanal", "Analyse des canaux e-commerce, application mobile et boutiques")

channel_stats = run_query("""
    SELECT
        channel_name,
        COUNT(*) AS lignes,
        COUNT(DISTINCT order_id) AS commandes,
        SUM(amount_eur) AS ca,
        ROUND(AVG(amount_eur)::numeric, 2) AS panier_ligne
    FROM dwh.v_sales_analytics
    GROUP BY channel_name
    ORDER BY ca DESC
""")

c1, c2, c3 = st.columns(3)
for i, row in channel_stats.iterrows():
    cols = [c1, c2, c3]
    with cols[i % 3]:
        st.metric(row["channel_name"], f"{row['ca']:,.0f} EUR", f"{int(row['commandes'])} cmd.")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("CA par canal")
    fig = px.bar(
        channel_stats, x="channel_name", y="ca",
        text="ca", color="channel_name",
        color_discrete_sequence=["#FF2D2D", "#E60000", "#B30000"],
        labels={"channel_name": "Canal", "ca": "CA (EUR)"},
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Part de marche par canal")
    fig2 = px.treemap(
        channel_stats,
        path=["channel_name"],
        values="ca",
        color="ca",
        color_continuous_scale=["#FFE0E0", "#FF2D2D"],
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Comparatif panier moyen par ligne")
fig4 = go.Figure(go.Funnel(
    y=channel_stats["channel_name"],
    x=channel_stats["panier_ligne"],
    textinfo="value+percent initial",
    marker=dict(color=["#FF2D2D", "#CC0000", "#990000"]),
))
fig4.update_layout(height=350, title="Panier moyen par transaction")
st.plotly_chart(fig4, use_container_width=True)
