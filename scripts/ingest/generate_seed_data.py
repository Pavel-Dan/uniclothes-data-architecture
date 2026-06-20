#!/usr/bin/env python3
"""Generate fictitious UNICLOTHES seed data for the data architecture POC."""

import csv
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "seed"

FIRST_NAMES = [
    "Marie", "Lucas", "Emma", "Hugo", "Lea", "Louis", "Chloe", "Gabriel",
    "Camille", "Raphael", "Sarah", "Arthur", "Ines", "Jules", "Manon",
    "Paul", "Julie", "Nathan", "Clara", "Tom", "Anais", "Maxime", "Lola",
]
LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier",
]

STORES = [
    ("PAR01", "UNICLOTHES Paris Marais", "Paris", "Ile-de-France"),
    ("PAR02", "UNICLOTHES Paris Opera", "Paris", "Ile-de-France"),
    ("LYO01", "UNICLOTHES Lyon Confluence", "Lyon", "Auvergne-Rhone-Alpes"),
    ("MAR01", "UNICLOTHES Marseille Vieux-Port", "Marseille", "PACA"),
    ("BOR01", "UNICLOTHES Bordeaux", "Bordeaux", "Nouvelle-Aquitaine"),
    ("LIL01", "UNICLOTHES Lille", "Lille", "Hauts-de-France"),
    ("NAN01", "UNICLOTHES Nantes", "Nantes", "Pays de la Loire"),
    ("STR01", "UNICLOTHES Strasbourg", "Strasbourg", "Grand Est"),
    ("TLS01", "UNICLOTHES Toulouse", "Toulouse", "Occitanie"),
    ("NCE01", "UNICLOTHES Nice", "Nice", "PACA"),
]

CATEGORIES = ["T-shirts", "Pantalons", "Robes", "Vestes", "Accessoires", "Chaussures"]

PRODUCTS = [
    ("UC-TS-001", "T-shirt coton bio blanc", "T-shirts", 29.90),
    ("UC-TS-002", "T-shirt oversize noir", "T-shirts", 34.90),
    ("UC-PA-001", "Jean slim indigo", "Pantalons", 79.90),
    ("UC-PA-002", "Pantalon chino beige", "Pantalons", 59.90),
    ("UC-RO-001", "Robe midi lin", "Robes", 89.90),
    ("UC-RO-002", "Robe portefeuille", "Robes", 69.90),
    ("UC-VE-001", "Veste denim", "Vestes", 99.90),
    ("UC-VE-002", "Blouson leger", "Vestes", 119.90),
    ("UC-AC-001", "Echarpe laine", "Accessoires", 39.90),
    ("UC-AC-002", "Ceinture cuir", "Accessoires", 49.90),
    ("UC-CH-001", "Basket minimaliste", "Chaussures", 89.90),
    ("UC-CH-002", "Mocassin cuir", "Chaussures", 109.90),
    ("UC-TS-003", "Debardeur coton", "T-shirts", 24.90),
    ("UC-PA-003", "Short lin", "Pantalons", 44.90),
    ("UC-RO-003", "Combinaison ete", "Robes", 79.90),
    ("UC-VE-003", "Parka impermeable", "Vestes", 149.90),
    ("UC-AC-003", "Bonnet merinos", "Accessoires", 29.90),
    ("UC-AC-004", "Sac tote coton", "Accessoires", 34.90),
    ("UC-TS-004", "Polo pique", "T-shirts", 39.90),
    ("UC-PA-004", "Jogging confort", "Pantalons", 54.90),
]


def make_email(first: str, last: str, idx: int) -> str:
    base = f"{first.lower()}.{last.lower()}{idx}"
    return f"{base}@email.com"


