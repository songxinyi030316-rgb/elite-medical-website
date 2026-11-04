# Elite Medical Product Catalog

Streamlit website for Elite Medical's B2B product catalog.

## Getting Started

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

For Streamlit Cloud, use `app.py` as the main file path.

## Render deployment and search metadata

Use this Build Command to install dependencies and brand the initial HTML:

```sh
pip install -r requirements.txt && python scripts/prepare_web_metadata.py
```

Keep the Start Command as:

```sh
streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true
```

The preparation script updates Streamlit's installed HTML template, preserving
its application assets. It provides the title, description, logo, and organization
information before JavaScript runs. It fails the build if the upstream template
changes incompatibly. `site_metadata.py` shares the title with the running app.
This is a compatibility workaround, not server rendering of the product catalog.
After deployment, verify the raw homepage HTML and request a recrawl in Google
Search Console. Google controls the final search title/snippet and update timing.
