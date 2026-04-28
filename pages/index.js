import ProductCard from "../components/ProductCard";
import categories from "../data/categories.json";
import products from "../data/products.json";

export default function Home() {
  return (
    <main>
      <section className="home-hero">
        <div className="hero-copy">
          <p className="eyebrow">Elite Medical</p>
          <h1>B2B medical product sourcing, organized for inquiry.</h1>
          <p className="intro">
            A professional catalog experience for medical distributors,
            procurement teams, and healthcare product buyers.
          </p>
          <div className="hero-actions">
            <a className="button primary" href="/products">
              Browse products
            </a>
            <a className="button secondary" href="#quote">
              Request a quote
            </a>
          </div>
        </div>

        <div className="hero-panel" aria-label="Catalog summary">
          <span>{categories.length}</span>
          <p>Product categories ready for structured B2B inquiry</p>
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <p className="eyebrow">Categories</p>
          <h2>Product categories</h2>
        </div>

        <div className="category-grid">
          {categories.map((category) => (
            <a className="category-card" href="/products" key={category}>
              {category}
            </a>
          ))}
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <p className="eyebrow">Catalog</p>
          <h2>Featured product</h2>
        </div>

        <section className="product-grid" aria-label="Featured products">
          {products.slice(0, 6).map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </section>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <p className="eyebrow">Why choose us</p>
          <h2>Built for medical procurement workflows</h2>
        </div>

        <div className="why-grid">
          <article>
            <h3>Structured references</h3>
            <p>Product pages keep specifications and reference numbers easy to review.</p>
          </article>
          <article>
            <h3>Category-first browsing</h3>
            <p>Buyers can move from product family to detailed inquiry quickly.</p>
          </article>
          <article>
            <h3>Inquiry-ready pages</h3>
            <p>Each product page includes a focused request form for B2B follow-up.</p>
          </article>
        </div>
      </section>

      <section className="cta-band" id="quote">
        <div>
          <p className="eyebrow">Request a Quote</p>
          <h2>Ready to discuss product requirements?</h2>
        </div>
        <p className="intro">
          Browse the catalog and send an inquiry from the relevant product page.
        </p>
        <a className="button primary" href="/products">
          Request a Quote
        </a>
      </section>
    </main>
  );
}
