import re
import json
import os
import hashlib


def extract_category_path(html: str):
    m = re.search(r'"breadcrumbs"\s*:\s*\[(.*?)\]', html, re.DOTALL)
    if not m:
        return None

    cats = re.findall(r'"name"\s*:\s*"([^"]+)"', m.group(1))
    return "/".join(cats).lower() if cats else None


def extract_pdp_with_regex(html: str) -> dict:
    def grab(pattern):
        m = re.search(pattern, html, re.DOTALL)
        return m.group(1).strip() if m else None

    category_path = extract_category_path(html)

    sizes = re.findall(
        r'"value"\s*:\s*"([^"]+)"[^}]*?"inStock"\s*:\s*(true|false)',
        html
    )

    seen = set()
    variants = []
    for v, s in sizes:
        key = (v, s)
        if key in seen:
            continue
        seen.add(key)
        variants.append({"value": v, "inStock": s == "true"})

    data = {
        "product_title": grab(r'"product"\s*:\s*\{"id"\s*:\s*\d+\s*,\s*"name"\s*:\s*"([^"]+)"'),
        "brand": grab(r'"brand"\s*:\s*\{"id"\s*:\s*\d+\s*,\s*"name"\s*:\s*"([^"]+)"'),
        "review": (lambda x: int(x) if x else None)(grab(r'"totalCount"\s*:\s*(\d+)')),
        "rating": (lambda x: float(x) if x else None)(grab(r'"averageRating"\s*:\s*([\d.]+)')),
        "category_path": category_path,
        "variants": {"size": variants},
        "msrp": (lambda x: float(x) if x else None)(grab(r'"sellingPrice"\s*:\s*\{\s*"value"\s*:\s*([\d.]+)')),
        "price": (lambda x: float(x) if x else None)(grab(r'"originalPrice"\s*:\s*\{\s*"value"\s*:\s*([\d.]+)')),
        "seller_name": grab(r'"merchantName"\s*:\s*"([^"]+)"'),
    }

    return data


def build_unique_key(item: dict) -> str:

    title = (item.get("product_title") or "").strip().lower()
    brand = (item.get("brand") or "").strip().lower()
    seller = (item.get("seller_name") or "").strip().lower()

    if title or brand or seller:
        return f"{brand}|{title}|{seller}"

    raw = json.dumps(item, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def main():
    all_items = []
    seen_products = set()

    for i in range(1, 50):
        filename = f"pdp_{i}.html"
        if not os.path.exists(filename):
            print(f"⚠️ Skipping (file not found): {filename}")
            continue

        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()

        data = extract_pdp_with_regex(html)

        if not any(data.values()):
            print(f"⚠️ Skipping (empty extraction): {filename}")
            continue

        key = build_unique_key(data)
        if key in seen_products:
            print(f"🔁 Duplicate product skipped: {filename} -> {key}")
            continue
        seen_products.add(key)

        all_items.append(data)

    out_file = "pdp_output.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(all_items)} unique products into: {out_file}")


if __name__ == "__main__":
    main()
