"""Fetch product images from MinIO (server-side, Docker-safe)."""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from functools import lru_cache

import requests

MINIO_ENDPOINT = os.getenv(
    "MINIO_ENDPOINT",
    os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000"),
).rstrip("/")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "product-images")

_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


@lru_cache(maxsize=1)
def list_bucket_objects() -> tuple[str, ...]:
    """List object keys in the product-images bucket (S3 ListObjectsV2)."""
    url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}?list-type=2"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return ()
        root = ET.fromstring(response.content)
        keys: list[str] = []
        for elem in root.iter():
            if elem.tag.endswith("Key") and elem.text:
                keys.append(elem.text.strip())
        return tuple(keys)
    except (requests.RequestException, ET.ParseError):
        return ()


def candidate_keys(product_ref: str, stored_key: str | None) -> list[str]:
    keys: list[str] = []
    if stored_key:
        keys.append(stored_key)
    for ext in _IMAGE_EXTENSIONS:
        keys.append(f"{product_ref}{ext}")
    keys.append(product_ref)
    available = list_bucket_objects()
    for obj in available:
        obj_lower = obj.lower()
        ref_lower = product_ref.lower()
        if obj_lower.startswith(ref_lower) and obj not in keys:
            keys.append(obj)
    return list(dict.fromkeys(keys))


def resolve_object_key(product_ref: str, stored_key: str | None) -> str | None:
    for key in candidate_keys(product_ref, stored_key):
        if fetch_image_bytes(key):
            return key
    return stored_key


def fetch_image_bytes(object_key: str | None) -> bytes | None:
    if not object_key:
        return None
    url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_key}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.content:
            return response.content
    except requests.RequestException:
        pass
    return None


def fetch_product_image(product_ref: str, stored_key: str | None) -> tuple[bytes | None, str | None]:
    for key in candidate_keys(product_ref, stored_key):
        data = fetch_image_bytes(key)
        if data:
            return data, key
    return None, stored_key


def public_image_url(object_key: str | None) -> str | None:
    public_base = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000").rstrip("/")
    if not object_key:
        return None
    return f"{public_base}/{MINIO_BUCKET}/{object_key}"
