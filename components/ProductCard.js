import Link from "next/link";

export default function ProductCard({ product }) {
  return (
    <article className="product-card" aria-label={product.name}>
      <div className="product-image">
        <img src={product.image} alt="" />
      </div>

      <div className="product-card-body">
        <p className="product-category">{product.category}</p>
        <h3>{product.name}</h3>
        <p>{product.description}</p>
      </div>

      <Link className="text-link" href={`/products/${product.id}`}>
        View product
      </Link>
    </article>
  );
}
