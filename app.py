import json
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="Elite Medical")

st.title("Elite Medical Product Catalog")
st.write("Medical product supplier")

st.subheader("Test content")
st.write("If you see this, the app is working")


DATA_PATH = Path(__file__).parent / "data" / "products.json"
FALLBACK_PRODUCTS = [
    {
        "name": "TRANSPARENT FILM DRESSING",
        "category": "MEDICAL DRESSING PAD",
        "variants": [{"spec": "paper frame", "ref": "EL010101"}],
    },
    {
        "name": "WOUND CARE DRESSING",
        "category": "MEDICAL DRESSING PAD",
        "variants": [{"spec": "non-woven + absorbent pad", "ref": "EL010201"}],
    },
]


def load_products():
    try:
        with DATA_PATH.open("r", encoding="utf-8") as products_file:
            products = json.load(products_file)
    except Exception:
        st.warning("No products loaded")
        return FALLBACK_PRODUCTS

    if not isinstance(products, list) or not products:
        st.warning("No products loaded")
        return FALLBACK_PRODUCTS

    return [product for product in products if isinstance(product, dict)]


products = load_products()

st.subheader("Products")

if not products:
    st.write("No products loaded")
else:
    for product in products:
        name = product.get("name", "Unnamed product")
        category = product.get("category", "Uncategorized")
        variants = product.get("variants", [])

        st.write(f"**{name}**")
        st.write(f"Category: {category}")

        if isinstance(variants, list) and variants:
            for variant in variants:
                if isinstance(variant, dict):
                    spec = variant.get("spec", "needs_review")
                    ref = variant.get("ref", "needs_review")
                    st.write(f"- {spec} | {ref}")
        else:
            st.write("- variants need review")
