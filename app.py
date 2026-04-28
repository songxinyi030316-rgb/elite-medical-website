import json
from pathlib import Path

import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "products.json"

FALLBACK_PRODUCTS = [
    {
        "id": "EL010101",
        "category": "MEDICAL DRESSING PAD",
        "name": "TRANSPARENT FILM DRESSING",
        "variants": [
            {"spec": "paper frame", "ref": "EL010101"},
            {"spec": "paper frame type, with slot", "ref": "EL010102"},
        ],
    },
    {
        "id": "EL010201",
        "category": "MEDICAL DRESSING PAD",
        "name": "WOUND CARE DRESSING",
        "variants": [
            {"spec": "non-woven + absorbent pad", "ref": "EL010201"},
            {"spec": "PU + absorbent pad", "ref": "EL010202"},
        ],
    },
    {
        "id": "EL030101",
        "category": "BANDAGE",
        "name": "HIGH ELASTIC BANDAGE",
        "variants": [
            {"spec": "5", "ref": "EL-030101"},
            {"spec": "7.5", "ref": "EL-030102"},
        ],
    },
]


def normalize_products(raw_products):
    if not isinstance(raw_products, list):
        return []

    products = []
    for product in raw_products:
        if not isinstance(product, dict):
            continue

        variants = product.get("variants", [])
        if not isinstance(variants, list):
            variants = []

        products.append(
            {
                "id": str(product.get("id", "needs_review")),
                "category": str(product.get("category", "needs_review")),
                "name": str(product.get("name", "needs_review")),
                "variants": [
                    {
                        "spec": str(variant.get("spec", "needs_review")),
                        "ref": str(variant.get("ref", "needs_review")),
                    }
                    for variant in variants
                    if isinstance(variant, dict)
                ],
            }
        )

    return products


def load_products():
    try:
        with DATA_PATH.open("r", encoding="utf-8") as products_file:
            products = normalize_products(json.load(products_file))
    except Exception as error:
        st.warning("No products loaded")
        st.caption(f"Using fallback brochure sample content. Data error: {error}")
        return FALLBACK_PRODUCTS

    if not products:
        st.warning("No products loaded")
        st.caption("Using fallback brochure sample content.")
        return FALLBACK_PRODUCTS

    return products


def product_matches(product, selected_category, search_query):
    if selected_category != "All categories" and product["category"] != selected_category:
        return False

    searchable_text = " ".join(
        [
            product["name"],
            product["category"],
            product["id"],
            " ".join(variant["spec"] for variant in product["variants"]),
            " ".join(variant["ref"] for variant in product["variants"]),
        ]
    ).lower()

    return search_query.lower().strip() in searchable_text


st.set_page_config(page_title="Elite Medical Product Catalog", layout="wide")

st.title("Elite Medical Product Catalog")
st.write(
    "Elite Medical is a B2B medical product supplier offering disposable "
    "medical products, wound care items, bandages, protective products, "
    "respiratory supplies, urology products, injection products, and laboratory "
    "consumables for healthcare procurement teams and distributors."
)

products = load_products()
categories = sorted({product["category"] for product in products})

st.sidebar.header("Catalog Filters")
selected_category = st.sidebar.selectbox(
    "Category filter", ["All categories", *categories]
)
search_query = st.sidebar.text_input("Search products")

filtered_products = [
    product
    for product in products
    if product_matches(product, selected_category, search_query)
]

st.subheader("Products")
st.write(f"Loaded products: {len(products)}")

if not filtered_products:
    st.info("No products loaded")
else:
    st.caption(f"Showing {len(filtered_products)} product(s)")

    for product in filtered_products:
        with st.container():
            st.markdown(f"### {product['name']}")
            st.write(f"**Category:** {product['category']}")
            st.write(f"**Product ID:** {product['id']}")

            with st.expander("Product details", expanded=False):
                if product["variants"]:
                    st.table(
                        [
                            {"Spec": variant["spec"], "Ref": variant["ref"]}
                            for variant in product["variants"]
                        ]
                    )
                else:
                    st.write("Variants: needs_review")
            st.markdown("---")

st.subheader("Inquiry Form")

product_options = [product["name"] for product in products] or ["No products loaded"]

with st.form("inquiry_form"):
    inquiry_name = st.text_input("Name")
    inquiry_email = st.text_input("Email")
    inquiry_company = st.text_input("Company")
    inquiry_product = st.selectbox("Product", product_options)
    inquiry_message = st.text_area("Message")
    submitted = st.form_submit_button("Send inquiry")

if submitted:
    st.success("Inquiry received")
    st.write(
        {
            "name": inquiry_name,
            "email": inquiry_email,
            "company": inquiry_company,
            "product": inquiry_product,
            "message": inquiry_message,
        }
    )
