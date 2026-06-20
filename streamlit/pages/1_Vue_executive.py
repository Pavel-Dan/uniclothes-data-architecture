"""Vue executive — KPIs strategiques."""

import plotly.express as px
import streamlit as st

from lib.db import run_query
from lib.ui import inject_brand_css, page_header, render_sidebar_header

st.set_page_config(page_title="Vue executive", layout="wide")
inject_brand_css()
render_sidebar_header()
page_header("Vue executive", "Indicateurs cles pour le Comite Data UNICLOTHES")

monthly = run_query("""
    SELECT dd.year_num, dd.month_name, dd.month_num,
           SUM(fs.amount_eur) AS ca,
           COUNT(DISTINCT fs.order_id) AS commandes,
           COUNT(DISTINCT fs.customer_key) AS clients
    FROM dwh.fact_sales fs
    JOIN dwh.dim_date dd ON fs.date_key = dd.date_key
    GROUP BY dd.year_num, dd.month_name, dd.month_num
    ORDER BY dd.year_num, dd.month_num
""")

if monthly.empty:
    st.warning("Aucune donnee - executez run_etl.cmd")
    st.stop()

latest = monthly.iloc[-1]
prev = monthly.iloc[-2] if len(monthly) > 1 else latest

c1, c2, c3, c4 = st.columns(4)
c1.metric("CA dernier mois", f"{latest['ca']:,.0f} EUR", f"{latest['ca'] - prev['ca']:+,.0f}")
c2.metric("Commandes", int(latest["commandes"]), int(latest["commandes"] - prev["commandes"]))
c3.metric("Clients uniques", int(latest["clients"]))
c4.metric("Panier moyen", f"{latest['ca'] / max(latest['commandes'], 1):,.0f} EUR")

col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Evolution du chiffre d'affaires")
    fig = px.area(
        monthly,
        x="month_name",
        y="ca",
        labels={"month_name": "Mois", "ca": "CA (EUR)"},
        color_discrete_sequence=["#FF2D2D"],
    )
    fig.update_traces(line=dict(color="#FF2D2D", width=2), fillcolor="rgba(255,45,45,0.25)")
    fig.update_layout(hovermode="x", height=380, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.subheader("Commandes par mois")
    fig2 = px.bar(
        monthly,
        x="month_name",
        y="commandes",
        text="commandes",
        labels={"month_name": "Mois", "commandes": "Commandes"},
        color_discrete_sequence=["#FF2D2D"],
    )
    fig2.update_traces(
        textposition="outside",
        marker=dict(color="#FF2D2D", line=dict(width=0)),
    )
    fig2.update_layout(showlegend=False, height=380, plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Repartition omnicanale (CA)")
channel = run_query("""
    SELECT channel_name, SUM(amount_eur) AS ca
    FROM dwh.v_sales_analytics
    GROUP BY channel_name ORDER BY ca DESC
""")
fig3 = px.pie(
    channel,
    names="channel_name",
    values="ca",
    hole=0.45,
    color_discrete_sequence=["#FF2D2D", "#CC0000", "#990000"],
)
fig3.update_traces(textposition="inside", pull=[0.02, 0, 0])
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)
