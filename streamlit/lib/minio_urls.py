"""Helpers for MinIO URLs."""

import os

from lib.images import public_image_url, resolve_object_key

MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000").rstrip("/")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "product-images")


def product_image_url(object_key: str | None, product_ref: str | None = None) -> str | None:
    key = resolve_object_key(product_ref, object_key) if product_ref else object_key
    return public_image_url(key)
