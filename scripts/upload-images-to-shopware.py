#!/usr/bin/env python3
"""
Upload product images from shared/images/ to Shopware 6 and assign as cover images.

Matches products by name to image filenames.
"""

import json
import os
import sys
import uuid
import base64
import re
from urllib.request import Request, urlopen
from urllib.error import URLError

SHOPWARE_URL = "http://localhost:8888"
IMAGES_DIR = "shared/images"
ADMIN_USER = "admin"
ADMIN_PASS = "shopware"


def get_admin_token() -> str:
    url = f"{SHOPWARE_URL}/api/oauth/token"
    payload = json.dumps({
        "grant_type": "password",
        "client_id": "administration",
        "username": ADMIN_USER,
        "password": ADMIN_PASS,
    }).encode()
    req = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())["access_token"]


def api_request(token: str, method: str, endpoint: str, data=None, headers_extra=None, raw_body=None):
    url = f"{SHOPWARE_URL}/api/{endpoint}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if headers_extra:
        headers.update(headers_extra)
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    elif raw_body is not None:
        body = raw_body
    else:
        body = None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=60) as resp:
            if resp.status == 204:
                return {}
            return json.loads(resp.read())
    except URLError as e:
        if hasattr(e, 'read'):
            err = e.read().decode()[:300]
            print(f"    API Error: {err}", file=sys.stderr)
        raise


def get_all_products(token: str) -> list[dict]:
    """Get all products with pagination."""
    all_products = []
    page = 1
    while True:
        result = api_request(token, "POST", "search/product", {
            "limit": 100,
            "page": page,
            "filter": [{"type": "prefix", "field": "productNumber", "value": "NVIDIA-"}],
            "associations": {"cover": {"associations": {"media": {}}}},
        })
        data = result.get("data", [])
        all_products.extend(data)
        if len(data) < 100:
            break
        page += 1
    return all_products


def name_to_filename(name: str) -> str:
    """Convert product name to probable image filename."""
    # Replace spaces with underscores, remove special chars
    clean = name.replace(" ", "_").replace("-", "_").replace(",", "")
    clean = re.sub(r"[^a-zA-Z0-9_]", "", clean)
    return clean


def find_image(name: str) -> str | None:
    """Find matching image file for a product name."""
    target = name_to_filename(name).lower()
    for f in os.listdir(IMAGES_DIR):
        fname = os.path.splitext(f)[0].lower().replace("-", "_")
        # Try exact match first
        if fname == target or fname == target + "_small":
            return os.path.join(IMAGES_DIR, f)
    # Fuzzy: check if all significant words from product name are in filename
    words = [w.lower() for w in name.split() if len(w) > 2]
    for f in os.listdir(IMAGES_DIR):
        fname_lower = f.lower().replace("-", "_").replace(".", "_")
        matches = sum(1 for w in words if w.lower().replace("-", "_") in fname_lower)
        if matches >= len(words) * 0.6 and matches >= 2:
            return os.path.join(IMAGES_DIR, f)
    return None


def upload_image_and_assign(token: str, product_id: str, product_name: str, image_path: str) -> bool:
    """Upload image to Shopware media and assign to product as cover."""
    media_id = uuid.uuid4().hex
    ext = os.path.splitext(image_path)[1].lstrip(".")
    if ext == "jpeg":
        ext = "jpg"
    content_type = f"image/{ext}"

    # 1. Create media entity
    try:
        api_request(token, "POST", "media", {"id": media_id})
    except Exception as e:
        print(f"    Failed to create media entity: {e}", file=sys.stderr)
        return False

    # 2. Upload image binary
    with open(image_path, "rb") as f:
        image_data = f.read()

    file_name = os.path.splitext(os.path.basename(image_path))[0]
    try:
        api_request(
            token, "POST",
            f"_action/media/{media_id}/upload?extension={ext}&fileName={file_name}",
            raw_body=image_data,
            headers_extra={"Content-Type": content_type},
        )
    except Exception as e:
        print(f"    Failed to upload image: {e}", file=sys.stderr)
        return False

    # 3. Create product-media association and set as cover
    pm_id = uuid.uuid4().hex
    try:
        api_request(token, "PATCH", f"product/{product_id}", {
            "coverId": pm_id,
            "media": [{
                "id": pm_id,
                "mediaId": media_id,
                "position": 0,
            }],
        })
    except Exception as e:
        print(f"    Failed to assign to product: {e}", file=sys.stderr)
        return False

    return True


def main():
    print("Authenticating...")
    token = get_admin_token()

    print("Fetching products...")
    products = get_all_products(token)
    print(f"Found {len(products)} products")

    uploaded = 0
    skipped = 0
    no_image = 0

    for p in products:
        name = p.get("translated", {}).get("name") or p.get("name") or ""
        pid = p["id"]
        has_cover = p.get("cover") is not None

        if not name or has_cover:
            skipped += 1
            continue

        image_path = find_image(name)
        if not image_path:
            print(f"  SKIP (no image found): {name}")
            no_image += 1
            continue

        print(f"  Uploading: {name} <- {os.path.basename(image_path)}")
        if upload_image_and_assign(token, pid, name, image_path):
            uploaded += 1
        else:
            print(f"    FAILED: {name}")

    print(f"\nDone! Uploaded: {uploaded}, Skipped (has image): {skipped}, No image found: {no_image}")


if __name__ == "__main__":
    main()
