import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "products.json"

GREEN = "#118457"
DARK = "#25302b"
MUTED = "#65736d"
LIGHT_GREEN = "#eefaf3"

CORE_CATEGORIES = [
    "Medical Dressing",
    "Bandage",
    "Protective Products",
    "Respiratory",
    "Urology",
    "Injection",
    "Laboratory",
]

FALLBACK_PRODUCTS = [
    {
        "id": "EL010101",
        "name": "Transparent Film Dressing",
        "category": "Medical Dressing",
        "raw_category": "Medical Dressing Pad",
        "image": "",
        "variants": [{"spec": "paper frame", "ref": "EL010101"}],
    },
    {
        "id": "EL010201",
        "name": "Wound Care Dressing",
        "category": "Medical Dressing",
        "raw_category": "Medical Dressing Pad",
        "image": "",
        "variants": [{"spec": "non-woven + absorbent pad", "ref": "EL010201"}],
    },
    {
        "id": "EL-030101",
        "name": "High Elastic Bandage",
        "category": "Bandage",
        "raw_category": "Bandage",
        "image": "",
        "variants": [{"spec": "5 cm", "ref": "EL-030101"}],
    },
]


def broad_category(raw_category):
    category = str(raw_category).upper()
    if "BANDAGE" in category:
        return "Bandage"
    if "RESPIRATORY" in category or "ANAESTHESIA" in category:
        return "Respiratory"
    if "UROLOGY" in category:
        return "Urology"
    if "INJECTION" in category or "INTRAVENOUS" in category or "SURGICAL" in category:
        return "Injection"
    if "LABORATORY" in category:
        return "Laboratory"
    if "PROTECTIVE" in category or "DIAGNOSTIC" in category or "RECOVERY" in category:
        return "Protective Products"
    if "DRESSING" in category or "GAUZE" in category or "TAPE" in category:
        return "Medical Dressing"
    return "Protective Products"


def title_case(value):
    return str(value).replace("  ", " ").strip().title()


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

        raw_category = product.get("category", "Uncategorized")
        products.append(
            {
                "id": str(product.get("id", "needs_review")),
                "name": title_case(product.get("name", "Unnamed product")),
                "category": broad_category(raw_category),
                "raw_category": title_case(raw_category),
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
            product["raw_category"],
            product["id"],
            " ".join(variant["spec"] for variant in product["variants"]),
            " ".join(variant["ref"] for variant in product["variants"]),
        ]
    ).lower()
    return query.lower().strip() in searchable


def reset_filters():
    st.session_state.product_category = "All Categories"
    st.session_state.product_search = ""


