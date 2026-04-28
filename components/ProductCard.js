export default function ProductCard({ product }) {
  return (
    <article className="product-card">
      <div>
        <h2>{product.name}</h2>
        <p>{product.description}</p>
      </div>
      <strong>${product.price.toFixed(2)}</strong>
    </article>
  );
}
