import base64
import html
import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "products.json"
HERO_IMAGE = "/public/hero/cover.png"
HERO_IMAGE_PATH = ROOT / HERO_IMAGE.lstrip("/")
ICON_DIR = ROOT / "public" / "icons"
LOGO_PATH = ICON_DIR / "logo.png"
EXPERIENCE_ICON_PATH = ICON_DIR / "experience.png"
CE_ICON_PATH = ICON_DIR / "ce.png"
ISO_ICON_PATH = ICON_DIR / "iso.png"
SERVICE_ICON_PATH = ICON_DIR / "service.png"
COMPANY_DIR = ROOT / "public" / "company"
COMPANY_IMAGE_PATH = COMPANY_DIR / "company.png"
INNER_COMPANY_IMAGE_PATH = COMPANY_DIR / "innercompany.png"

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

PAGE_SLUGS = {
    "Home": "home",
    "About Us": "about",
    "Products": "products",
    "Contact": "contact",
}
SLUG_PAGES = {slug: page for page, slug in PAGE_SLUGS.items()}

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
    st.query_params["page"] = PAGE_SLUGS.get(page, PAGE_SLUGS["Home"])


def open_chatbot():
    st.session_state.chatbot_open = True


def close_chatbot():
    st.session_state.chatbot_open = False


def add_chatbot_query(query, products):
    cleaned_query = str(query).strip()
    if not cleaned_query:
        return

    st.session_state.chatbot_open = True
    st.session_state.chatbot_history.append({"role": "user", "content": cleaned_query})
    st.session_state.chatbot_history.append(
        {"role": "bot", "content": build_chatbot_reply(cleaned_query, products)}
    )
    st.session_state.chatbot_input = ""


def send_current_chatbot_query(products):
    add_chatbot_query(st.session_state.get("chatbot_input", ""), products)


def image_data_uri(path):
    if not path.exists():
        return ""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


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


def variant_summary(product):
    variants = product.get("variants", [])
    if not variants:
        return "REF/spec: needs review"

    summaries = []
    for variant in variants[:2]:
        ref = str(variant.get("ref", "needs_review"))
        spec = str(variant.get("spec", "needs_review"))
        summaries.append(f"{ref} - {spec}")

    if len(variants) > 2:
        summaries.append(f"+{len(variants) - 2} more variants")

    return "REF/spec: " + "; ".join(summaries)


def search_products_for_chat(query, products):
    cleaned_query = str(query).lower().strip()
    if not cleaned_query:
        return []

    matches = []
    for product in products:
        if matches_search(product, cleaned_query):
            matches.append(product)
        if len(matches) == 5:
            break

    return matches


def build_chatbot_reply(query, products):
    matches = search_products_for_chat(query, products)
    if not matches:
        return (
            "I could not find an exact match in the catalog. Please contact our team "
            "for sourcing support.\n\n"
            "Email: info@elitemedline.com\n"
            "Website: www.elitemedline.com\n\n"
            "You can also submit a quote request through the Contact page."
        )

    lines = ["Here are matching products from the Elite Medical catalog:"]
    for product in matches:
        lines.append(
            "\n".join(
                [
                    f"- {product['name']}",
                    f"  Category: {product['category']}",
                    f"  {variant_summary(product)}",
                ]
            )
        )

    return "\n\n".join(lines)


def render_chat_message(message):
    role = "user" if message.get("role") == "user" else "bot"
    content = html.escape(str(message.get("content", ""))).replace("\n", "<br>")
    st.markdown(
        f'<div class="chat-message {role}">{content}</div>',
        unsafe_allow_html=True,
    )


