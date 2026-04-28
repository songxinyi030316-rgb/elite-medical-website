import json
from pathlib import Path

import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "products.json"

FALLBACK_PRODUCTS = [
    {
        "id": "EL010101",
        "name": "Transparent Film Dressing",
        "category": "Medical Dressing Pad",
        "variants": [{"spec": "paper frame", "ref": "EL010101"}],
    },
    {
        "id": "EL010201",
        "name": "Wound Care Dressing",
        "category": "Medical Dressing Pad",
        "variants": [{"spec": "non-woven + absorbent pad", "ref": "EL010201"}],
    },
    {
        "id": "EL-030101",
        "name": "High Elastic Bandage",
        "category": "Bandage",
        "variants": [{"spec": "5 cm", "ref": "EL-030101"}],
    },
]


def load_products():
    try:
        products = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return FALLBACK_PRODUCTS

    if not isinstance(products, list) or not products:
        return FALLBACK_PRODUCTS

    clean_products = []
    for product in products:
        if not isinstance(product, dict):
            continue
        variants = product.get("variants", [])
        if not isinstance(variants, list):
            variants = []
        clean_products.append(
            {
                "id": str(product.get("id", "needs_review")),
                "name": str(product.get("name", "Unnamed product")).title(),
                "category": str(product.get("category", "Uncategorized")).title(),
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

    return clean_products or FALLBACK_PRODUCTS


def matches_search(product, query):
    text = " ".join(
        [
            product["name"],
            product["category"],
            product["id"],
            " ".join(variant["spec"] for variant in product["variants"]),
            " ".join(variant["ref"] for variant in product["variants"]),
        ]
    ).lower()
    return query.lower().strip() in text


st.set_page_config(page_title="Elite Medical Product Catalog", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #ffffff; }
    .hero {
        padding: 2rem;
        border-radius: 12px;
        background: #eef7ff;
        border: 1px solid #d5e9fb;
        margin-bottom: 1.5rem;
    }
    .hero h1 { color: #0b4f8a; margin-bottom: .4rem; }
    .cta {
        display: inline-block;
        margin-top: .75rem;
        padding: .65rem 1rem;
        border-radius: 8px;
        background: #0b6fb3;
        color: white;
        font-weight: 700;
    }
    .product-card {
        padding: 1.1rem;
        border: 1px solid #dbe8f3;
        border-radius: 10px;
        margin-bottom: 1rem;
        background: #fbfdff;
    }
    .product-card h3 { color: #0b4f8a; margin-bottom: .35rem; }
    .metric-text { color: #466175; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Elite Medical Product Catalog</h1>
      <p>Disposable medical products, medical consumables, laboratory consumables, and healthcare supplies.</p>
      <span class="cta">Request a Quote</span>
    </div>
    """,
    unsafe_allow_html=True,
)

products = load_products()
categories = sorted({product["category"] for product in products})

st.sidebar.header("Catalog Filters")
selected_category = st.sidebar.selectbox("Category", ["All Categories", *categories])
search_query = st.sidebar.text_input("Search by product name or REF code")

filtered_products = [
    product
    for product in products
    if (selected_category == "All Categories" or product["category"] == selected_category)
    and matches_search(product, search_query)
]

st.subheader("Product Catalog")
st.caption(f"Showing {len(filtered_products)} of {len(products)} products")

if not filtered_products:
    st.info("No matching products found. Try another category or search term.")

for product in filtered_products:
    st.markdown(
        f"""
        <div class="product-card">
          <h3>{product["name"]}</h3>
          <p class="metric-text"><strong>Category:</strong> {product["category"]}</p>
          <p class="metric-text"><strong>Variants:</strong> {len(product["variants"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("View specs and REF codes"):
        if product["variants"]:
            st.table(product["variants"])
        else:
            st.write("Variant details need review.")

st.markdown("---")
st.subheader("Product Inquiry")

with st.form("inquiry_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    company = st.text_input("Company")
    selected_product = st.selectbox(
        "Selected product", [product["name"] for product in products]
    )
    message = st.text_area("Message")
    submitted = st.form_submit_button("Submit Inquiry")

if submitted:
    st.success("Thank you. Your inquiry has been received.")

st.markdown("---")
st.subheader("Why Choose Elite Medical")

col1, col2 = st.columns(2)
with col1:
    st.write("**10+ years manufacturing experience**")
    st.write("**CE approved products**")
with col2:
    st.write("**ISO13485:2016 certified facilities**")
    st.write("**One-stop sourcing service**")
