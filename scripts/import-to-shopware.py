#!/usr/bin/env python3
"""
Import NVIDIA Blueprint fashion products into Shopware 6 via Admin API.

Creates categories and products with descriptions and prices.
Images are referenced by URL from the shared/images directory.

Usage:
    python scripts/import-to-shopware.py [--shopware-url URL] [--limit N]
"""

import argparse
import csv
import json
import re
import sys
import uuid
from urllib.request import Request, urlopen
from urllib.error import URLError

DEFAULT_SHOPWARE_URL = "http://localhost:8888"
DEFAULT_CSV = "shared/data/products.csv"
ADMIN_USER = "admin"
ADMIN_PASS = "shopware"


def get_admin_token(shopware_url: str) -> str:
    """Get OAuth token from Shopware Admin API."""
    url = f"{shopware_url}/api/oauth/token"
    payload = json.dumps({
        "grant_type": "password",
        "client_id": "administration",
        "username": ADMIN_USER,
        "password": ADMIN_PASS,
    }).encode()
    req = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())["access_token"]


def api_request(shopware_url: str, token: str, method: str, endpoint: str, data: dict = None):
    """Make authenticated Admin API request."""
    url = f"{shopware_url}/api/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            if resp.status == 204:
                return {}
            return json.loads(resp.read())
    except URLError as e:
        if hasattr(e, 'read'):
            error_body = e.read().decode()
            print(f"  API Error {endpoint}: {error_body[:200]}", file=sys.stderr)
        raise


def get_or_create_category(shopware_url: str, token: str, name: str, parent_id: str) -> str:
    """Get existing category by name or create a new one."""
    # Search for existing category
    search_data = {
        "filter": [{"type": "equals", "field": "name", "value": name}],
        "limit": 1,
    }
    try:
        result = api_request(shopware_url, token, "POST", "search/category", search_data)
        if result.get("total", 0) > 0:
            cat_id = result["data"][0]["id"]
            print(f"  Category '{name}' exists: {cat_id[:8]}...")
            return cat_id
    except Exception:
        pass

    # Create new category
    cat_id = uuid.uuid4().hex
    cat_data = {
        "id": cat_id,
        "name": name,
        "parentId": parent_id,
        "active": True,
        "visible": True,
        "type": "page",
        "productAssignmentType": "product",
    }
    try:
        api_request(shopware_url, token, "POST", "category", cat_data)
        print(f"  Category '{name}' created: {cat_id[:8]}...")
    except Exception as e:
        print(f"  Category '{name}' error: {e}", file=sys.stderr)
    return cat_id


def get_root_category(shopware_url: str, token: str) -> str:
    """Get the root category ID."""
    result = api_request(shopware_url, token, "POST", "search/category", {
        "filter": [{"type": "equals", "field": "parentId", "value": None}],
        "limit": 1,
    })
    return result["data"][0]["id"]


def get_tax_id(shopware_url: str, token: str) -> str:
    """Get the first available tax ID."""
    result = api_request(shopware_url, token, "POST", "search/tax", {"limit": 1})
    return result["data"][0]["id"]


def get_sales_channel_id(shopware_url: str, token: str) -> str:
    """Get the Storefront sales channel ID."""
    result = api_request(shopware_url, token, "POST", "search/sales-channel", {
        "filter": [{"type": "equals", "field": "name", "value": "Storefront"}],
        "limit": 1,
    })
    return result["data"][0]["id"]


def read_products(csv_path: str, limit: int = 0) -> list[dict]:
    """Read products from NVIDIA CSV."""
    products = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                continue
            desc = row.get("description", "").strip()
            desc = re.sub(r"\s+", " ", desc)
            price = float(row.get("price", "0") or "0")
            if price == 0:
                price = 49.99
            products.append({
                "name": name,
                "description": desc,
                "price": price,
                "category": row.get("subcategory", row.get("category", "general")).strip(),
            })
            if limit and len(products) >= limit:
                break
    return products


def create_product(shopware_url: str, token: str, product: dict, category_id: str, tax_id: str, sales_channel_id: str) -> bool:
    """Create a single product in Shopware."""
    product_id = uuid.uuid4().hex
    product_number = f"NVIDIA-{uuid.uuid4().hex[:8].upper()}"

    product_data = {
        "id": product_id,
        "name": product["name"],
        "productNumber": product_number,
        "stock": 100,
        "taxId": tax_id,
        "price": [{
            "currencyId": "b7d2554b0ce847cd82f3ac9bd1c0dfca",
            "gross": product["price"],
            "net": round(product["price"] / 1.19, 2),
            "linked": True,
        }],
        "description": product["description"],
        "active": True,
        "categories": [{"id": category_id}],
        "visibilities": [{
            "salesChannelId": sales_channel_id,
            "visibility": 30,
        }],
    }

    try:
        api_request(shopware_url, token, "POST", "product", product_data)
        return True
    except Exception as e:
        print(f"  Error creating '{product['name']}': {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Import NVIDIA products into Shopware 6")
    parser.add_argument("--shopware-url", default=DEFAULT_SHOPWARE_URL)
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--limit", type=int, default=20, help="Max products to import (default: 20)")
    args = parser.parse_args()

    print(f"Connecting to {args.shopware_url}...")
    token = get_admin_token(args.shopware_url)
    print("Authenticated with Admin API")

    root_id = get_root_category(args.shopware_url, token)
    tax_id = get_tax_id(args.shopware_url, token)
    sc_id = get_sales_channel_id(args.shopware_url, token)
    print(f"Root category: {root_id[:8]}..., Tax: {tax_id[:8]}..., Sales Channel: {sc_id[:8]}...")

    products = read_products(args.csv, args.limit)
    print(f"Read {len(products)} products from {args.csv}")

    # Create categories
    category_map = {}
    for p in products:
        cat_name = p["category"]
        if cat_name not in category_map:
            category_map[cat_name] = get_or_create_category(args.shopware_url, token, cat_name.title(), root_id)

    # Create products
    created = 0
    for p in products:
        cat_id = category_map[p["category"]]
        print(f"  Creating: {p['name']} (EUR {p['price']})...")
        if create_product(args.shopware_url, token, p, cat_id, tax_id, sc_id):
            created += 1

    print(f"\nDone! Created {created}/{len(products)} products in Shopware.")
    print(f"View at: {args.shopware_url}")


if __name__ == "__main__":
    main()