def write_csv(path: Path, headers: list, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  wrote {path.name}: {len(rows)} rows")


def generate_customers(n_base: int = 480) -> dict:
    """Generate customers with intentional cross-channel duplicates (~5%)."""
    customers = []
    duplicate_pool = []

    for i in range(n_base):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = make_email(fn, ln, i)
        phone = f"+336{random.randint(10000000, 99999999)}"
        consent = random.random() > 0.25
        consent_date = date.today() - timedelta(days=random.randint(30, 800))
        last_activity = date.today() - timedelta(days=random.randint(0, 500))
        customers.append({
            "email": email,
            "first_name": fn,
            "last_name": ln,
            "phone": phone,
            "consent_marketing": consent,
            "consent_date": consent_date,
            "last_activity": last_activity,
        })
        if random.random() < 0.08:
            duplicate_pool.append(customers[-1].copy())

    crm_rows, web_rows, pos_rows = [], [], []

    for i, c in enumerate(customers):
        cid = f"CRM-{i+1:05d}"
        crm_rows.append([
            cid, c["email"], c["first_name"], c["last_name"], c["phone"],
            c["consent_marketing"], c["consent_date"], c["last_activity"],
        ])
        if random.random() > 0.3:
            wid = f"WEB-{i+1:05d}"
            web_rows.append([
                wid, c["email"], c["first_name"], c["last_name"], c["phone"],
                c["consent_marketing"], c["consent_date"], c["last_activity"],
            ])

    for j, dup in enumerate(duplicate_pool):
        store = random.choice(STORES)[0]
        pid = f"POS-DUP-{j+1:04d}"
        pos_rows.append([
            pid, dup["email"],
            dup["first_name"], dup["last_name"] + "-POS",
            dup["phone"], dup["consent_marketing"],
            dup["consent_date"], dup["last_activity"], store,
        ])

    for i in range(80):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = make_email(fn, ln, 9000 + i)
        store = random.choice(STORES)[0]
        pos_rows.append([
            f"POS-{i+1:05d}", email, fn, ln,
            f"+336{random.randint(10000000, 99999999)}",
            random.random() > 0.4,
            date.today() - timedelta(days=random.randint(60, 400)),
            date.today() - timedelta(days=random.randint(0, 200)),
            store,
        ])

    write_csv(OUTPUT_DIR / "customers_crm.csv",
              ["source_id", "email", "first_name", "last_name", "phone",
               "consent_marketing", "consent_date", "last_activity"], crm_rows)
    write_csv(OUTPUT_DIR / "customers_web.csv",
              ["source_id", "email", "first_name", "last_name", "phone",
               "consent_marketing", "consent_date", "last_activity"], web_rows)
    write_csv(OUTPUT_DIR / "customers_pos.csv",
              ["source_id", "email", "first_name", "last_name", "phone",
               "consent_marketing", "consent_date", "last_activity", "store_code"], pos_rows)

    return {c["email"]: c for c in customers}


def generate_products() -> None:
    erp_rows = []
    web_rows = []
    for ref, name, cat, price in PRODUCTS:
        stock = random.randint(10, 500)
        erp_rows.append([ref, name, cat, f"{price:.2f}", stock])
        web_rows.append([f"WEB-{ref}", ref, name, cat, f"{price:.2f}"])
        if random.random() < 0.15:
            bad_ref = ref.replace("UC-", "WEB-")
            web_rows.append([f"WEB-{bad_ref}", bad_ref, name + " (web)", cat, f"{price + 5:.2f}"])

    write_csv(OUTPUT_DIR / "products_erp.csv",
              ["product_ref", "product_name", "category", "price_eur", "stock_qty"], erp_rows)
    write_csv(OUTPUT_DIR / "products_web.csv",
              ["web_sku", "product_ref", "product_name", "category", "price_eur"], web_rows)


def generate_stores() -> None:
    rows = [[s[0], s[1], s[2], s[3], "2024-06-01"] for s in STORES]
    rows[0][4] = "2024-01-15"
    write_csv(OUTPUT_DIR / "stores.csv",
              ["store_code", "store_name", "city", "region", "opened_date"], rows)


def generate_orders(emails: list, n_orders: int = 2200) -> None:
    web_rows, pos_rows = [], []
    product_refs = [p[0] for p in PRODUCTS]

    for i in range(n_orders):
        email = random.choice(emails)
        product_ref = random.choice(product_refs)
        price = next(p[3] for p in PRODUCTS if p[0] == product_ref)
        qty = random.randint(1, 3)
        order_date = datetime.now() - timedelta(
            days=random.randint(0, 365),
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59),
        )
        amount = round(price * qty, 2)

        if random.random() > 0.35:
            channel = random.choice(["web", "app"])
            web_rows.append([
                f"WEB-ORD-{i+1:06d}", email, channel,
                order_date.strftime("%Y-%m-%d %H:%M:%S"),
                product_ref, qty, f"{price:.2f}", f"{amount:.2f}",
            ])
        else:
            store = random.choice(STORES)[0]
            pos_rows.append([
                f"POS-ORD-{i+1:06d}", email, store,
                order_date.strftime("%Y-%m-%d %H:%M:%S"),
                product_ref, qty, f"{price:.2f}", f"{amount:.2f}",
            ])

    write_csv(OUTPUT_DIR / "orders_web.csv",
              ["order_id", "customer_email", "channel", "order_date",
               "product_ref", "quantity", "unit_price_eur", "amount_eur"], web_rows)
    write_csv(OUTPUT_DIR / "orders_pos.csv",
              ["order_id", "customer_email", "store_code", "order_date",
               "product_ref", "quantity", "unit_price_eur", "amount_eur"], pos_rows)


def main() -> None:
    print("Generating UNICLOTHES seed data...")
    customer_map = generate_customers()
    generate_products()
    generate_stores()
    generate_orders(list(customer_map.keys()))
    print("Done.")


if __name__ == "__main__":
    main()