def render_section_heading(kicker, title, body=""):
    st.markdown(
        f"""
        <div class="section-heading">
          <span>{kicker}</span>
          <h2>{title}</h2>
          {f"<p>{body}</p>" if body else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_product_card(product):
    with st.container():
        st.markdown('<div class="product-shell">', unsafe_allow_html=True)
        if product.get("image"):
            try:
                st.image(product["image"], width=150)
            except Exception:
                st.markdown('<span class="no-image">No image</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="no-image">No image</span>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="product-name">{product["name"]}</div>
            <div class="product-category">{product["category"]}</div>
            <div class="variant-pill">{len(product["variants"])} variants</div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("View Details"):
            if product["variants"]:
                st.table(product["variants"])
            else:
                st.write("Variant details need review.")
        st.markdown("</div>", unsafe_allow_html=True)


def category_counts(products):
    return {
        category: sum(1 for product in products if product["category"] == category)
        for category in CORE_CATEGORIES
    }


st.set_page_config(page_title="Elite Medical Product Catalog", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background: #ffffff;
        color: {DARK};
    }}
    .block-container {{
        max-width: 1220px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, p {{
        color: {DARK};
    }}
    div[data-testid="stTabs"] button {{
        color: {DARK};
        font-weight: 800;
    }}
    section[data-testid="stSidebar"] {{
        background: #f4fbf7;
        border-right: 1px solid #dcefe5;
    }}
    .site-hero {{
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(280px, .8fr);
        gap: 1.2rem;
        align-items: stretch;
        margin-bottom: 1rem;
    }}
    .hero-copy, .hero-visual, .section-card, .trust-card, .category-card, .product-shell, .quote-card, .contact-card {{
        border: 1px solid #dcefe5;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(17, 132, 87, .08);
    }}
    .hero-copy {{
        padding: 1.5rem;
        background: linear-gradient(135deg, #effaf4 0%, #ffffff 76%);
        border-left: 7px solid {GREEN};
    }}
    .text-logo {{
        color: {GREEN};
        font-size: 1.1rem;
        font-weight: 950;
        letter-spacing: .05em;
        margin-bottom: .45rem;
    }}
    .hero-title {{
        font-size: 2.7rem;
        line-height: 1.02;
        font-weight: 950;
        margin-bottom: .75rem;
    }}
    .hero-body {{
        color: {MUTED};
        font-size: 1.03rem;
        line-height: 1.5;
        max-width: 720px;
    }}
    .cta-row {{
        display: flex;
        gap: .7rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }}
    .primary-cta, .secondary-cta {{
        display: inline-block;
        border-radius: 999px;
        padding: .68rem 1rem;
        font-weight: 850;
    }}
    .primary-cta {{
        background: {GREEN};
        color: #ffffff;
    }}
    .secondary-cta {{
        border: 1px solid #b9dfc9;
        color: {GREEN};
        background: #ffffff;
    }}
    .hero-visual {{
        padding: 1rem;
        background:
            radial-gradient(circle at 15% 15%, #c7ecd6 0, transparent 26%),
            linear-gradient(145deg, #f5fcf7 0%, #ffffff 66%);
    }}
    .visual-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .65rem;
        margin-top: .5rem;
    }}
    .visual-note {{
        color: {MUTED};
        font-weight: 750;
        font-size: .9rem;
    }}
    .section-heading {{
        margin: 1rem 0 .65rem;
    }}
    .section-heading span {{
        color: {GREEN};
        font-weight: 950;
        text-transform: uppercase;
        font-size: .76rem;
        letter-spacing: .03em;
    }}
    .section-heading h2 {{
        margin: .16rem 0 .15rem;
        font-size: 1.55rem;
        line-height: 1.15;
    }}
    .section-heading p {{
        color: {MUTED};
        margin: 0;
    }}
    .section-card {{
        padding: 1.15rem;
        background: {LIGHT_GREEN};
    }}
    .stat-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: .75rem;
        margin: .85rem 0 1rem;
    }}
    .trust-card {{
        padding: .9rem;
        min-height: 96px;
        border-top: 4px solid {GREEN};
    }}
    .trust-card strong {{
        display: block;
        color: {DARK};
        font-size: .98rem;
        margin-bottom: .25rem;
    }}
    .trust-card span {{
        color: {MUTED};
        font-size: .86rem;
    }}
    .category-card {{
        padding: .9rem;
        min-height: 96px;
        background: #f8fdf9;
    }}
    .category-card strong {{
        display: block;
        min-height: 38px;
    }}
    .category-count {{
        color: {GREEN};
        font-weight: 850;
        margin-top: .35rem;
    }}
    .sidebar-category-list {{
        border-top: 1px solid #dcefe5;
        margin-top: .8rem;
        padding-top: .6rem;
    }}
    .sidebar-category-row {{
        display: flex;
        justify-content: space-between;
        gap: .6rem;
        padding: .22rem 0;
        color: {DARK};
        font-size: .9rem;
        border-bottom: 1px solid #edf6f1;
    }}
    .sidebar-category-row span:last-child {{
        color: {GREEN};
        font-weight: 850;
    }}
    .product-shell {{
        padding: .78rem;
        margin-bottom: .7rem;
        background: #ffffff;
    }}
    .product-shell img {{
        max-height: 118px;
        object-fit: contain;
    }}
    .no-image {{
        display: inline-block;
        background: #f2f8f4;
        color: {MUTED};
        border-radius: 999px;
        border: 1px dashed #bddfc9;
        font-size: .78rem;
        font-weight: 800;
        padding: .18rem .55rem;
        margin-bottom: .35rem;
    }}
    .product-name {{
        color: {DARK};
        font-weight: 900;
        line-height: 1.2;
        min-height: 42px;
        margin-top: .28rem;
    }}
    .product-category {{
        color: {MUTED};
        font-size: .88rem;
        margin: .35rem 0;
    }}
    .variant-pill {{
        display: inline-block;
        color: {GREEN};
        background: #eaf8f0;
        border-radius: 999px;
        padding: .22rem .55rem;
        font-size: .82rem;
        font-weight: 850;
    }}
    .quote-card, .contact-card {{
        padding: 1.15rem;
        background: #f8fdf9;
    }}
    .footer {{
        margin-top: 1.1rem;
        padding: 1rem 1.15rem;
        border-radius: 14px;
        background: {DARK};
        color: #ffffff;
    }}
    .footer strong, .footer span {{
        color: #ffffff;
    }}
    div.stButton > button {{
        border-radius: 999px;
        border: 1px solid #b9dfc9;
        color: {DARK};
        background: #ffffff;
        font-weight: 800;
        padding: .35rem .9rem;
    }}
    div.stButton > button:hover {{
        border-color: {GREEN};
        color: {GREEN};
    }}
    @media (max-width: 900px) {{
        .site-hero, .stat-grid {{
            grid-template-columns: 1fr;
        }}
        .hero-title {{
            font-size: 2rem;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

products = load_products()
counts = category_counts(products)
hero_images = [product["image"] for product in products if product.get("image")][:4]

if "product_category" not in st.session_state:
    st.session_state.product_category = "All Categories"
if "product_search" not in st.session_state:
    st.session_state.product_search = ""

st.sidebar.header("Product Navigation")
st.sidebar.selectbox(
    "Category filter",
    ["All Categories", *CORE_CATEGORIES],
    key="product_category",
)
st.sidebar.text_input(
    "Search by product name or REF code",
    key="product_search",
)
st.sidebar.button("Reset filter", on_click=reset_filters)
st.sidebar.markdown("**Categories**")
st.sidebar.markdown('<div class="sidebar-category-list">', unsafe_allow_html=True)
for category in CORE_CATEGORIES:
    st.sidebar.markdown(
        f"""
        <div class="sidebar-category-row">
          <span>{category}</span>
          <span>{counts.get(category, 0)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.sidebar.markdown("</div>", unsafe_allow_html=True)

home_tab, products_tab, contact_tab = st.tabs(["Home", "Products", "Contact"])

with home_tab:
    hero_left, hero_right = st.columns([1.35, .85])
    with hero_left:
        st.markdown(
            """
            <div class="hero-copy">
              <div class="text-logo">ELITE MEDICAL</div>
              <div class="hero-title">Medical Product Catalog 2025</div>
              <div class="hero-body">
                B2B medical consumables and healthcare supplies manufacturer based in
                Nanjing, China, serving distributors, hospitals, and procurement teams
                with export-ready product sourcing.
              </div>
              <div class="cta-row">
                <span class="primary-cta">View Products</span>
                <span class="secondary-cta">Request a Quote</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_right:
        st.markdown('<div class="hero-visual">', unsafe_allow_html=True)
        st.markdown('<div class="visual-note">Product families from the 2025 brochure</div>', unsafe_allow_html=True)
        image_cols = st.columns(2)
        for index, image in enumerate(hero_images):
            with image_cols[index % 2]:
                st.image(image, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    render_section_heading("Company Introduction", "Elite Medical (Nanjing) Co., Ltd.")
    st.markdown(
        """
        <div class="section-card">
          <strong>Based in Nanjing, Jiangsu, China</strong><br>
          More than 20 years of experience in medical product design, manufacturing,
          and export. Product coverage includes sports care, medical consumables,
          laboratory consumables/instruments, and medical dressings. Elite Medical
          supports distributors, hospitals, and procurement teams with CE approved
          products, ISO13485:2016 certified facilities, and one-stop sourcing service.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="stat-grid">
          <div class="trust-card"><strong>20+ Years Experience</strong><span>Medical product design, manufacturing, and export.</span></div>
          <div class="trust-card"><strong>CE Approved</strong><span>Products prepared for international B2B markets.</span></div>
          <div class="trust-card"><strong>ISO13485:2016 Certified</strong><span>Certified facilities and quality management.</span></div>
          <div class="trust-card"><strong>One-stop Medical Sourcing</strong><span>Catalog support for distributors and procurement teams.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with products_tab:
    render_section_heading(
        "Product Catalog",
        "Medical Product Catalog",
        "Search and filter products from the sidebar, then open product details for specs and REF codes.",
    )

    selected_category = st.session_state.product_category
    search_query = st.session_state.product_search

    filtered_products = [
        product
        for product in products
        if (
            selected_category == "All Categories"
            or product["category"] == selected_category
        )
        and matches_search(product, search_query)
    ]

    render_section_heading("Catalog", f"{len(filtered_products)} Products Shown")
    if not filtered_products:
        st.info("No matching products found. Try another category or search term.")

    for start in range(0, len(filtered_products), 3):
        columns = st.columns(3)
        for column, product in zip(columns, filtered_products[start : start + 3]):
            with column:
                render_product_card(product)

with contact_tab:
    render_section_heading(
        "Quote request",
        "Send Us Your Product Requirements",
        "Our team will respond with specifications and quotation support.",
    )

    form_col, info_col = st.columns([1.25, .75])
    with form_col:
        st.markdown('<div class="quote-card">', unsafe_allow_html=True)
        with st.form("inquiry_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                company = st.text_input("Company")
            with col2:
                email = st.text_input("Email")
                interested_product = st.selectbox(
                    "Interested product",
                    [product["name"] for product in products],
                )
            message = st.text_area("Message")
            submitted = st.form_submit_button("Submit Inquiry")
        if submitted:
            st.success("Thank you. Your inquiry has been received.")
        st.markdown("</div>", unsafe_allow_html=True)

    with info_col:
        st.markdown(
            """
            <div class="contact-card">
              <h3>Contact Information</h3>
              <strong>Elite Medical (Nanjing) Co., Ltd.</strong><br><br>
              <strong>Email:</strong> info@elitemedline.com<br>
              <strong>Website:</strong> www.elitemedline.com<br>
              <strong>Location:</strong> Nanjing, Jiangsu, China
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="section-card" style="margin-top:.8rem;">
              Send us your product requirements and our team will respond with
              specifications and quotation support.
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="footer">
      <strong>Elite Medical (Nanjing) Co., Ltd.</strong><br>
      <span>www.elitemedline.com | info@elitemedline.com | Professional B2B medical product supplier</span>
    </div>
    """,
    unsafe_allow_html=True,
)
