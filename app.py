import streamlit as st


st.set_page_config(page_title="Elite Medical Product Catalog")

st.title("Elite Medical Product Catalog")
st.write("App is running")

products = [
    {
        "name": "Transparent Film Dressing",
        "category": "Medical Dressing Pad",
        "ref": "EL010101",
        "spec": "paper frame",
    },
    {
        "name": "Wound Care Dressing",
        "category": "Medical Dressing Pad",
        "ref": "EL010201",
        "spec": "non-woven + absorbent pad",
    },
    {
        "name": "High Elastic Bandage",
        "category": "Bandage",
        "ref": "EL-030101",
        "spec": "5 cm",
    },
]

for product in products:
    st.subheader(product["name"])
    st.write(f"Category: {product['category']}")
    st.write(f"Ref: {product['ref']}")
    st.write(f"Spec: {product['spec']}")
    st.markdown("---")
