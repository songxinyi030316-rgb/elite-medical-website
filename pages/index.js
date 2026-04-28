import ProductCard from "../components/ProductCard";
import products from "../data/products.json";

export default function Home() {
  return (
    <main>
      <section className="hero">
        <p className="eyebrow">New Project</p>
        <h1>Products</h1>
        <p className="intro">
          A small Next.js starter with reusable components and local JSON data.
        </p>
      </section>

      <section className="grid" aria-label="Sample products">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </section>
    </main>
  );
}
