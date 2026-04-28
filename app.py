import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "products.json"

BRAND_GREEN = "#118457"
BRAND_DARK = "#2b2f33"

FALLBACK_PRODUCTS = [
    {
        "id": "EL010101",
        "name": "Transparent Film Dressing",
        "category": "Medical Dressing Pad",
        "image": "",
        "variants": [{"spec": "paper frame", "ref": "EL010101"}],
    },
    {
        "id": "EL010201",
        "name": "Wound Care Dressing",
        "category": "Medical Dressing Pad",
        "image": "",
        "variants": [{"spec": "non-woven + absorbent pad", "ref": "EL010201"}],
    },
    {
        "id": "EL-030101",
        "name": "High Elastic Bandage",
        "category": "Bandage",
        "image": "",
        "variants": [{"spec": "5 cm", "ref": "EL-030101"}],
    },
]


def image_path_for(product):
    image = str(product.get("image", "")).strip()
    if not image or image == "needs_review":
        return ""

    image_path = ROOT / image.lstrip("/")
    return str(image_path) if image_path.exists() else ""


def load_products():
    try:
        raw_products = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return FALLBACK_PRODUCTS

    if not isinstance(raw_products, list) or not raw_products:
        return FALLBACK_PRODUCTS

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
                "name": str(product.get("name", "Unnamed product")).title(),
                "category": str(product.get("category", "Uncategorized")).title(),
                "image": image_path_for(product),
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

    return products or FALLBACK_PRODUCTS


def matches_search(product, query):
    searchable = " ".join(
        [
            product["name"],
            product["category"],
            product["id"],
            " ".join(variant["spec"] for variant in product["variants"]),
            " ".join(variant["ref"] for variant in product["variants"]),
        ]
    ).lower()
    return query.lower().strip() in searchable


