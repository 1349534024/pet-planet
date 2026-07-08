import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const runtimeApiBase = window.__PET_PLANET_CONFIG__?.API_BASE_URL || "";
const API_BASE = import.meta.env.VITE_API_BASE_URL || runtimeApiBase;

function useApi(path, fallback) {
  const [data, setData] = useState(fallback);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    let active = true;
    fetch(`${API_BASE}${path}`)
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((json) => {
        if (!active) return;
        setData(json?.data?.items || json?.data || json || fallback);
        setStatus("online");
      })
      .catch(() => {
        if (!active) return;
        setData(fallback);
        setStatus("demo");
      });

    return () => {
      active = false;
    };
  }, [path]);

  return { data, status };
}

const demoPets = [
  { id: 1, name: "Mochi", type: "Cat", city: "Shanghai", note: "Vaccinated and family friendly" },
  { id: 2, name: "Lucky", type: "Dog", city: "Hangzhou", note: "Active, social, ready for adoption" },
  { id: 3, name: "Nana", type: "Rabbit", city: "Suzhou", note: "Calm companion, needs a stable home" },
];

const demoProducts = [
  { id: 1, title: "Complete Cat Food", price_cent: 12900, status: "On sale" },
  { id: 2, title: "Smart Pet Water Fountain", price_cent: 19900, status: "On sale" },
  { id: 3, title: "Portable Travel Carrier", price_cent: 8900, status: "Reviewing" },
];

function normalizeList(value, fallback) {
  if (Array.isArray(value)) return value.length ? value : fallback;
  if (Array.isArray(value?.items)) return value.items.length ? value.items : fallback;
  return fallback;
}

function App() {
  const petsResult = useApi("/api/v1/adoptions?page=1&page_size=3", demoPets);
  const productsResult = useApi("/api/v1/products?page=1&page_size=3", demoProducts);
  const pets = useMemo(() => normalizeList(petsResult.data, demoPets), [petsResult.data]);
  const products = useMemo(() => normalizeList(productsResult.data, demoProducts), [productsResult.data]);

  return (
    <main>
      <section className="hero">
        <nav>
          <div className="brand">
            <span className="brand-mark">P</span>
            Pet Planet
          </div>
          <div className="nav-actions">
            <a href={`${API_BASE}/docs`} target="_blank" rel="noreferrer">Swagger</a>
            <a href={`${API_BASE}/health`} target="_blank" rel="noreferrer">Health</a>
          </div>
        </nav>

        <div className="hero-grid">
          <div>
            <p className="eyebrow">Pet mall - Adoption - Admin audit</p>
            <h1>Pet Planet</h1>
            <p className="subtitle">
              A demo app for pet commerce, adoption, merchant services, admin audit, risk control, messaging, and statistics.
            </p>
            <div className="cta-row">
              <a className="primary" href={`${API_BASE}/docs`} target="_blank" rel="noreferrer">
                Open API Docs <span>-&gt;</span>
              </a>
              <a className="secondary" href={`${API_BASE}/api/v1/admin/statistics/overview`} target="_blank" rel="noreferrer">
                Admin Entry
              </a>
            </div>
          </div>

          <div className="status-panel">
            <div className="status-item"><b>API</b> Backend API <span>{productsResult.status}</span></div>
            <div className="status-item"><b>SKU</b> Products <span>{products.length} items</span></div>
            <div className="status-item"><b>USER</b> Login Entry <span>Auth / Profile / Pets</span></div>
            <div className="status-item"><b>ADMIN</b> Admin Audit <span>RBAC / Risk / Stats</span></div>
          </div>
        </div>
      </section>

      <section className="content">
        <div className="section-title">
          <h2>Pet List</h2>
          <span>{petsResult.status === "online" ? "From backend API" : "Demo data"}</span>
        </div>
        <div className="cards">
          {pets.map((pet) => (
            <article className="card" key={pet.id || pet.name}>
              <p className="tag">{pet.type || pet.pet_type || "Pet"}</p>
              <h3>{pet.name || pet.title || "Adoption Pet"}</h3>
              <p>{pet.city || "Local"} - {pet.note || pet.description || "Waiting for a reliable new home"}</p>
            </article>
          ))}
        </div>

        <div className="section-title">
          <h2>Product List</h2>
          <span>{productsResult.status === "online" ? "From backend API" : "Demo data"}</span>
        </div>
        <div className="cards">
          {products.map((product) => (
            <article className="card" key={product.id || product.title}>
              <p className="tag">{product.status || "Product"}</p>
              <h3>{product.title || product.name}</h3>
              <p>Price: CNY {(((product.price_cent || product.price || 0) / 100) || 0).toFixed(2)}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
