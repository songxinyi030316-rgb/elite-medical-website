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
EXPORT_MAP_PATH = ROOT / "public" / "map.png"

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

PAGES = [
    ("home", "Home"),
    ("about", "About Us"),
    ("products", "Products"),
    ("contact", "Contact"),
]
PAGE_LABELS = {slug: label for slug, label in PAGES}
PAGE_ALIASES = {
    "home": "home",
    "Home": "home",
    "about": "about",
    "About Us": "about",
    "products": "products",
    "Products": "products",
    "contact": "contact",
    "Contact": "contact",
}

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


def set_product_category(category):
    st.session_state.product_category = category


def toggle_compare_product(product_id):
    selected = list(st.session_state.get("compare_products", []))
    st.session_state.show_compare_table = False
    if product_id in selected:
        selected.remove(product_id)
        st.session_state.compare_notice = ""
    elif len(selected) < 3:
        selected.append(product_id)
        st.session_state.compare_notice = ""
    else:
        st.session_state.compare_notice = "You can compare up to 3 products at a time."
    st.session_state.compare_products = selected


def navigate_to(page):
    page_slug = PAGE_ALIASES.get(str(page), str(page).lower())
    if page_slug not in PAGE_LABELS:
        page_slug = "home"
    st.session_state["page"] = page_slug
    st.session_state.current_page = PAGE_LABELS[page_slug]


def start_product_inquiry(product_name):
    st.session_state.selected_product = product_name
    st.session_state.inquiry_product = product_name
    navigate_to("Contact")


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


def product_image_path(product):
    image = str(product.get("image", "")).strip()
    if not image or image == "needs_review":
        return None

    if image.startswith("/public/"):
        path = ROOT / image.lstrip("/")
    else:
        raw_path = Path(image)
        path = raw_path if raw_path.is_absolute() else ROOT / image.lstrip("/")
    return path if path.exists() else None


def category_preview_images(products, categories, limit=3):
    images = []
    for category in categories:
        for product in products:
            if product.get("category") != category:
                continue
            path = product_image_path(product)
            if path:
                images.append((category, image_data_uri(path)))
                break
        if len(images) >= limit:
            break
    return images


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


