import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "products.json"
HERO_IMAGE = "/public/hero/cover.png"
HERO_IMAGE_PATH = ROOT / HERO_IMAGE.lstrip("/")

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


def navigate_to(page):
    st.session_state.current_page = page


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
        padding-top: 1rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, p {{
        color: {DARK};
    }}
    div[role="radiogroup"] {{
        gap: .45rem;
        margin-bottom: .9rem;
    }}
    div[role="radiogroup"] label {{
        border: 1px solid #dcefe5;
        border-radius: 999px;
        background: #ffffff;
        padding: .25rem .8rem;
        box-shadow: 0 6px 16px rgba(17, 132, 87, .06);
    }}
    div[role="radiogroup"] label[data-checked="true"] {{
        background: {GREEN};
        border-color: {GREEN};
        color: #ffffff;
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
        padding: 1.35rem;
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
        font-size: 2.45rem;
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
    .hero-visual {{
        padding: .8rem;
        background:
            radial-gradient(circle at 15% 15%, #c7ecd6 0, transparent 26%),
            linear-gradient(145deg, #f5fcf7 0%, #ffffff 66%);
    }}
    .hero-visual img {{
        border-radius: 12px;
        box-shadow: 0 16px 34px rgba(17, 132, 87, .18);
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
    .company-gradient {{
        border-radius: 18px;
        padding: 1.1rem;
        margin: .7rem 0 .95rem;
        background:
            linear-gradient(135deg, rgba(17,132,87,.97), rgba(35,165,101,.88)),
            radial-gradient(circle at 82% 18%, rgba(255,255,255,.24), transparent 34%);
        box-shadow: 0 16px 38px rgba(17, 132, 87, .18);
    }}
    .company-grid {{
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(280px, .65fr);
        gap: .9rem;
        align-items: stretch;
    }}
    .company-copy, .company-panel {{
        border-radius: 14px;
        padding: 1rem;
        background: rgba(255,255,255,.13);
        border: 1px solid rgba(255,255,255,.25);
    }}
    .company-copy h2, .company-copy p, .company-copy strong,
    .company-panel strong, .company-panel span {{
        color: #ffffff;
    }}
    .company-copy h2 {{
        margin: 0 0 .45rem;
        font-size: 1.55rem;
        line-height: 1.16;
    }}
    .company-copy p {{
        margin: 0;
        line-height: 1.55;
    }}
    .company-panel {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .6rem;
    }}
    .mini-badge {{
        border-radius: 12px;
        background: rgba(255,255,255,.18);
        padding: .7rem;
        min-height: 88px;
    }}
    .mini-badge strong {{
        display: block;
        font-size: .95rem;
        line-height: 1.16;
        margin-bottom: .25rem;
    }}
    .mini-badge span {{
        font-size: .78rem;
        line-height: 1.25;
    }}
    .intro-strip {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .75rem;
        margin-bottom: .95rem;
    }}
    .intro-item {{
        border-radius: 14px;
        border: 1px solid #dcefe5;
        background: #ffffff;
        padding: .85rem;
        box-shadow: 0 10px 24px rgba(17, 132, 87, .07);
    }}
    .intro-item strong {{
        display: block;
        color: {DARK};
        margin-bottom: .25rem;
    }}
    .intro-item span {{
        color: {MUTED};
        font-size: .88rem;
        line-height: 1.35;
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
    .contact-hero {{
        border-radius: 18px;
        padding: 1.1rem;
        margin-bottom: .85rem;
        background: linear-gradient(135deg, #eefaf3 0%, #ffffff 74%);
        border: 1px solid #dcefe5;
        border-left: 7px solid {GREEN};
    }}
    .contact-hero h2 {{
        margin: 0 0 .25rem;
    }}
    .contact-hero p {{
        color: {MUTED};
        margin: 0;
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
    div.stButton > button[kind="primary"] {{
        background: {GREEN};
        border-color: {GREEN};
        color: #ffffff;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background: #0c6f49;
        border-color: #0c6f49;
        color: #ffffff;
    }}
    @media (max-width: 900px) {{
        .site-hero, .stat-grid, .company-grid, .intro-strip {{
            grid-template-columns: 1fr;
        }}
        .hero-title {{
            font-size: 2rem;
        }}
        .company-panel {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

products = load_products()
counts = category_counts(products)

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "product_category" not in st.session_state:
    st.session_state.product_category = "All Categories"
if "product_search" not in st.session_state:
    st.session_state.product_search = ""

st.radio(
    "Navigation",
    ["Home", "Products", "Contact"],
    key="current_page",
    horizontal=True,
    label_visibility="collapsed",
)

if st.session_state.current_page == "Products":
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
else:
    st.sidebar.markdown("### ELITE MEDICAL")
    st.sidebar.write("Professional B2B medical product supplier in China.")
    st.sidebar.markdown(
        """
        <div class="sidebar-category-list">
          <div class="sidebar-category-row"><span>CE Approved</span><span>Yes</span></div>
          <div class="sidebar-category-row"><span>ISO13485:2016</span><span>Certified</span></div>
          <div class="sidebar-category-row"><span>Catalog Products</span><span>{}</span></div>
        </div>
        """.format(len(products)),
        unsafe_allow_html=True,
    )

if st.session_state.current_page == "Home":
    hero_left, hero_right = st.columns([1.08, .92])
    with hero_left:
        st.markdown(
            """
            <div class="hero-copy">
              <div class="text-logo">ELITE MEDICAL</div>
              <div class="hero-title">Medical Product Catalog 2025</div>
              <div class="hero-body">
                B2B medical consumables, disposable medical products, laboratory
                consumables, and healthcare supplies from a reliable medical product
                partner in China.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        button_col_1, button_col_2, _ = st.columns([.9, .95, 1.25])
        with button_col_1:
            st.button(
                "View Products",
                type="primary",
                use_container_width=True,
                on_click=navigate_to,
                args=("Products",),
            )
        with button_col_2:
            st.button(
                "Request a Quote",
                use_container_width=True,
                on_click=navigate_to,
                args=("Contact",),
            )
    with hero_right:
        st.markdown('<div class="hero-visual">', unsafe_allow_html=True)
        st.markdown('<div class="visual-note">Brochure cover and product identity</div>', unsafe_allow_html=True)
        if HERO_IMAGE_PATH.exists():
            st.image(str(HERO_IMAGE_PATH), width="stretch")
        else:
            st.markdown(f"<strong>{HERO_IMAGE}</strong>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="company-gradient">
          <div class="company-grid">
            <div class="company-copy">
              <h2>Elite Medical (Nanjing) Co., Ltd.</h2>
              <p>
                Based in Nanjing, Jiangsu, China, Elite Medical designs and manufactures
                disposable medical products, surgical and laboratory instruments, and
                hospital equipment. With more than 10 years of experience, CE approved
                products, ISO13485:2016 certified facilities, one-stop sourcing service,
                and customization support, Elite Medical is positioned as a reliable
                medical product partner for distributors, hospitals, and procurement
                teams worldwide.
              </p>
            </div>
            <div class="company-panel">
              <div class="mini-badge"><strong>10+ Years</strong><span>Medical product manufacturing and export experience.</span></div>
              <div class="mini-badge"><strong>CE Approved</strong><span>Product support for international purchasing teams.</span></div>
              <div class="mini-badge"><strong>ISO13485:2016</strong><span>Certified facilities and quality management.</span></div>
              <div class="mini-badge"><strong>Customization</strong><span>Private label and product sourcing services available.</span></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="intro-strip">
          <div class="intro-item"><strong>Disposable Medical Products</strong><span>Catalog coverage for medical consumables, dressings, care products, and supply needs.</span></div>
          <div class="intro-item"><strong>Surgical & Laboratory Supply</strong><span>Support for surgical instruments, laboratory consumables, and hospital equipment.</span></div>
          <div class="intro-item"><strong>One-stop B2B Sourcing</strong><span>Specification, sourcing, and quotation support for export customers.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_section_heading("Trust", "Why Choose Elite Medical")
    st.markdown(
        """
        <div class="stat-grid">
          <div class="trust-card"><strong>10+ Years Experience</strong><span>Medical product design, manufacturing, and export.</span></div>
          <div class="trust-card"><strong>CE Approved</strong><span>Products prepared for international B2B markets.</span></div>
          <div class="trust-card"><strong>ISO13485:2016 Certified</strong><span>Certified facilities and quality management.</span></div>
          <div class="trust-card"><strong>One-stop Medical Sourcing</strong><span>Catalog support for distributors and procurement teams.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif st.session_state.current_page == "Products":
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

else:
    st.markdown(
        """
        <div class="contact-hero">
          <h2>Request a Quote</h2>
          <p>Send us your product requirements and our team will respond with specifications and quotation support.</p>
        </div>
        """,
        unsafe_allow_html=True,
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
