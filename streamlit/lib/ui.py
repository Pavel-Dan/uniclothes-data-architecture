"""UI partagée — branding UNICLOTHES."""

from pathlib import Path

import streamlit as st

RED = "#FF2D2D"
RED_DARK = "#CC0000"
RED_LIGHT = "#FFF0F0"
ASSETS = Path(__file__).resolve().parent.parent / "assets"


def inject_brand_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'DM Sans', sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {RED} 0%, {RED_DARK} 100%);
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        [data-testid="stSidebar"] .stMarkdown a {{
            color: white !important;
        }}

        div[data-testid="stMetric"] {{
            background: {RED_LIGHT};
            border-left: 4px solid {RED};
            border-radius: 8px;
            padding: 12px 16px;
        }}
        div[data-testid="stMetric"] label {{
            color: #555 !important;
        }}
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {RED_DARK} !important;
            font-weight: 700;
        }}

        .uc-hero {{
            background: linear-gradient(135deg, {RED} 0%, {RED_DARK} 100%);
            color: white;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
        }}
        .uc-hero h1 {{
            color: white !important;
            margin: 0;
            font-size: 2rem;
        }}
        .uc-hero p {{
            color: rgba(255,255,255,0.9);
            margin: 0.5rem 0 0 0;
        }}

        .uc-badge {{
            display: inline-block;
            background: {RED};
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .uc-alert {{
            background: #FFF3CD;
            border-left: 4px solid #FFC107;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_header() -> None:
    logo_path = ASSETS / "uniclothes_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=110)
    st.markdown("---")
    st.caption("Plateforme data Phase 1")
    st.caption("Consolidation omnicanale")


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="uc-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    colors = {"OK": "#28a745", "ALERT": "#dc3545", "INFO": "#6c757d"}
    color = colors.get(status, "#6c757d")
    return f'<span class="uc-badge" style="background:{color}">{status}</span>'
