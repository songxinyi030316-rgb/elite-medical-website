import json
from pathlib import Path

import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "products.json"


st.set_page_config(page_title="Elite Medical Product Catalog", layout="wide")

st.title("Test page working")
st.title("Elite Medical Product Catalog")
st.write(
    "Elite Medical provides a B2B catalog of disposable medical products, "
    "medical consumables, laboratory consumables, and healthcare supplies for "
    "procurement teams and distributors."
)


def load_products():
    try:
        with DATA_PATH.open("r", encoding="utf-8") as products_file:
            products = json.load(products_file)
        if not isinstance(products, list):
            st.warning("No products loaded")
            return []
        return products
    except Exception as error:
        st.warning("No products loaded")
        st.caption(f"Data load error: {error}")
        return []


products = load_products()

categories = sorted(
    {
        product.get("category", "needs_review")
        for product in products
        if isinstance(product, dict)
    }
)

category_options = ["All categories", *categories] if categories else ["All categories"]
selected_category = st.sidebar.selectbox("Category filter", category_options)
search_query = st.sidebar.text_input("Search products")

filtered_products = []
for product in products:
    if not isinstance(product, dict):
        continue

    name = product.get("name", "needs_review")
    category = product.get("category", "needs_review")
    variants = product.get("variants", [])

    matches_category = (
        selected_category == "All categories" or category == selected_category
    )
    searchable_text = " ".join(
        [
            str(name),
            str(category),
            " ".join(str(variant.get("ref", "")) for variant in variants),
            " ".join(str(variant.get("spec", "")) for variant in variants),
        ]
    ).lower()
    matches_search = search_query.lower() in searchable_text

    if matches_category and matches_search:
        filtered_products.append(product)

st.subheader("Products")

if not products:
    st.info("No products loaded")
elif not filtered_products:
    st.info("No products loaded")
else:
    st.caption(f"Showing {len(filtered_products)} of {len(products)} products")

    for product in filtered_products:
        name = product.get("name", "needs_review")
        category = product.get("category", "needs_review")
        variants = product.get("variants", [])

        with st.expander(f"{name} — {category}", expanded=False):
            st.write(f"**Product name:** {name}")
            st.write(f"**Category:** {category}")

            if variants:
                st.write("**Variants:**")
                st.table(
                    [
                        {
                            "Spec": variant.get("spec", "needs_review"),
                            "Ref": variant.get("ref", "needs_review"),
                        }
                        for variant in variants
                    ]
                )
            else:
                st.write("Variants: needs_review")

st.subheader("Product Inquiry")

product_names = [
    product.get("name", "needs_review")
    for product in products
    if isinstance(product, dict)
]
product_options = product_names if product_names else ["No products loaded"]

with st.form("inquiry_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    company = st.text_input("Company")
    product = st.selectbox("Product", product_options)
    message = st.text_area("Message")
    submitted = st.form_submit_button("Send inquiry")

if submitted:
    st.success("Inquiry submitted")
    st.write(
        {
            "name": name,
            "email": email,
            "company": company,
            "product": product,
            "message": message,
        }
    )