def render_chatbot(products):
    if "chatbot_open" not in st.session_state:
        st.session_state.chatbot_open = False
    if "chatbot_input" not in st.session_state:
        st.session_state.chatbot_input = ""
    if "chatbot_history" not in st.session_state:
        st.session_state.chatbot_history = [
            {
                "role": "bot",
                "content": "Hi! I can help you find products from the Elite Medical catalog.",
            }
        ]

    if not st.session_state.chatbot_open:
        st.markdown('<span class="chatbot-button-marker"></span>', unsafe_allow_html=True)
        st.button("💬 Need help?", key="chatbot_open_button", on_click=open_chatbot)
        return

    st.markdown('<span class="chatbot-panel-marker"></span>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="chatbot-title">
              <strong>Elite Medical Assistant</strong>
              <span>Local catalog search</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for message in st.session_state.chatbot_history[-6:]:
            render_chat_message(message)

        st.markdown('<div class="chatbot-suggestions">Quick search</div>', unsafe_allow_html=True)
        suggestion_row_1 = st.columns(3)
        suggestion_row_2 = st.columns(2)
        suggestions = [
            ("Medical Dressing", suggestion_row_1[0]),
            ("Bandage", suggestion_row_1[1]),
            ("Respiratory", suggestion_row_1[2]),
            ("Injection", suggestion_row_2[0]),
            ("Laboratory", suggestion_row_2[1]),
        ]
        for suggestion, column in suggestions:
            with column:
                st.button(
                    suggestion,
                    key=f"chatbot_suggestion_{suggestion}",
                    width="stretch",
                    on_click=add_chatbot_query,
                    args=(suggestion, products),
                )

        st.text_input(
            "Search by product, category, or REF code",
            key="chatbot_input",
            placeholder="Example: dressing, EL010101, respiratory",
        )
        action_col_1, action_col_2 = st.columns([1, .72])
        with action_col_1:
            st.button(
                "Send",
                key="chatbot_send",
                type="primary",
                width="stretch",
                on_click=send_current_chatbot_query,
                args=(products,),
            )
        with action_col_2:
            st.button("Close", key="chatbot_close", width="stretch", on_click=close_chatbot)


hero_background = image_data_uri(HERO_IMAGE_PATH)
hero_background_css = (
    "linear-gradient(90deg, rgba(7, 74, 50, .94) 0%, "
    "rgba(11, 108, 70, .78) 34%, rgba(11, 108, 70, .22) 62%, "
    f"rgba(11, 108, 70, 0) 100%), url('{hero_background}')"
    if hero_background
    else "linear-gradient(90deg, rgba(7, 74, 50, .94) 0%, rgba(11, 108, 70, .24) 100%)"
)
about_background = image_data_uri(COMPANY_IMAGE_PATH)
about_background_css = (
    "linear-gradient(90deg, rgba(7, 74, 50, .93) 0%, "
    "rgba(13, 103, 68, .72) 42%, rgba(13, 103, 68, .14) 100%), "
    f"url('{about_background}')"
    if about_background
    else "linear-gradient(90deg, rgba(7, 74, 50, .93) 0%, rgba(13, 103, 68, .18) 100%)"
)
experience_icon = image_data_uri(EXPERIENCE_ICON_PATH)
ce_icon = image_data_uri(CE_ICON_PATH)
iso_icon = image_data_uri(ISO_ICON_PATH)
service_icon = image_data_uri(SERVICE_ICON_PATH)
inner_company_image = image_data_uri(INNER_COMPANY_IMAGE_PATH)
logo_image = image_data_uri(LOGO_PATH)

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
        padding-top: 2.75rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, p {{
        color: {DARK};
    }}
    .site-header {{
        margin: 1.8rem calc(50% - 50vw) 1rem;
        padding: 0 max(1.5rem, calc((100vw - 1120px) / 2));
        background: #ffffff;
        border-bottom: 1px solid #e2eee8;
        box-shadow: 0 12px 32px rgba(37, 48, 43, .08);
        position: relative;
        z-index: 20;
    }}
    .site-header-inner {{
        min-height: 86px;
        display: flex;
        align-items: center;
        gap: 1.15rem;
    }}
    .brand-link {{
        display: flex;
        align-items: center;
        gap: .7rem;
        text-decoration: none;
        min-width: 250px;
    }}
    .brand-link img {{
        width: 62px;
        height: 62px;
        object-fit: contain;
    }}
    .brand-link span {{
        color: {DARK};
        font-size: 1.12rem;
        font-weight: 950;
        letter-spacing: .04em;
        white-space: nowrap;
    }}
    .nav-links {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.25rem;
        flex: 1;
    }}
    .nav-link {{
        position: relative;
        color: {DARK};
        text-decoration: none;
        font-size: .98rem;
        font-weight: 900;
        padding: .55rem .05rem;
        white-space: nowrap;
    }}
    .nav-link:hover {{
        color: {GREEN};
    }}
    .nav-link.active {{
        color: {GREEN};
    }}
    .nav-link.active::after {{
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: .18rem;
        height: 3px;
        border-radius: 999px;
        background: {GREEN};
    }}
    .quote-link {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        padding: 0 1rem;
        border-radius: 999px;
        background: {GREEN};
        color: #ffffff;
        text-decoration: none;
        font-weight: 900;
        white-space: nowrap;
        box-shadow: 0 12px 24px rgba(17, 132, 87, .18);
    }}
    .quote-link:hover {{
        background: #0c6f49;
        color: #ffffff;
    }}
    section[data-testid="stSidebar"] {{
        background: #f4fbf7;
        border-right: 1px solid #dcefe5;
    }}
    section[data-testid="stSidebar"] img {{
        max-width: 160px;
        margin-bottom: .5rem;
    }}
    .section-card, .trust-card, .category-card, .product-shell, .quote-card, .contact-card {{
        border: 1px solid #dcefe5;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(17, 132, 87, .08);
    }}
    .home-hero {{
        min-height: 460px;
        margin: .25rem calc(50% - 50vw) 0;
        padding: 0 max(1.5rem, calc((100vw - 1120px) / 2));
        background-image: {hero_background_css};
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        position: relative;
        overflow: hidden;
    }}
    .home-hero-content {{
        max-width: 520px;
        padding-bottom: 4.8rem;
    }}
    .home-kicker {{
        color: #d8f5e5;
        font-size: .95rem;
        font-weight: 950;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }}
    .home-hero h1 {{
        color: #ffffff;
        font-size: 3.4rem;
        line-height: 1.02;
        font-weight: 950;
        margin: 0 0 .45rem;
    }}
    .home-hero h2 {{
        color: #ffffff;
        font-size: 1.55rem;
        line-height: 1.16;
        margin: 0 0 .8rem;
        font-weight: 850;
    }}
    .home-hero p {{
        color: #edf8f1;
        font-size: 1.05rem;
        line-height: 1.5;
        margin: 0;
    }}
    .hero-action-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"],
    div[data-testid="stMarkdown"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"],
    div[data-testid="stMarkdownContainer"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"] {{
        position: relative;
        z-index: 5;
        width: min(430px, calc(100vw - 3rem));
        margin-top: -5.25rem;
        margin-left: max(0rem, calc((100vw - 1120px) / 2));
        margin-bottom: 3.2rem;
    }}
    div[data-testid="element-container"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button,
    div[data-testid="stMarkdown"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button,
    div[data-testid="stMarkdownContainer"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button {{
        min-height: 44px;
        box-shadow: 0 12px 24px rgba(0, 0, 0, .15);
    }}
    .company-section {{
        max-width: 1120px;
        margin: 0 auto 1.1rem;
        padding: 0;
    }}
    .company-layout {{
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(340px, .92fr);
        gap: 1.1rem;
        align-items: start;
    }}
    .company-text {{
        max-width: 610px;
    }}
    .company-eyebrow {{
        color: {GREEN};
        font-size: .78rem;
        font-weight: 950;
        letter-spacing: .06em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }}
    .company-text h2 {{
        color: {DARK};
        font-size: 1.75rem;
        line-height: 1.18;
        margin: 0 0 .55rem;
    }}
    .company-text p {{
        color: {MUTED};
        line-height: 1.62;
        margin: 0 0 .8rem;
    }}
    .company-points {{
        display: grid;
        gap: .42rem;
        margin-top: .65rem;
    }}
    .company-point {{
        display: flex;
        align-items: center;
        gap: .48rem;
        color: {DARK};
        font-weight: 760;
        font-size: .95rem;
    }}
    .company-point::before {{
        content: "";
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: {GREEN};
        flex: 0 0 auto;
    }}
    .feature-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .75rem;
    }}
    .feature-card {{
        border: 1px solid #e0eee6;
        border-radius: 14px;
        background: #ffffff;
        padding: 1rem .85rem;
        min-height: 154px;
        box-shadow: 0 10px 28px rgba(17, 132, 87, .08);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .feature-card strong {{
        display: block;
        color: {DARK};
        font-size: .98rem;
        line-height: 1.2;
        margin-bottom: .28rem;
    }}
    .feature-icon-img {{
        width: 56px;
        height: 56px;
        object-fit: contain;
        margin: 0 auto .6rem;
        display: block;
    }}
    .feature-card span {{
        color: {MUTED};
        font-size: .84rem;
        line-height: 1.34;
    }}
    .about-hero {{
        min-height: 370px;
        margin: .25rem calc(50% - 50vw) 1.15rem;
        padding: 0 max(1.5rem, calc((100vw - 1120px) / 2));
        background-image: {about_background_css};
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
    }}
    .about-hero-content {{
        max-width: 620px;
    }}
    .about-hero h1 {{
        color: #ffffff;
        font-size: 3rem;
        line-height: 1.05;
        margin: 0 0 .55rem;
        font-weight: 950;
    }}
    .about-hero p {{
        color: #eefaf3;
        font-size: 1.12rem;
        line-height: 1.5;
        margin: 0;
    }}
    .about-section {{
        max-width: 1120px;
        margin: 0 auto 1.05rem;
    }}
    .about-grid {{
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(320px, .92fr);
        gap: 1.25rem;
        align-items: center;
    }}
    .about-copy {{
        padding-right: .4rem;
    }}
    .about-kicker {{
        color: {GREEN};
        font-size: .78rem;
        font-weight: 950;
        letter-spacing: .06em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }}
    .about-copy h2, .about-section h2 {{
        color: {DARK};
        font-size: 1.65rem;
        line-height: 1.18;
        margin: 0 0 .55rem;
    }}
    .about-copy p {{
        color: {MUTED};
        line-height: 1.62;
        margin: 0 0 .72rem;
    }}
    .about-image {{
        width: 100%;
        max-height: 360px;
        object-fit: cover;
        border-radius: 18px;
        box-shadow: 0 18px 46px rgba(37, 48, 43, .16);
        border: 1px solid #dcefe5;
    }}
    .category-cloud {{
        display: flex;
        flex-wrap: wrap;
        gap: .42rem;
        margin-top: .75rem;
    }}
    .category-chip {{
        border-radius: 999px;
        background: #eefaf3;
        color: {DARK};
        border: 1px solid #d8efe2;
        padding: .28rem .58rem;
        font-size: .82rem;
        font-weight: 760;
    }}
    .about-card-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: .75rem;
        margin-top: .7rem;
    }}
    .about-card, .certificate-card {{
        border: 1px solid #dcefe5;
        border-radius: 14px;
        background: #ffffff;
        padding: .9rem;
        box-shadow: 0 10px 28px rgba(17, 132, 87, .08);
    }}
    .about-card strong, .certificate-card strong {{
        display: block;
        color: {DARK};
        line-height: 1.2;
        margin-bottom: .28rem;
    }}
    .about-card span, .certificate-card span {{
        color: {MUTED};
        font-size: .84rem;
        line-height: 1.35;
    }}
    .certificate-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .75rem;
        margin-top: .7rem;
    }}
    .certificate-card {{
        text-align: center;
        min-height: 150px;
    }}
    .certificate-card img {{
        width: 56px;
        height: 56px;
        object-fit: contain;
        margin-bottom: .55rem;
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
    .chatbot-button-marker,
    .chatbot-panel-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.chatbot-button-marker) + div[data-testid="element-container"] {{
        position: fixed;
        right: 1.15rem;
        bottom: 1.15rem;
        z-index: 1000;
        width: auto;
    }}
    div[data-testid="element-container"]:has(.chatbot-button-marker) + div[data-testid="element-container"] div.stButton > button {{
        background: {GREEN};
        color: #ffffff;
        border: 1px solid #0e724b;
        min-height: 44px;
        padding: .45rem .9rem;
        box-shadow: 0 14px 34px rgba(17, 132, 87, .28);
    }}
    div[data-testid="element-container"]:has(.chatbot-button-marker) + div[data-testid="element-container"] div.stButton > button:hover {{
        background: #0c6f49;
        color: #ffffff;
    }}
    div[data-testid="element-container"]:has(.chatbot-panel-marker) + div[data-testid="stVerticalBlock"] {{
        position: fixed;
        right: 1.15rem;
        bottom: 1.15rem;
        z-index: 1000;
        width: min(370px, calc(100vw - 2rem));
        max-height: min(76vh, 650px);
        overflow-y: auto;
        border: 1px solid #dcefe5;
        border-radius: 18px;
        background: #ffffff;
        padding: .9rem;
        box-shadow: 0 20px 60px rgba(37, 48, 43, .22);
    }}
    .chatbot-title {{
        border-bottom: 1px solid #e5f2ea;
        margin-bottom: .55rem;
        padding-bottom: .5rem;
    }}
    .chatbot-title strong {{
        display: block;
        color: {DARK};
        font-size: 1rem;
    }}
    .chatbot-title span {{
        color: {MUTED};
        font-size: .78rem;
    }}
    .chat-message {{
        border-radius: 13px;
        padding: .6rem .7rem;
        margin: .45rem 0;
        font-size: .86rem;
        line-height: 1.4;
    }}
    .chat-message.bot {{
        background: #effaf4;
        color: {DARK};
        border: 1px solid #d8efe2;
    }}
    .chat-message.user {{
        background: {GREEN};
        color: #ffffff;
        margin-left: 2.5rem;
    }}
    .chatbot-suggestions {{
        color: {GREEN};
        font-weight: 900;
        font-size: .78rem;
        margin: .55rem 0 .25rem;
        text-transform: uppercase;
        letter-spacing: .03em;
    }}
    div[data-testid="element-container"]:has(.chatbot-panel-marker) + div[data-testid="stVerticalBlock"] div.stButton > button {{
        min-height: 34px;
        padding: .2rem .5rem;
        font-size: .78rem;
    }}
    @media (max-width: 900px) {{
        .block-container {{
            padding-top: 2.25rem;
        }}
        .site-header {{
            margin-top: 1.45rem;
            padding: 0 1rem;
        }}
        .site-header-inner {{
            min-height: auto;
            padding: .85rem 0;
            flex-wrap: wrap;
        }}
        .brand-link {{
            min-width: 0;
            flex: 1 1 100%;
        }}
        .brand-link img {{
            width: 54px;
            height: 54px;
        }}
        .nav-links {{
            order: 2;
            flex: 1 1 100%;
            justify-content: flex-start;
            gap: .9rem;
            overflow-x: auto;
            padding-bottom: .15rem;
        }}
        .quote-link {{
            order: 1;
            min-height: 38px;
            padding: 0 .85rem;
        }}
        .stat-grid, .company-layout, .about-grid, .about-card-grid, .certificate-grid {{
            grid-template-columns: 1fr;
        }}
        .home-hero {{
            min-height: 420px;
            padding: 0 1.25rem;
            background-position: center right;
        }}
        .home-hero h1 {{
            font-size: 2.45rem;
        }}
        .home-hero h2 {{
            font-size: 1.22rem;
        }}
        div[data-testid="element-container"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"],
        div[data-testid="stMarkdown"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"],
        div[data-testid="stMarkdownContainer"]:has(.hero-action-marker) + div[data-testid="stHorizontalBlock"] {{
            margin-left: 1.25rem;
            margin-bottom: 2.4rem;
        }}
        .feature-grid {{
            grid-template-columns: 1fr;
        }}
        .about-hero {{
            min-height: 320px;
            padding: 0 1.25rem;
        }}
        .about-hero h1 {{
            font-size: 2.35rem;
        }}
        div[data-testid="element-container"]:has(.chatbot-panel-marker) + div[data-testid="stVerticalBlock"] {{
            right: .75rem;
            bottom: .75rem;
            width: calc(100vw - 1.5rem);
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

products = load_products()
counts = category_counts(products)

page_slug = st.query_params.get("page", PAGE_SLUGS["Home"])
if isinstance(page_slug, list):
    page_slug = page_slug[0] if page_slug else PAGE_SLUGS["Home"]
requested_page = SLUG_PAGES.get(str(page_slug).lower(), "Home")
st.session_state.current_page = requested_page
if "product_category" not in st.session_state:
    st.session_state.product_category = "All Categories"
if "product_search" not in st.session_state:
    st.session_state.product_search = ""

logo_tag = f'<img src="{logo_image}" alt="Elite Medical logo">' if logo_image else ""
nav_links = "\n".join(
    f'<a class="nav-link {"active" if st.session_state.current_page == page else ""}" '
    f'href="?page={slug}">{page}</a>'
    for page, slug in PAGE_SLUGS.items()
)
st.markdown(
    f"""
    <header class="site-header">
      <div class="site-header-inner">
        <a class="brand-link" href="?page=home">
          {logo_tag}
          <span>ELITE MEDICAL</span>
        </a>
        <nav class="nav-links">
          {nav_links}
        </nav>
        <a class="quote-link" href="?page=contact">Request a Quote</a>
      </div>
    </header>
    """,
    unsafe_allow_html=True,
)

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width=150)

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
    st.markdown(
        """
        <section class="home-hero">
          <div class="home-hero-content">
            <div class="home-kicker">ELITE MEDICAL</div>
            <h1>Medical Product Catalog 2026</h1>
            <h2>Disposable medical products and healthcare supplies for B2B procurement.</h2>
            <p>
              Export-ready medical consumables, laboratory supplies, and hospital
              product sourcing from a reliable partner in China.
            </p>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<span class="hero-action-marker"></span>', unsafe_allow_html=True)
    hero_button_1, hero_button_2, _ = st.columns([1, 1.05, 1.35])
    with hero_button_1:
        st.button(
            "View Products",
            type="primary",
            width="stretch",
            on_click=navigate_to,
            args=("Products",),
        )
    with hero_button_2:
        st.button(
            "Request a Quote",
            width="stretch",
            on_click=navigate_to,
            args=("Contact",),
        )

    st.markdown(
        f"""
        <section class="company-section">
          <div class="company-layout">
            <div class="company-text">
              <div class="company-eyebrow">Company Introduction</div>
              <h2>Elite Medical (Nanjing) Co., Ltd.</h2>
              <p>
                Based in Nanjing, China, Elite Medical supports international B2B
                customers with dependable medical product sourcing and export service.
                The company provides disposable medical products, medical consumables,
                laboratory consumables, surgical supplies, and hospital equipment.
              </p>
              <div class="company-points">
                <div class="company-point">More than 10 years experience</div>
                <div class="company-point">CE approved products</div>
                <div class="company-point">ISO13485 certified facilities</div>
                <div class="company-point">One-stop sourcing service</div>
              </div>
            </div>
            <div class="feature-grid">
              <div class="feature-card">
                <img class="feature-icon-img" src="{experience_icon}" alt="10+ Years Experience">
                <strong>10+ Years Experience</strong>
                <span>Manufacturing and export support for medical product buyers.</span>
              </div>
              <div class="feature-card">
                <img class="feature-icon-img" src="{ce_icon}" alt="CE Approved">
                <strong>CE Approved</strong>
                <span>Product supply prepared for international medical markets.</span>
              </div>
              <div class="feature-card">
                <img class="feature-icon-img" src="{iso_icon}" alt="ISO13485:2016 Certified">
                <strong>ISO13485:2016 Certified</strong>
                <span>Certified facilities and quality management support.</span>
              </div>
              <div class="feature-card">
                <img class="feature-icon-img" src="{service_icon}" alt="One-stop Medical Sourcing">
                <strong>One-stop Medical Sourcing</strong>
                <span>Product sourcing and quotation support for procurement teams.</span>
              </div>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

elif st.session_state.current_page == "About Us":
    st.markdown(
        """
        <section class="about-hero">
          <div class="about-hero-content">
            <h1>About Elite Medical</h1>
            <p>Reliable Medical Product Partner in China</p>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <section class="about-section">
          <div class="about-grid">
            <div class="about-copy">
              <div class="about-kicker">Elite Team</div>
              <h2>Elite Medical (Nanjing) Co., Ltd.</h2>
              <p>
                Established in 2006, Elite Medical (Nanjing) Co., Ltd. is a
                manufacturer and trader specializing in the research, development,
                and production of medical consumables.
              </p>
              <p>
                With mature production and after-sales service, Elite Medical helps
                international buyers create an efficient procurement experience with
                reliable, effective, convenient, and pleasant sourcing in China.
              </p>
              <p>
                Our team provides professional advice and sufficient purchasing
                suggestions, positioning Elite Medical as a reliable, efficient, and
                quality-assured medical product supplier in China.
              </p>
            </div>
            <div>
              <img class="about-image" src="{inner_company_image}" alt="Elite Medical team and office">
            </div>
          </div>
          <div class="category-cloud">
            <span class="category-chip">Respiratory and anaesthesia products</span>
            <span class="category-chip">Catheter products</span>
            <span class="category-chip">Urology products</span>
            <span class="category-chip">Intravenous injection and surgical products</span>
            <span class="category-chip">Disposable and diagnostic products</span>
            <span class="category-chip">Medical dressing pad</span>
            <span class="category-chip">Gauze</span>
            <span class="category-chip">Cotton</span>
            <span class="category-chip">Non-woven fabrics</span>
            <span class="category-chip">Plasters</span>
            <span class="category-chip">Bandages</span>
            <span class="category-chip">Tapes</span>
            <span class="category-chip">Other medical products</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="about-section">
          <div class="about-kicker">Why Choose Us</div>
          <h2>Trusted B2B Medical Supply Support</h2>
          <div class="about-card-grid">
            <div class="about-card"><strong>Ranked High Locally</strong><span>Recognized within the local medical product industry.</span></div>
            <div class="about-card"><strong>Multiple Certifications</strong><span>Compliance-focused supply and quality documentation support.</span></div>
            <div class="about-card"><strong>Growing Customer Base</strong><span>Serving more buyers with reliable export and sourcing support.</span></div>
            <div class="about-card"><strong>Quality Reputation</strong><span>Known for dependable product quality and practical service.</span></div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <section class="about-section">
          <div class="about-kicker">Certificates</div>
          <h2>Quality and Verification Support</h2>
          <div class="certificate-grid">
            <div class="certificate-card"><img src="{ce_icon}" alt="CE Certificate"><strong>CE Certificate</strong><span>Product documentation support for international markets.</span></div>
            <div class="certificate-card"><img src="{iso_icon}" alt="ISO Certificate"><strong>ISO Certificate</strong><span>Quality management and certified facility support.</span></div>
            <div class="certificate-card"><img src="{service_icon}" alt="SFDA / MDMA Verification"><strong>SFDA / MDMA Verification</strong><span>Verification support for regulated sourcing workflows.</span></div>
          </div>
        </section>
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

render_chatbot(products)
