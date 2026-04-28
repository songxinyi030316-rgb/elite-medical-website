import { useMemo, useState } from "react";
import ProductCard from "../../components/ProductCard";
import categories from "../../data/categories.json";
import products from "../../data/products.json";

export default function ProductsPage() {
  const [activeCategory, setActiveCategory] = useState("All");

  const filteredProducts = useMemo(() => {
    if (activeCategory === "All") {
      return products;
    }

    return products.filter((product) => product.category === activeCategory);
  }, [activeCategory]);

  return (
    <main>
      <section className="page-heading">
        <p className="eyebrow">Product Catalog</p>
        <h1>Medical product categories</h1>
        <p className="intro">
          Browse the product catalog by category and open a product page to send
          a detailed inquiry.
        </p>
      </section>

      <section className="filter-panel" aria-label="Product categories">
        {["All", ...categories].map((category) => (
          <button
            className={category === activeCategory ? "chip active" : "chip"}
            key={category}
            type="button"
            onClick={() => setActiveCategory(category)}
          >
            {category}
          </button>
        ))}
      </section>

      <section className="product-grid" aria-label="Products">
        {filteredProducts.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </section>

      {filteredProducts.length === 0 ? (
        <p className="empty-state">No products listed in this category yet.</p>
      ) : null}
    </main>
  );
}