def render_product_card(product):
    if product.get("image"):
        st.image(product["image"], width=150)
    else:
        st.write("No image available")

    st.markdown(
        f"""
        <div class="product-card">
          <div class="product-name">{product["name"]}</div>
          <div class="product-meta">{product["category"]}</div>
          <div class="variant-count">{len(product["variants"])} variants</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("View Details"):
        if product["variants"]:
            st.table(product["variants"])
        else:
            st.write("Variant details need review.")


st.set_page_config(page_title="Elite Medical Product Catalog", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background: #ffffff;
        color: {BRAND_DARK};
    }}
    h1, h2, h3 {{
        color: {BRAND_DARK};
    }}
    section[data-testid="stSidebar"] {{
        background: #f3faf6;
        border-right: 1px solid #dcefe5;
    }}
    .text-logo {{
        color: {BRAND_GREEN};
        font-weight: 900;
        font-size: 1rem;
        letter-spacing: .04em;
        margin-bottom: .75rem;
    }}
    .hero {{
        background: linear-gradient(135deg, #eefaf4 0%, #ffffff 72%);
        border: 1px solid #dcefe5;
        border-radius: 14px;
        padding: 2.2rem;
        margin-bottom: 1.6rem;
    }}
    .hero-title {{
        color: {BRAND_DARK};
        font-size: 2.8rem;
        line-height: 1.05;
        font-weight: 900;
        margin: 0 0 .65rem;
    }}
    .hero-subtitle {{
        color: #53605a;
        max-width: 760px;
        font-size: 1.05rem;
        line-height: 1.55;
        margin-bottom: 1rem;
    }}
    .cta {{
        display: inline-block;
        background: {BRAND_GREEN};
        color: white;
        border-radius: 999px;
        padding: .72rem 1.15rem;
        font-weight: 800;
    }}
    .badge-row {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .8rem;
        margin: .4rem 0 1.8rem;
    }}
    .trust-badge, .category-card, .product-card, .quote-card, .footer-card {{
        border: 1px solid #dcefe5;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(17, 132, 87, .07);
    }}
    .trust-badge {{
        padding: .95rem 1rem;
        color: {BRAND_DARK};
        font-weight: 800;
        text-align: center;
    }}
    .section-heading {{
        margin: 1.4rem 0 .9rem;
    }}
    .section-heading span {{
        color: {BRAND_GREEN};
        font-weight: 900;
        text-transform: uppercase;
        font-size: .78rem;
    }}
    .section-heading h2 {{
        margin: .2rem 0 0;
        font-size: 1.65rem;
    }}
    .category-card {{
        padding: 1rem;
        min-height: 108px;
        background: #f8fdf9;
    }}
    .category-name {{
        color: {BRAND_DARK};
        font-weight: 850;
        min-height: 42px;
    }}
    .category-count {{
        color: {BRAND_GREEN};
        font-weight: 800;
        margin-top: .55rem;
    }}
    .product-card {{
        margin-top: .65rem;
        margin-bottom: .45rem;
        padding: 1rem;
        min-height: 145px;
        background: #fbfefd;
    }}
    .product-name {{
        color: {BRAND_DARK};
        font-size: 1.05rem;
        line-height: 1.25;
        font-weight: 850;
        min-height: 54px;
    }}
    .product-meta {{
        color: #66726d;
        font-size: .9rem;
        margin: .5rem 0;
    }}
    .variant-count {{
        color: {BRAND_GREEN};
        font-weight: 800;
    }}
    .quote-card {{
        padding: 1.25rem;
        background: #f6fcf8;
    }}
    .footer-card {{
        margin-top: 1.7rem;
        padding: 1.25rem;
        background: {BRAND_DARK};
        color: #ffffff;
    }}
    .footer-card a, .footer-card p {{
        color: #ffffff;
    }}
    div.stButton > button {{
        border: 1px solid #cde8d8;
        background: #ffffff;
        color: {BRAND_DARK};
        border-radius: 999px;
        font-weight: 750;
    }}
    div.stButton > button:hover {{
        border-color: {BRAND_GREEN};
        color: {BRAND_GREEN};
    }}
    @media (max-width: 900px) {{
        .badge-row {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
        .hero-title {{
            font-size: 2.1rem;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

products = load_products()
categories = sorted({product["category"] for product in products})
category_counts = {
    category: sum(1 for product in products if product["category"] == category)
    for category in categories
}

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All Categories"
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

st.markdown(
    """
    <div class="hero">
      <div class="text-logo">ELITE MEDICAL</div>
      <div class="hero-title">Product Brochure 2025 / Medical Product Catalog</div>
      <div class="hero-subtitle">
        Export-ready disposable medical products, medical consumables, laboratory consumables,
        and healthcare supplies for distributors, hospitals, and procurement teams.
      </div>
      <span class="cta">Request a Quote</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="badge-row">
      <div class="trust-badge">CE Approved</div>
      <div class="trust-badge">ISO13485:2016 Certified</div>
      <div class="trust-badge">10+ Years Experience</div>
      <div class="trust-badge">One-stop Medical Sourcing</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-heading">
      <span>Browse by category</span>
      <h2>Product Categories</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

category_tiles = ["All Categories", *categories]
tile_columns = st.columns(4)
for index, category in enumerate(category_tiles):
    count = len(products) if category == "All Categories" else category_counts[category]
    with tile_columns[index % 4]:
        st.markdown(
            f"""
            <div class="category-card">
              <div class="category-name">{category}</div>
              <div class="category-count">{count} products</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Filter", key=f"category_{index}_{category}"):
            st.session_state.selected_category = category

st.sidebar.header("Catalog Controls")
if st.sidebar.button("Reset filters"):
    st.session_state.selected_category = "All Categories"
    st.session_state.search_query = ""

selected_category = st.sidebar.selectbox(
    "Category filter",
    ["All Categories", *categories],
    key="selected_category",
)
search_query = st.sidebar.text_input(
    "Search by product name or REF code",
    key="search_query",
)

filtered_products = [
    product
    for product in products
    if (selected_category == "All Categories" or product["category"] == selected_category)
    and matches_search(product, search_query)
]

st.markdown(
    f"""
    <div class="section-heading">
      <span>Catalog</span>
      <h2>{len(filtered_products)} products shown</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

if not filtered_products:
    st.info("No matching products found. Use the sidebar to reset filters.")

for start in range(0, len(filtered_products), 3):
    columns = st.columns(3)
    for column, product in zip(columns, filtered_products[start : start + 3]):
        with column:
            render_product_card(product)

st.markdown("---")
st.markdown(
    """
    <div class="section-heading">
      <span>Request pricing</span>
      <h2>Product Inquiry</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="quote-card">', unsafe_allow_html=True)
with st.form("quote_request_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name")
        company = st.text_input("Company")
    with col2:
        email = st.text_input("Email")
        selected_product = st.selectbox(
            "Product",
            [product["name"] for product in products],
        )
    message = st.text_area("Message")
    submitted = st.form_submit_button("Submit Quote Request")

if submitted:
    st.success("Thank you. Your quote request has been received.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-heading">
      <span>Why choose us</span>
      <h2>Why Choose Elite Medical</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

why_columns = st.columns(4)
why_points = [
    ("10+ Years", "Manufacturing experience"),
    ("CE Approved", "Products for international markets"),
    ("ISO13485:2016", "Certified facilities"),
    ("One-stop", "Medical sourcing service"),
]
for column, (title, text) in zip(why_columns, why_points):
    with column:
        st.markdown(
            f"""
            <div class="trust-badge">
              <div>{title}</div>
              <small>{text}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="footer-card">
      <strong>Elite Medical (Nanjing) Co., Ltd.</strong><br>
      www.elitemedline.com<br>
      info@elitemedline.com<br>
      Professional B2B medical product supplier
    </div>
    """,
    unsafe_allow_html=True,
)
