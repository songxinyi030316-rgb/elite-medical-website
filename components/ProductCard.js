import Link from "next/link";

const DEFAULT_PRODUCT_IMAGE = "/products/default.png";

export default function ProductCard({ product }) {
  const variantCount = product.variants?.length || 0;

  return (
    <article className="product-card" aria-label={product.name}>
      <div className="product-image">
        <img src={product.image || DEFAULT_PRODUCT_IMAGE} alt="" />
      </div>

      <div className="product-card-body">
        <p className="product-category">{product.category}</p>
        <h3>{product.name}</h3>
        <p>
          {variantCount > 0
            ? `${variantCount} extracted variant${variantCount === 1 ? "" : "s"}`
            : "Variant details need review"}
        </p>
      </div>

      <Link className="text-link" href={`/products/${encodeURIComponent(product.id)}`}>
        View product
      </Link>
    </article>
  );
}
