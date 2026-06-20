"""Connexion PostgreSQL UNICLOTHES."""

import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://uniclothes:uniclothes_dev_2026@postgres:5432/uniclothes",
)


@st.cache_resource
def get_engine() -> Engine:
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})
