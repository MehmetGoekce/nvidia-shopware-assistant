#!/usr/bin/env python3
"""
Sync Shopware 6 product data to CSV format for NVIDIA Blueprint catalog retriever.

Usage:
    python scripts/sync-shopware.py [--shopware-url URL] [--access-key KEY] [--output PATH]

Defaults to dockware dev instance at http://localhost:8888
"""

import argparse
import csv
import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

DEFAULT_SHOPWARE_URL = "http://localhost:8888"
DEFAULT_OUTPUT = "shared/data/products_shopware.csv"
DEFAULT_ACCESS_KEY = "SWSCWWRXRLLXNWHNB0F2NJNIUG"


def fetch_products(shopware_url: str, access_key: str) -> list[dict]:
    """Fetch all products from Shopware 6 Store API with media and categories."""
    url = f"{shopware_url}/store-api/product"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "sw-access-key": access_key,
    }
    payload = json.dumps({
        "limit": 100,
        "associations": {
            "cover": {"associations": {"media": {}}},
            "categories": {},
        },
    }).encode()

    req = Request(url, data=payload, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("elements", [])
    except URLError as e:
        print(f"Error connecting to Shopware at {shopware_url}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_product_row(product: dict, shopware_url: str) -> dict | None:
    """Extract a single product into Blueprint CSV format."""
    # Shopware 6 uses 'translated' for locale-specific fields
    translated = product.get("translated", {})
    name = translated.get("name") or product.get("name")
    if not name:
        return None

    # Description: strip HTML tags
    description = translated.get("description") or product.get("description", "") or ""
    description = re.sub(r"<[^>]+>", " ", description)
    description = re.sub(r"\s+", " ", description).strip()
    if not description or description.startswith("Lorem ipsum"):
        description = name

    # Price: use calculatedPrice (Storefront API) or fall back to price array
    calc_price = product.get("calculatedPrice", {})
    if calc_price:
        price = calc_price.get("totalPrice", 0.0)
    else:
        price_data = product.get("price", [])
        price = price_data[0].get("gross", 0.0) if price_data else 0.0

    # Image URL
    image_url = ""
    cover = product.get("cover")
    if cover and cover.get("media"):
        image_url = cover["media"].get("url", "")
    if image_url and not image_url.startswith("http"):
        image_url = f"{shopware_url}{image_url}"

    # Category — take first category name or "general"
    categories = product.get("categories") or []
    category = "general"
    for cat in categories:
        cat_name = cat.get("translated", {}).get("name") or cat.get("name", "")
        if cat_name:
            category = cat_name
            break

    return {
        "category": category,
        "subcategory": "",
        "name": name,
        "description": description,
        "url": "",
        "price": f"{price:.2f}",
        "image": image_url,
    }


def main():
    parser = argparse.ArgumentParser(description="Sync Shopware products to Blueprint CSV")
    parser.add_argument("--shopware-url", default=DEFAULT_SHOPWARE_URL)
    parser.add_argument("--access-key", default=DEFAULT_ACCESS_KEY)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    print(f"Fetching products from {args.shopware_url}...")
    products = fetch_products(args.shopware_url, args.access_key)
    print(f"Found {len(products)} products")

    # Deduplicate by name (Shopware returns variants as separate products)
    seen_names = set()
    rows = []
    for p in products:
        row = extract_product_row(p, args.shopware_url)
        if row and row["name"] not in seen_names:
            seen_names.add(row["name"])
            rows.append(row)

    if not rows:
        print("No products found! Check Shopware URL and access key.", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["category", "subcategory", "name", "description", "url", "price", "image"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} products to {args.output}")
    for row in rows:
        print(f"  - [{row['category']}] {row['name']} | EUR {row['price']}")


if __name__ == "__main__":
    main()
