#!/usr/bin/env python3
"""Generate placeholder product images and upload to MinIO."""

import csv
import os
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED_ERP = ROOT / "seed" / "products_erp.csv"
OUT_DIR = ROOT / "seed" / "product_images"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_USER = os.getenv("MINIO_ROOT_USER", "uniclothes_minio")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "uniclothes_minio_2026")
MINIO_BUCKET = "product-images"
CONTAINER = os.getenv("MINIO_CONTAINER", "uniclothes-minio")


def _png_rgb(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Minimal PNG writer (no external deps)."""
    r, g, b = rgb
    row = bytes([0] + [r, g, b] * width)
    raw = row * height
    compressed = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


def load_product_refs() -> list[str]:
    refs = []
    with SEED_ERP.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            refs.append(row["product_ref"])
    return refs


def generate_images(refs: list[str]) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    colors = [(255, 45, 45), (204, 0, 0), (153, 0, 0), (255, 120, 120)]
    paths = []
    for i, ref in enumerate(refs):
        path = OUT_DIR / f"{ref}.jpg"
        # Save as .jpg filename but PNG bytes (browsers accept)
        path.write_bytes(_png_rgb(320, 320, colors[i % len(colors)]))
        paths.append(path)
        print(f"  generated {path.name}")
    return paths


def upload_via_mc() -> None:
    network = subprocess.check_output(
        ["docker", "inspect", CONTAINER, "-f", "{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}"],
        text=True,
    ).strip()
    if not network:
        raise RuntimeError(f"Cannot detect Docker network for {CONTAINER}")

    abs_out = OUT_DIR.resolve()
    cmd = [
        "docker", "run", "--rm",
        "--network", network,
        "-v", f"{abs_out}:/data:ro",
        "minio/mc:latest",
        "/bin/sh", "-c",
        (
            f"mc alias set local http://{CONTAINER}:9000 {MINIO_USER} {MINIO_PASSWORD} && "
            f"mc mb --ignore-existing local/{MINIO_BUCKET} && "
            f"mc anonymous set download local/{MINIO_BUCKET} && "
            f"mc cp /data/*.jpg local/{MINIO_BUCKET}/"
        ),
    ]
    print("Uploading to MinIO...")
    subprocess.run(cmd, check=True)
    print(f"Uploaded {len(list(OUT_DIR.glob('*.jpg')))} images to {MINIO_BUCKET}/")


def main() -> int:
    print("=== UNICLOTHES product images -> MinIO ===")
    if not SEED_ERP.exists():
        print(f"Missing {SEED_ERP}", file=sys.stderr)
        return 1
    refs = load_product_refs()
    print(f"Generating {len(refs)} placeholder images...")
    generate_images(refs)
    try:
        upload_via_mc()
    except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError) as exc:
        print(f"Upload failed: {exc}", file=sys.stderr)
        print("Images saved locally in scripts/seed/product_images/", file=sys.stderr)
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
