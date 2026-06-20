"""UNICLOTHES — Portail BI Streamlit."""

import streamlit as st

from lib.db import run_query
from lib.ui import inject_brand_css, page_header, render_sidebar_header

st.set_page_config(
    page_title="UNICLOTHES BI",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_brand_css()
render_sidebar_header()

page_header(
    "UNICLOTHES Data Hub",
    "Tableaux de bord omnicanaux — e-commerce, app mobile & boutiques France",
)

try:
    kpis = run_query("""
        SELECT
            (SELECT COUNT(*) FROM dwh.fact_sales) AS ventes,
            (SELECT COUNT(*) FROM dwh.dim_customer WHERE is_active_12m) AS clients_actifs,
            (SELECT ROUND(SUM(amount_eur)::numeric, 0) FROM dwh.fact_sales) AS ca_total,
            (SELECT COUNT(*) FROM dwh.dim_store WHERE store_code <> 'ONLINE') AS boutiques
    """).iloc[0]
except Exception as exc:
    st.error(f"Impossible de se connecter a PostgreSQL : {exc}")
    st.info("Lancez d'abord `docker compose up -d` puis `.\\scripts\\run_etl.cmd`")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Lignes de vente", f"{int(kpis['ventes']):,}".replace(",", " "))
c2.metric("Clients actifs (12 mois)", f"{int(kpis['clients_actifs']):,}".replace(",", " "))
c3.metric("Chiffre d'affaires", f"{int(kpis['ca_total']):,} EUR".replace(",", " "))
c4.metric("Boutiques France", int(kpis["boutiques"]))

st.markdown("---")
st.subheader("Navigation")
st.markdown("""
Utilisez le **menu lateral** pour explorer les tableaux de bord :

| Dashboard | Contenu |
|-----------|---------|
| **Vue executive** | KPIs strategiques & tendances mensuelles |
| **Ventes omnicanal** | Repartition web / app / boutique, treemap et funnel |
| **Performance boutiques** | Classement magasins & regions |
| **Collection & produits** | Top articles, categories, panier moyen |
| **Qualite data & UNICLUB** | KPIs gouvernance, consentements, doublons |
""")

st.markdown(
    '<div class="uc-alert">'
    "<strong>Monitoring infrastructure</strong> : Grafana reste disponible sur "
    "<a href='http://localhost:3001' target='_blank'>localhost:3001</a> "
    "(connexions PostgreSQL, sante des services)."
    "</div>",
    unsafe_allow_html=True,
)

st.caption("UNICLOTHES — Bloc 2 Architecture de donnees | Pavel-Dan DIACONU")