def render_export_markets_section(show_map=False):
    map_image = image_data_uri(EXPORT_MAP_PATH) if show_map else ""
    if map_image:
        st.markdown(
            f"""
            <section class="export-map-section">
              <img src="{map_image}" alt="Elite Medical export markets map">
            </section>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <section class="export-section">
          <div>
            <span>Export Markets</span>
            <h2>Serving Global Medical Procurement Needs</h2>
            <p>
              Elite Medical supports B2B buyers, distributors, hospitals, and procurement
              teams sourcing medical consumables for international supply programs.
            </p>
          </div>
          <div class="market-grid">
            <div>Europe</div>
            <div>Middle East</div>
            <div>Southeast Asia</div>
            <div>North America</div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_faq_section():
    st.markdown(
        """
        <div class="section-heading compact-heading">
          <span>FAQ</span>
          <h2>Common Procurement Questions</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("What products does Elite Medical supply?"):
        st.write(
            "Elite Medical supplies disposable medical products, medical consumables, "
            "laboratory consumables, medical dressings, respiratory products, injection "
            "products, and related healthcare supplies."
        )
    with st.expander("Do products come with CE approval?"):
        st.write("Many products are CE approved. Please share the product and market requirements so our team can confirm documentation.")
    with st.expander("Are facilities ISO13485:2016 certified?"):
        st.write("Yes. Elite Medical works with ISO13485:2016 certified facilities and quality management support.")
    with st.expander("Can customers request customization?"):
        st.write("Yes. Customization services are available for suitable products, packaging, and sourcing requirements.")
    with st.expander("How can I request a quotation?"):
        st.write("Use the Contact page or a product Contact Now button with product name, quantity, and target market.")


def render_quick_rfq(form_key, compact_title="Quick Request a Quote"):
    product_key = f"{form_key}_product"
    if st.session_state.get("selected_product") and not st.session_state.get(product_key):
        st.session_state[product_key] = st.session_state.selected_product

    st.markdown('<span class="quick-rfq-marker"></span>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            f"""
            <div class="quick-rfq-copy">
              <span>RFQ</span>
              <h2>{compact_title}</h2>
              <p>Send basic requirements and our team will follow up with product and quotation support.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form(form_key):
            name_col, email_col, company_col = st.columns(3)
            with name_col:
                name = st.text_input("Name", key=f"{form_key}_name")
            with email_col:
                email = st.text_input("Email", key=f"{form_key}_email")
            with company_col:
                company = st.text_input("Company", key=f"{form_key}_company")
            product_col, quantity_col = st.columns([1.2, .8])
            with product_col:
                product = st.text_input(
                    "Product of Interest",
                    key=product_key,
                    placeholder="Product name or REF code",
                )
            with quantity_col:
                quantity = st.text_input(
                    "Quantity",
                    key=f"{form_key}_quantity",
                    placeholder="e.g., 500 boxes / 10,000 pcs",
                )
            message = st.text_area(
                "Message",
                key=f"{form_key}_message",
                placeholder="Share specifications, destination market, packaging, or certification needs.",
                height=84,
            )
            submitted = st.form_submit_button("Submit Quick RFQ")
        if submitted:
            st.success("Thank you. Your quote request has been received.")
            st.session_state.last_quick_rfq = {
                "name": name,
                "email": email,
                "company": company,
                "product": product,
                "quantity": quantity,
                "message": message,
            }


def product_sample_refs(product, limit=3):
    refs = [
        str(variant.get("ref", "needs_review"))
        for variant in product.get("variants", [])[:limit]
        if isinstance(variant, dict)
    ]
    return ", ".join(refs) if refs else "needs review"


def render_compare_panel(products):
    selected_ids = st.session_state.get("compare_products", [])
    product_lookup = {product["id"]: product for product in products}
    selected_products = [
        product_lookup[product_id]
        for product_id in selected_ids
        if product_id in product_lookup
    ]
    selected_count = len(selected_products)

    st.markdown('<span class="compare-panel-marker"></span>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            f"""
            <div class="compare-panel-header">
              <div>
                <h2>Product Compare</h2>
                <p>Select up to 3 products to compare specifications and REF codes.</p>
              </div>
              <span>{selected_count} / 3 selected</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("compare_notice"):
            st.warning(st.session_state.compare_notice)

        if not selected_products:
            st.markdown(
                """
                <div class="compare-empty">
                  No products selected yet. Use the compare button on product cards below.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            chip_columns = st.columns(min(3, selected_count))
            for column, product in zip(chip_columns, selected_products):
                with column:
                    st.markdown(
                        f"""
                        <div class="compare-chip">
                          <strong>{html.escape(product["name"])}</strong>
                          <span>{html.escape(product["category"])}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.button(
                        "Remove",
                        key=f"remove_compare_{product['id']}",
                        width="stretch",
                        on_click=toggle_compare_product,
                        args=(product["id"],),
                    )

        can_compare = selected_count >= 2
        action_col, helper_col = st.columns([.9, 1.6])
        with action_col:
            if st.button(
                "Compare Selected Products",
                width="stretch",
                type="primary" if can_compare else "secondary",
                disabled=not can_compare,
                key="compare_selected_products_button",
            ):
                st.session_state.show_compare_table = True
        with helper_col:
            if not can_compare:
                st.markdown(
                    '<div class="compare-helper">Select at least 2 products to compare.</div>',
                    unsafe_allow_html=True,
                )

        if st.session_state.get("show_compare_table") and can_compare:
            st.markdown('<div class="compare-result-title">Comparison Results</div>', unsafe_allow_html=True)
            st.table(
                [
                    {
                        "Product": product["name"],
                        "Category": product["category"],
                        "Variants": len(product.get("variants", [])),
                        "Sample REF Codes": product_sample_refs(product),
                    }
                    for product in selected_products
                ]
            )


def render_product_card(product, card_index=0):
    image_path = product_image_path(product)
    if image_path:
        image_markup = (
            f'<div class="product-image-slot has-image">'
            f'<img src="{image_data_uri(image_path)}" alt="{html.escape(product["name"])}">'
            f"</div>"
        )
    else:
        image_markup = '<div class="product-image-slot missing"><span>No image</span></div>'

    st.markdown('<span class="product-card-marker"></span>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            f"""
            <div class="product-card-content">
              {image_markup}
              <div class="product-name">{html.escape(product["name"])}</div>
              <div class="product-category">{html.escape(product["category"])}</div>
              <div class="variant-pill">{len(product["variants"])} variants</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("View Details"):
            if product["variants"]:
                st.table(product["variants"])
            else:
                st.write("Variant details need review.")
        st.markdown('<span class="product-contact-button-marker"></span>', unsafe_allow_html=True)
        st.button(
            "Contact Now",
            key=f"contact_now_{card_index}_{product['id']}",
            type="primary",
            width="stretch",
            on_click=start_product_inquiry,
            args=(product["name"],),
        )
        selected_for_compare = product["id"] in st.session_state.get("compare_products", [])
        compare_label = "Selected for Compare" if selected_for_compare else "Add to Compare"
        compare_marker_class = "product-compare-button-marker selected" if selected_for_compare else "product-compare-button-marker"
        st.markdown(f'<span class="{compare_marker_class}"></span>', unsafe_allow_html=True)
        st.button(
            compare_label,
            key=f"compare_{card_index}_{product['id']}",
            width="stretch",
            on_click=toggle_compare_product,
            args=(product["id"],),
        )


def render_category_quick_cards(categories, counts):
    for row_start in range(0, len(categories), 3):
        row_categories = categories[row_start : row_start + 3]
        st.markdown('<span class="category-quick-marker"></span>', unsafe_allow_html=True)
        columns = st.columns(3)
        for column, category in zip(columns, row_categories):
            is_selected = st.session_state.product_category == category
            with column:
                st.button(
                    f"{category}\n{counts.get(category, 0)} products",
                    key=f"quick_category_{category}",
                    type="primary" if is_selected else "secondary",
                    width="stretch",
                    on_click=set_product_category,
                    args=(category,),
                )


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


def sample_ref_summary(product):
    variants = product.get("variants", [])
    if not variants:
        return "Sample REF: needs review"

    variant = variants[0]
    ref = str(variant.get("ref", "needs_review"))
    spec = str(variant.get("spec", "needs_review"))
    return f"Sample REF: {ref} ({spec})"


def chatbot_search_text(product):
    variants = product.get("variants", [])
    variant_text = " ".join(
        " ".join(
            [
                str(variant.get("spec", "")),
                str(variant.get("ref", "")),
            ]
        )
        for variant in variants
        if isinstance(variant, dict)
    )
    return " ".join(
        [
            str(product.get("name", "")),
            str(product.get("category", "")),
            str(product.get("raw_category", "")),
            str(product.get("id", "")),
            variant_text,
        ]
    ).lower()


CHATBOT_STOP_WORDS = {
    "a",
    "an",
    "any",
    "can",
    "catalog",
    "do",
    "find",
    "for",
    "have",
    "i",
    "me",
    "need",
    "please",
    "product",
    "products",
    "show",
    "the",
    "you",
}


def chat_tokens(query):
    normalized = str(query).lower()
    separators = ",.!?;:()[]{}\"'"
    for separator in separators:
        normalized = normalized.replace(separator, " ")
    return [word for word in normalized.split() if word]


def search_products_for_chat(query, products):
    cleaned_query = str(query).lower().strip()
    if not cleaned_query:
        return []

    tokens = chat_tokens(cleaned_query)
    keywords = [word for word in tokens if word not in CHATBOT_STOP_WORDS]
    if not keywords:
        keywords = tokens

    scored_matches = []
    for product in products:
        searchable = chatbot_search_text(product)
        keyword_hits = sum(1 for keyword in keywords if keyword in searchable)
        phrase_hit = cleaned_query in searchable
        if phrase_hit or keyword_hits:
            score = keyword_hits + (10 if phrase_hit else 0)
            scored_matches.append((score, product))

    scored_matches.sort(key=lambda item: item[0], reverse=True)
    return [product for _, product in scored_matches[:5]]


def related_chatbot_recommendations(matches, products, limit=3):
    if not matches:
        return []

    matched_ids = {product["id"] for product in matches}
    primary_category = matches[0].get("category", "")
    recommendations = []
    for product in products:
        if product.get("id") in matched_ids:
            continue
        if product.get("category") == primary_category:
            recommendations.append(product)
        if len(recommendations) >= limit:
            break
    return recommendations


def chat_has_word(query, words):
    tokens = chat_tokens(query)
    return any(word in tokens for word in words)


def chat_has_phrase(query, phrases):
    normalized = str(query).lower()
    return any(phrase in normalized for phrase in phrases)


def build_chatbot_reply(query, products):
    cleaned_query = str(query).lower().strip()

    if chat_has_word(cleaned_query, ["hi", "hello", "hey"]):
        return (
            "Hi! 👋 I’m the Elite Medical assistant.\n"
            "I can help you find products from our catalog or guide you to request a quote.\n\n"
            "You can ask things like:\n"
            "- Do you have hydrocolloid dressing?\n"
            "- Show me bandage products\n"
            "- I need respiratory products"
        )

    if chat_has_phrase(cleaned_query, ["thank you"]) or chat_has_word(cleaned_query, ["thanks"]):
        return (
            "You're welcome! 😊\n"
            "Let me know if you need help finding any medical products."
        )

    if chat_has_phrase(cleaned_query, ["what can you do", "how to use"]) or chat_has_word(
        cleaned_query, ["help"]
    ):
        return (
            "I can help you:\n"
            "- Search products by name or category\n"
            "- Find REF codes and specifications\n"
            "- Guide you to request a quote\n\n"
            "Try asking:\n"
            "'Show me medical dressing'\n"
            "or\n"
            "'I need bandage products'"
        )

    matches = search_products_for_chat(query, products)
    if not matches:
        return (
            "I couldn’t find an exact match in our catalog.\n\n"
            "You can try:\n"
            "- dressing\n"
            "- bandage\n"
            "- respiratory\n\n"
            "Or contact our team for sourcing support:\n"
            "info@elitemedline.com"
        )

    lines = ["Here are matching products from the Elite Medical catalog:"]
    for product in matches:
        lines.append(
            "\n".join(
                [
                    f"- {product['name']}",
                    f"  Category: {product['category']}",
                    f"  {sample_ref_summary(product)}",
                ]
            )
        )

    recommendations = related_chatbot_recommendations(matches, products)
    if recommendations:
        lines.append(
            "You may also be interested in…\n"
            + "\n".join(
                [
                    f"- {product['name']} ({sample_ref_summary(product)})"
                    for product in recommendations
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
    .site-header-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] {{
        height: 96px;
        margin: 1.25rem calc(50% - 50vw) 1rem;
        padding: 0 72px;
        background: #ffffff;
        border-bottom: 1px solid #e2eee8;
        box-shadow: 0 12px 32px rgba(37, 48, 43, .08);
        position: relative;
        z-index: 20;
        display: flex !important;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }}
    div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        display: flex;
        align-items: center;
        height: 96px;
    }}
    div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {{
        width: 100%;
        display: flex;
        align-items: center;
    }}
    .brand-static {{
        display: flex;
        align-items: center;
        gap: 18px;
        height: 96px;
        line-height: 1;
    }}
    .brand-static img {{
        width: auto;
        height: 54px;
        object-fit: contain;
        display: block;
    }}
    .brand-static span {{
        color: {DARK};
        font-size: 1.12rem;
        font-weight: 950;
        letter-spacing: .04em;
        white-space: nowrap;
        line-height: 1;
    }}
    div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button {{
        min-height: 42px;
        border: 0;
        border-radius: 0;
        background: transparent;
        color: {DARK} !important;
        text-decoration: none !important;
        font-size: .98rem;
        font-weight: 900;
        box-shadow: none;
        padding: 0 .1rem;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button:hover {{
        color: {GREEN} !important;
        background: transparent;
    }}
    div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button[kind="primary"] {{
        position: relative;
        background: transparent;
        color: {GREEN} !important;
        border-bottom: 3px solid {GREEN};
        border-radius: 0;
    }}
    section[data-testid="stSidebar"] {{
        background: #f4fbf7;
        border-right: 1px solid #dcefe5;
    }}
    section[data-testid="stSidebar"] img {{
        max-width: 160px;
        margin-bottom: .5rem;
    }}
    .section-card, .trust-card, .category-card, .quote-card, .contact-card {{
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
    .buyer-flow-section,
    .support-section {{
        max-width: 1120px;
        margin: 1.05rem auto;
    }}
    .compact-section-title {{
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: .85rem;
    }}
    .compact-section-title span {{
        color: {GREEN};
        font-size: .76rem;
        font-weight: 950;
        letter-spacing: .06em;
        text-transform: uppercase;
    }}
    .compact-section-title h2 {{
        color: {DARK};
        font-size: 1.45rem;
        line-height: 1.16;
        margin: .12rem 0 0;
    }}
    .compact-section-title p {{
        max-width: 420px;
        color: {MUTED};
        font-size: .9rem;
        line-height: 1.45;
        margin: 0;
    }}
    .work-steps {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .75rem;
        position: relative;
    }}
    .work-step {{
        position: relative;
        border: 1px solid #dcefe5;
        border-radius: 16px;
        background: linear-gradient(180deg, #ffffff 0%, #f6fcf9 100%);
        padding: .95rem .85rem .9rem;
        box-shadow: 0 10px 26px rgba(17, 132, 87, .07);
        min-height: 126px;
    }}
    .work-step:not(:last-child)::after {{
        content: "";
        position: absolute;
        top: 33px;
        right: -.75rem;
        width: .75rem;
        height: 2px;
        background: #bfe4d0;
    }}
    .step-number {{
        width: 38px;
        height: 38px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: {GREEN};
        color: #ffffff;
        font-weight: 950;
        margin-bottom: .65rem;
        box-shadow: 0 8px 18px rgba(17, 132, 87, .2);
    }}
    .work-step strong,
    .support-card strong {{
        display: block;
        color: {DARK};
        font-size: .98rem;
        line-height: 1.2;
        margin-bottom: .28rem;
    }}
    .work-step span,
    .support-card span {{
        display: block;
        color: {MUTED};
        font-size: .84rem;
        line-height: 1.38;
    }}
    .support-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .75rem;
    }}
    .support-card {{
        border: 1px solid #e0eee6;
        border-radius: 16px;
        background: #ffffff;
        padding: .95rem .85rem;
        min-height: 138px;
        box-shadow: 0 10px 26px rgba(37, 48, 43, .06);
    }}
    .support-icon {{
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #e8f7ee;
        color: {GREEN};
        font-weight: 950;
        margin-bottom: .7rem;
    }}
    .quick-rfq, .export-section {{
        max-width: 1120px;
        margin: 1rem auto;
        border-radius: 18px;
        border: 1px solid #dcefe5;
        background: #ffffff;
        box-shadow: 0 12px 34px rgba(17, 132, 87, .08);
    }}
    .export-section span, .quick-rfq-copy span {{
        color: {GREEN};
        font-size: .76rem;
        font-weight: 950;
        text-transform: uppercase;
        letter-spacing: .06em;
    }}
    .export-section h2, .quick-rfq-copy h2 {{
        color: {DARK};
        margin: .12rem 0 0;
        font-size: 1.38rem;
        line-height: 1.18;
    }}
    .quick-rfq {{
        padding: .95rem;
        background: linear-gradient(135deg, #f4fbf7 0%, #ffffff 72%);
    }}
    .quick-rfq-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.quick-rfq-marker) + div[data-testid="stVerticalBlock"] {{
        max-width: 1120px;
        margin: 1rem auto;
        padding: .95rem;
        border-radius: 18px;
        border: 1px solid #dcefe5;
        background: linear-gradient(135deg, #f4fbf7 0%, #ffffff 72%);
        box-shadow: 0 12px 34px rgba(17, 132, 87, .08);
    }}
    .quick-rfq-copy {{
        margin-bottom: .65rem;
    }}
    .quick-rfq-copy p {{
        color: {MUTED};
        margin: .22rem 0 0;
        font-size: .9rem;
    }}
    .export-section {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(300px, .75fr);
        gap: 1rem;
        align-items: center;
        padding: 1rem;
        background: linear-gradient(135deg, #ffffff 0%, #eefaf3 100%);
    }}
    .export-section p {{
        color: {MUTED};
        margin: .4rem 0 0;
        line-height: 1.5;
    }}
    .export-map-section {{
        max-width: 1200px;
        width: 100%;
        margin: 40px auto;
        padding: 0;
    }}
    .export-map-section img {{
        width: 100%;
        height: auto;
        object-fit: contain;
        display: block;
        margin: 0 auto;
    }}
    .market-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .55rem;
    }}
    .market-grid div {{
        border-radius: 14px;
        border: 1px solid #dcefe5;
        background: #ffffff;
        padding: .7rem;
        color: {DARK};
        font-weight: 900;
        text-align: center;
        box-shadow: 0 8px 20px rgba(17, 132, 87, .06);
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
    .products-landing {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(230px, .42fr);
        gap: 1.25rem;
        align-items: center;
        min-height: 170px;
        padding: 1.35rem 1.45rem;
        margin: .2rem 0 .95rem;
        border-radius: 20px;
        border: 1px solid #d7efe1;
        background:
            radial-gradient(circle at 85% 20%, rgba(255, 255, 255, .92), rgba(255, 255, 255, 0) 30%),
            linear-gradient(135deg, #e7f8ee 0%, #f9fffb 62%, #ffffff 100%);
        box-shadow: 0 18px 44px rgba(17, 132, 87, .10);
        overflow: hidden;
    }}
    .products-landing-kicker {{
        color: {GREEN};
        font-size: .78rem;
        font-weight: 950;
        text-transform: uppercase;
        letter-spacing: .07em;
        margin-bottom: .25rem;
    }}
    .products-landing h1 {{
        color: {DARK};
        font-size: 2.15rem;
        line-height: 1.05;
        margin: 0 0 .35rem;
        font-weight: 950;
    }}
    .products-landing p {{
        color: {MUTED};
        max-width: 560px;
        margin: 0;
        font-size: 1rem;
        line-height: 1.45;
    }}
    .products-hero-images {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: .55rem;
    }}
    .products-hero-image {{
        width: 86px;
        height: 104px;
        border-radius: 16px;
        background: #ffffff;
        border: 1px solid #dcefe5;
        box-shadow: 0 14px 30px rgba(37, 48, 43, .10);
        object-fit: contain;
        padding: .45rem;
    }}
    .products-hero-image:nth-child(2) {{
        width: 104px;
        height: 124px;
    }}
    .products-section-label {{
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 1rem;
        margin: .1rem 0 .55rem;
    }}
    .products-section-label h2 {{
        margin: 0;
        color: {DARK};
        font-size: 1.2rem;
        font-weight: 950;
    }}
    .products-section-label span {{
        color: {MUTED};
        font-size: .88rem;
    }}
    .category-quick-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.category-quick-marker) + div[data-testid="stHorizontalBlock"] {{
        gap: .55rem;
        margin-bottom: .8rem;
    }}
    div[data-testid="element-container"]:has(.category-quick-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button {{
        min-height: 78px;
        border-radius: 16px;
        background: #ffffff;
        border: 1px solid #dcefe5;
        color: {DARK};
        box-shadow: 0 10px 24px rgba(17, 132, 87, .07);
        line-height: 1.18;
        padding: .58rem .62rem;
        white-space: pre-line;
        text-align: left;
        justify-content: flex-start;
    }}
    div[data-testid="element-container"]:has(.category-quick-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button::before {{
        content: "";
        width: 26px;
        height: 26px;
        border-radius: 9px;
        margin-right: .5rem;
        background: linear-gradient(135deg, #18a66a, #bcebd0);
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .68);
    }}
    div[data-testid="element-container"]:has(.category-quick-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button:hover {{
        border-color: {GREEN};
        background: #f4fbf7;
        color: {GREEN};
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(17, 132, 87, .12);
    }}
    div[data-testid="element-container"]:has(.category-quick-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button[kind="primary"] {{
        border-color: {GREEN};
        background: #eaf8f0;
        color: {GREEN};
        box-shadow: inset 0 0 0 1px rgba(17, 132, 87, .18), 0 12px 26px rgba(17, 132, 87, .12);
    }}
    .catalog-count-line {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .8rem;
        margin: .45rem 0 .7rem;
    }}
    .catalog-count-line strong {{
        color: {DARK};
        font-size: 1.02rem;
    }}
    .catalog-count-line span {{
        color: {GREEN};
        font-weight: 900;
        font-size: .88rem;
    }}
    .compare-panel-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.compare-panel-marker) + div[data-testid="stVerticalBlock"] {{
        margin: 1.05rem 0 0;
        padding: 1.45rem 1.55rem;
        border-radius: 20px;
        border: 1px solid #c8ead7;
        background:
            radial-gradient(circle at 96% 8%, rgba(188, 235, 208, .32), rgba(188, 235, 208, 0) 32%),
            linear-gradient(135deg, #edf9f3 0%, #fbfffd 72%);
        box-shadow: 0 16px 38px rgba(17, 132, 87, .10);
    }}
    .compare-panel-header {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: .75rem;
        padding-bottom: .7rem;
        border-bottom: 1px solid #dcefe5;
    }}
    .compare-panel-header h2 {{
        color: {DARK};
        font-size: 1.28rem;
        line-height: 1.15;
        margin: 0 0 .2rem;
    }}
    .compare-panel-header p {{
        color: {MUTED};
        font-size: .92rem;
        margin: 0;
    }}
    .compare-panel-header span {{
        flex: 0 0 auto;
        color: {GREEN};
        background: #ffffff;
        border: 1px solid #cfead9;
        border-radius: 999px;
        padding: .32rem .7rem;
        font-weight: 950;
        font-size: .86rem;
        box-shadow: 0 8px 18px rgba(17, 132, 87, .07);
    }}
    .compare-empty {{
        border-radius: 14px;
        border: 1px dashed #bddfc9;
        background: rgba(255,255,255,.72);
        color: {MUTED};
        font-size: .92rem;
        padding: .75rem;
        margin: .35rem 0 .75rem;
    }}
    .compare-chip {{
        min-height: 76px;
        border: 1px solid #dcefe5;
        border-radius: 14px;
        background: #ffffff;
        padding: .65rem .7rem;
        box-shadow: 0 8px 20px rgba(17, 132, 87, .06);
    }}
    .compare-chip strong {{
        display: block;
        color: {DARK};
        font-size: .9rem;
        line-height: 1.22;
        margin-bottom: .25rem;
    }}
    .compare-chip span {{
        color: {MUTED};
        font-size: .82rem;
    }}
    .compare-helper {{
        color: {MUTED};
        font-size: .9rem;
        padding-top: .5rem;
    }}
    .compare-result-title {{
        margin: .9rem 0 .45rem;
        color: {DARK};
        font-weight: 950;
        font-size: 1rem;
    }}
    .product-grid-divider {{
        display: flex;
        align-items: center;
        gap: .85rem;
        margin: 36px 0 28px;
        color: {GREEN};
        font-size: .78rem;
        font-weight: 950;
        letter-spacing: .06em;
        text-transform: uppercase;
    }}
    .product-grid-divider::before,
    .product-grid-divider::after {{
        content: "";
        height: 1px;
        background: #dcefe5;
        flex: 1 1 auto;
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
    .product-card-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.product-card-marker) + div[data-testid="stVerticalBlock"] {{
        min-height: 430px;
        height: 100%;
        padding: .8rem;
        margin-bottom: .85rem;
        border: 1px solid #dcefe5;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 10px 28px rgba(17, 132, 87, .08);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}
    .product-card-content {{
        display: flex;
        flex-direction: column;
        min-height: 266px;
    }}
    .product-image-slot {{
        height: 150px;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: .65rem;
        overflow: hidden;
    }}
    .product-image-slot.has-image img {{
        width: 100%;
        max-width: 172px;
        height: 150px;
        object-fit: contain;
        display: block;
    }}
    .product-image-slot.missing {{
        height: 52px;
        justify-content: flex-start;
        margin: .2rem 0 .55rem;
    }}
    .product-image-slot.missing span {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #f2f8f4;
        color: {MUTED};
        border-radius: 999px;
        border: 1px dashed #bddfc9;
        font-size: .78rem;
        font-weight: 850;
        padding: .22rem .58rem;
    }}
    .product-name {{
        color: {DARK};
        font-size: 1rem;
        line-height: 1.22;
        font-weight: 950;
        min-height: 48px;
        margin-bottom: .32rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .product-category {{
        color: {MUTED};
        font-size: .86rem;
        line-height: 1.3;
        min-height: 22px;
        margin-bottom: .45rem;
    }}
    .variant-pill {{
        display: inline-flex;
        align-items: center;
        align-self: flex-start;
        min-height: 28px;
        border-radius: 999px;
        background: #eefaf3;
        color: {GREEN};
        border: 1px solid #cfead9;
        font-size: .8rem;
        font-weight: 900;
        padding: .18rem .58rem;
    }}
    .product-contact-button-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.product-contact-button-marker) + div[data-testid="element-container"] div.stButton > button {{
        margin-top: .5rem;
        min-height: 36px;
        border-radius: 999px;
        background: #21a86f;
        border: 1px solid #21a86f;
        color: #ffffff;
        box-shadow: 0 8px 18px rgba(33, 168, 111, .16);
        font-size: .88rem;
        font-weight: 900;
    }}
    div[data-testid="element-container"]:has(.product-contact-button-marker) + div[data-testid="element-container"] div.stButton > button:hover {{
        background: #1c985f;
        border-color: #1c985f;
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 10px 22px rgba(33, 168, 111, .2);
    }}
    .product-compare-button-marker {{
        display: none;
    }}
    div[data-testid="element-container"]:has(.product-compare-button-marker) + div[data-testid="element-container"] div.stButton > button {{
        min-height: 32px;
        margin-top: .42rem;
        background: #ffffff;
        border: 1px solid #cfead9;
        color: {DARK};
        box-shadow: none;
        font-size: .82rem;
        font-weight: 850;
    }}
    div[data-testid="element-container"]:has(.product-compare-button-marker) + div[data-testid="element-container"] div.stButton > button:hover {{
        background: #f4fbf7;
        border-color: {GREEN};
        color: {GREEN};
    }}
    div[data-testid="element-container"]:has(.product-compare-button-marker.selected) + div[data-testid="element-container"] div.stButton > button {{
        background: #eaf8f0;
        border-color: {GREEN};
        color: {GREEN};
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
        div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] {{
            margin-top: 1.45rem;
            padding: 0 1rem;
            min-height: auto;
            padding: .85rem 0;
            flex-wrap: wrap !important;
        }}
        .brand-static {{
            min-width: 0;
            flex: 1 1 100%;
        }}
        .brand-static img {{
            width: 54px;
            height: 54px;
        }}
        div[data-testid="element-container"]:has(.site-header-marker) + div[data-testid="stHorizontalBlock"] div.stButton > button {{
            min-height: 38px;
            font-size: .9rem;
        }}
        .stat-grid, .company-layout, .about-grid, .about-card-grid, .certificate-grid, .export-section {{
            grid-template-columns: 1fr;
        }}
        .market-grid {{
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
        .compact-section-title {{
            align-items: flex-start;
            flex-direction: column;
            gap: .35rem;
        }}
        .work-steps,
        .support-grid {{
            grid-template-columns: 1fr;
        }}
        .work-step:not(:last-child)::after {{
            display: none;
        }}
        .about-hero {{
            min-height: 320px;
            padding: 0 1.25rem;
        }}
        .about-hero h1 {{
            font-size: 2.35rem;
        }}
        .products-landing {{
            grid-template-columns: 1fr;
            min-height: auto;
            padding: 1.05rem;
        }}
        .products-landing h1 {{
            font-size: 1.8rem;
        }}
        .products-hero-images {{
            justify-content: flex-start;
        }}
        .products-hero-image {{
            width: 74px;
            height: 88px;
        }}
        .products-section-label {{
            align-items: flex-start;
            flex-direction: column;
            gap: .12rem;
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

if "page" not in st.session_state:
    st.session_state["page"] = "home"
page = st.session_state["page"]
if page not in PAGE_LABELS:
    page = "home"
    st.session_state["page"] = page
st.session_state.current_page = PAGE_LABELS[page]
if "product_category" not in st.session_state:
    st.session_state.product_category = "All Categories"
if "product_search" not in st.session_state:
    st.session_state.product_search = ""
if "selected_product" not in st.session_state:
    st.session_state.selected_product = ""
if "inquiry_product" not in st.session_state:
    st.session_state.inquiry_product = st.session_state.selected_product
if "compare_products" not in st.session_state:
    st.session_state.compare_products = []
if "compare_notice" not in st.session_state:
    st.session_state.compare_notice = ""
if "show_compare_table" not in st.session_state:
    st.session_state.show_compare_table = False
if "last_quick_rfq" not in st.session_state:
    st.session_state.last_quick_rfq = {}

logo_tag = f'<img src="{logo_image}" alt="Elite Medical logo">' if logo_image else ""
st.markdown('<span class="site-header-marker"></span>', unsafe_allow_html=True)
header_columns = st.columns([3.4, .82, 1.08, .98, .98])
with header_columns[0]:
    st.markdown(
        f"""
        <div class="brand-static">
          {logo_tag}
          <span>ELITE MEDICAL</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
for column, (page_slug, page_label) in zip(header_columns[1:], PAGES):
    with column:
        st.button(
            page_label,
            key=f"nav_{page_slug}",
            type="primary" if page == page_slug else "secondary",
            width="stretch",
            on_click=navigate_to,
            args=(page_slug,),
        )

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width=150)

if page == "products":
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

if page == "home":
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
              <div class="company-eyebrow">COMPANY INTRODUCTION</div>
              <h2>Reliable B2B Medical Product Supplier</h2>
              <p>
                Elite Medical (Nanjing) Co., Ltd. supports international buyers
                with medical consumables, surgical supplies, laboratory consumables,
                and hospital equipment. With CE approved products, ISO13485:2016
                certified facilities, and one-stop sourcing support, we help
                procurement teams source products efficiently.
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

    st.markdown(
        """
        <section class="buyer-flow-section">
          <div class="compact-section-title">
            <div>
              <span>Buyer Process</span>
              <h2>How We Work With Buyers</h2>
            </div>
            <p>A clear sourcing workflow helps purchasing teams move from inquiry to shipment with fewer delays.</p>
          </div>
          <div class="work-steps">
            <div class="work-step">
              <div class="step-number">1</div>
              <strong>Send Inquiry</strong>
              <span>Share product requirements, REF codes, market needs, and expected quantity.</span>
            </div>
            <div class="work-step">
              <div class="step-number">2</div>
              <strong>Confirm Specifications</strong>
              <span>Our team checks size, material, packaging, certification, and sourcing details.</span>
            </div>
            <div class="work-step">
              <div class="step-number">3</div>
              <strong>Sample &amp; Approval</strong>
              <span>Review samples or documentation before confirming the purchase order.</span>
            </div>
            <div class="work-step">
              <div class="step-number">4</div>
              <strong>Production &amp; Delivery</strong>
              <span>Coordinate production, inspection, export documents, and shipment support.</span>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="support-section">
          <div class="compact-section-title">
            <div>
              <span>B2B Support</span>
              <h2>Who We Support</h2>
            </div>
            <p>Built for buyers who need dependable medical product sourcing and responsive quotation support.</p>
          </div>
          <div class="support-grid">
            <div class="support-card">
              <div class="support-icon">D</div>
              <strong>Medical Distributors</strong>
              <span>Catalog sourcing, repeat supply, and documentation support for distributor programs.</span>
            </div>
            <div class="support-card">
              <div class="support-icon">H</div>
              <strong>Hospitals &amp; Clinics</strong>
              <span>Practical product options for routine medical consumables and care supplies.</span>
            </div>
            <div class="support-card">
              <div class="support-icon">P</div>
              <strong>Procurement Teams</strong>
              <span>Clear specifications and quotation support for comparison and approval workflows.</span>
            </div>
            <div class="support-card">
              <div class="support-icon">I</div>
              <strong>Importers &amp; Wholesalers</strong>
              <span>Export-focused coordination for bulk orders, packaging needs, and market supply.</span>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    render_export_markets_section(show_map=True)

elif page == "about":
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

    render_export_markets_section()
    render_faq_section()

elif page == "products":
    product_quick_categories = [
        "Medical Dressing",
        "Bandage",
        "Protective Products",
        "Respiratory",
        "Injection",
        "Laboratory",
    ]
    preview_images = category_preview_images(products, product_quick_categories)
    if not preview_images and service_icon:
        preview_images = [("Medical Products", service_icon)]
    preview_html = "".join(
        f'<img class="products-hero-image" src="{image}" alt="{html.escape(category)} product">'
        for category, image in preview_images
        if image
    )

    st.markdown(
        f"""
        <section class="products-landing">
          <div>
            <div class="products-landing-kicker">Elite Medical Catalog</div>
            <h1>Product Catalog</h1>
            <p>Explore our full range of medical products for B2B sourcing and quotation support.</p>
          </div>
          <div class="products-hero-images">
            {preview_html}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="products-section-label">
          <h2>Browse by Category</h2>
          <span>Select a category to filter the catalog.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_category_quick_cards(product_quick_categories, counts)
    render_compare_panel(products)

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

    st.markdown('<div class="product-grid-divider">Browse Products</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="catalog-count-line">
          <strong>Product Grid</strong>
          <span>{len(filtered_products)} products shown</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not filtered_products:
        st.info("No matching products found. Try another category or search term.")

    for start in range(0, len(filtered_products), 3):
        columns = st.columns(3)
        for offset, (column, product) in enumerate(
            zip(columns, filtered_products[start : start + 3])
        ):
            with column:
                render_product_card(product, start + offset)

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
        if st.session_state.selected_product and not st.session_state.inquiry_product:
            st.session_state.inquiry_product = st.session_state.selected_product
        with st.form("inquiry_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                company = st.text_input("Company")
                interested_product = st.text_input(
                    "Product of Interest",
                    key="inquiry_product",
                    placeholder="Enter product name or REF code",
                )
            with col2:
                email = st.text_input("Email")
                quantity = st.text_input(
                    "Quantity",
                    placeholder="e.g., 500 boxes / 10,000 pcs",
                )
            message = st.text_area("Message")
            submitted = st.form_submit_button("Submit Inquiry")
        if submitted:
            st.success("Thank you. Your inquiry has been received.")
            st.markdown(
                f"""
                <div class="section-card" style="margin-top:.75rem;">
                  <strong>Inquiry summary</strong><br>
                  Product: {html.escape(interested_product or "Not specified")}<br>
                  Quantity: {html.escape(quantity or "Not specified")}
                </div>
                """,
                unsafe_allow_html=True,
            )
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
