import Link from "next/link";
import InquiryForm from "../../components/InquiryForm";
import products from "../../data/products.json";

export default function ProductDetailPage({ product }) {
  if (!product) {
    return null;
  }

  return (
    <main>
      <Link className="back-link" href="/products">
        Back to products
      </Link>

      <section className="product-detail">
        <div className="detail-image">
          <img src={product.image} alt="" />
        </div>

        <div className="detail-copy">
          <p className="product-category">{product.category}</p>
          <h1>{product.name}</h1>
          <p className="intro">{product.description}</p>

          <div className="variant-table" aria-label="Product variants">
            <div className="variant-row variant-head">
              <span>Spec</span>
              <span>Ref</span>
            </div>
            {product.variants.map((variant) => (
              <div className="variant-row" key={`${variant.spec}-${variant.ref}`}>
                <span>{variant.spec}</span>
                <span>{variant.ref}</span>
              </div>
            ))}
          </div>

          <a className="button primary" href="#inquiry">
            Request a quote
          </a>
        </div>
      </section>

      <section className="inquiry-section" id="inquiry">
        <div>
          <p className="eyebrow">Inquiry</p>
          <h2>Send a product inquiry</h2>
          <p>
            Share your company details and purchasing request. The current form
            logs submissions in the browser console.
          </p>
        </div>

        <InquiryForm productName={product.name} />
      </section>
    </main>
  );
}

export function getStaticPaths() {
  return {
    paths: products.map((product) => ({
      params: { id: product.id },
    })),
    fallback: false,
  };
}

export function getStaticProps({ params }) {
  return {
    props: {
      product: products.find((product) => product.id === params.id) || null,
    },
  };
}
