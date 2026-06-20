"""Qualite data & programme UNICLUB."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib.db import run_query
from lib.ui import inject_brand_css, page_header, render_sidebar_header

st.set_page_config(page_title="Qualite data & UNICLUB", layout="wide")
inject_brand_css()
render_sidebar_header()
page_header(
    "Qualite data & UNICLUB",
    "KPIs gouvernance Bloc 1 — doublons, emails, consentements marketing",
)

quality = run_query("""
    SELECT metric_name, metric_value, target_value, status
    FROM staging.quality_metrics ORDER BY metric_id
""")

consent = run_query("""
    SELECT
        consent_marketing,
        COUNT(*) AS nb_clients,
        COUNT(*) FILTER (WHERE is_active_12m) AS actifs
    FROM dwh.dim_customer
    GROUP BY consent_marketing
""")

sources = run_query("""
    SELECT source_system, COUNT(*) AS enregistrements
    FROM staging.customers_unified
    GROUP BY source_system ORDER BY enregistrements DESC
""")

dedup = run_query("""
    SELECT
        COUNT(*) AS golden_records,
        SUM(duplicate_count) AS raw_total,
        ROUND(100.0 * (SUM(duplicate_count) - COUNT(*)) / NULLIF(SUM(duplicate_count), 0), 1) AS taux_doublons
    FROM staging.customers_golden
""").iloc[0]

dup_row = quality[quality["metric_name"] == "duplicate_rate_pct"]
dup_val = float(dup_row["metric_value"].iloc[0]) if not dup_row.empty else float(dedup["taux_doublons"])
dup_target = float(dup_row["target_value"].iloc[0]) if not dup_row.empty else 2.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Membres UNICLUB (golden)", int(dedup["golden_records"]))
c2.metric("Taux doublons", f"{dup_val:.1f} %", f"Cible < {dup_target:.0f} %", delta_color="inverse")
c3.metric("Emails valides", "100 %" if not quality[quality["metric_name"] == "valid_email_rate_pct"].empty else "—")
c4.metric("Sources integrees", len(sources))

st.markdown(
    f'<div class="uc-alert"><strong>Contexte gouvernance :</strong> '
    f"UNICLOTHES vise un taux de doublons &lt; 2 % (rapport Bloc 1). "
    f"Le taux actuel ({dup_val:.1f} %) est en <strong>ALERT</strong> — "
    f"illustrant le besoin de golden record avant internationalisation ES/IT."
    f"</div>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Jauge — taux de doublons clients")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=dup_val,
        delta={"reference": dup_target, "relative": False, "valueformat": ".1f"},
        title={"text": "Doublons (%) — cible 2 %"},
        gauge={
            "axis": {"range": [0, 50]},
            "bar": {"color": "#FF2D2D"},
            "steps": [
                {"range": [0, 2], "color": "#d4edda"},
                {"range": [2, 10], "color": "#fff3cd"},
                {"range": [10, 50], "color": "#f8d7da"},
            ],
            "threshold": {"line": {"color": "green", "width": 4}, "value": 2},
        },
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Consentements marketing UNICLUB")
    consent["label"] = consent["consent_marketing"].map({True: "Consentement OK", False: "Sans consentement"})
    fig2 = px.pie(
        consent, names="label", values="nb_clients", hole=0.4,
        color_discrete_map={"Consentement OK": "#FF2D2D", "Sans consentement": "#CCCCCC"},
    )
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Volume par source avant deduplication")
fig3 = px.bar(
    sources, x="source_system", y="enregistrements",
    color="source_system",
    color_discrete_map={"crm": "#FF2D2D", "web": "#CC0000", "pos": "#990000"},
    labels={"source_system": "Source", "enregistrements": "Enregistrements"},
)
fig3.update_layout(showlegend=False, height=320)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Tableau de bord qualite")
display_q = quality.copy()
display_q.columns = ["Indicateur", "Valeur", "Cible", "Statut"]
st.dataframe(display_q, use_container_width=True, hide_index=True)

st.caption(
    "Les metriques alimentent le Comite Data mensuel (rapport Bloc 1, Partie 8)."
)
