"""Brand Streamlit's initial HTML during deployment, before the server starts.

Streamlit's page config is delivered after connection; crawlers can otherwise
receive its default title and noscript text. This deliberately patches the
installed frontend, so validate the template on every build and fail clearly
if an upstream change makes the patch unsafe. No vendor JS is modified.
"""

import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from site_metadata import DESCRIPTION, PAGE_TITLE, SITE_NAME, SITE_URL

START = "<!-- elite-metadata:start -->"
END = "<!-- elite-metadata:end -->"


def brand_html(source):
    """Return an idempotent edit, preserving app scripts and the React root."""
    source = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", source, flags=re.S)
    for pattern, label in [
        (r"<title>.*?</title>", "title"),
        (r"<noscript>.*?</noscript>", "noscript"),
        (r"</head>", "head"),
        (r'<link\b[^>]*rel="shortcut icon"[^>]*>', "favicon"),
    ]:
        if len(re.findall(pattern, source, flags=re.S)) != 1:
            raise ValueError("Unexpected Streamlit HTML: expected exactly one " + label)

    title = html.escape(PAGE_TITLE, quote=True)
    description = html.escape(DESCRIPTION, quote=True)
    source = re.sub(r"<title>.*?</title>", "<title>" + title + "</title>", source, flags=re.S)
    source = re.sub(
        r'<link\b[^>]*rel="shortcut icon"[^>]*>',
        '<link rel="shortcut icon" type="image/png" href="/elite-favicon.png" />',
        source,
    )
    source = re.sub(
        r"<noscript>.*?</noscript>",
        "<noscript><h1>Elite Medical — Medical Supplies &amp; B2B Product Catalog</h1>"
        "<p>" + description + "</p>"
        '<p>Contact: <a href="mailto:info@elitemedline.com">info@elitemedline.com</a>.</p>'
        "<p>Enable JavaScript to browse the interactive product catalog.</p></noscript>",
        source, flags=re.S,
    )
    structured_data = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": SITE_URL + "/#website",
             "url": SITE_URL + "/", "name": SITE_NAME},
            {"@type": "Organization", "@id": SITE_URL + "/#organization",
             "name": "Elite Medical (Nanjing) Co., Ltd.",
             "url": SITE_URL + "/", "email": "info@elitemedline.com",
             "logo": SITE_URL + "/elite-logo.png"},
        ],
    }
    metadata = "\n".join([
        START,
        '<meta name="description" content="' + description + '" />',
        '<meta property="og:type" content="website" />',
        '<meta property="og:site_name" content="' + SITE_NAME + '" />',
        '<meta property="og:title" content="' + title + '" />',
        '<meta property="og:description" content="' + description + '" />',
        '<meta property="og:image" content="' + SITE_URL + '/elite-logo.png" />',
        '<meta name="twitter:card" content="summary" />',
        '<script type="application/ld+json">' + json.dumps(structured_data) + '</script>',
        END,
    ])
    return source.replace("</head>", metadata + "\n</head>")


def prepare(static_dir):
    from PIL import Image

    index = static_dir / "index.html"
    result = brand_html(index.read_text(encoding="utf-8"))
    logo_path = ROOT / "public" / "icons" / "logo.png"
    with Image.open(logo_path) as original:
        logo = original.convert("RGBA")
        logo.thumbnail((192, 192))
        icon = Image.new("RGBA", (192, 192), "white")
        icon.alpha_composite(logo, ((192 - logo.width) // 2, (192 - logo.height) // 2))
        icon.save(static_dir / "elite-favicon.png")
        # Streamlit may request its default favicon before page config arrives.
        icon.save(static_dir / "favicon.png")
    (static_dir / "elite-logo.png").write_bytes(logo_path.read_bytes())
    index.write_text(result, encoding="utf-8")
    print("Prepared Elite Medical title, description, structured data and favicon.")


if __name__ == "__main__":
    import streamlit

    prepare(Path(streamlit.__file__).resolve().parent / "static")
