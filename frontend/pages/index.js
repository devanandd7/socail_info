import { useCallback, useEffect, useState } from "react";

import FilterBar from "../components/FilterBar";
import Layout from "../components/Layout";
import PostCard from "../components/PostCard";
import { fetchFiltered, fetchTrending, triggerCollect } from "../utils/api";

const DEFAULT_FILTERS = {
  platform: "",
  keyword: "",
  ai_category: "",
  use_ai: true,
  min_engagement: 10,
};

export default function HomePage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [posts, setPosts] = useState([]);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const [data, trendData] = await Promise.all([
        fetchFiltered({
          ...filters,
          min_engagement: String(filters.min_engagement),
          use_ai: String(filters.use_ai),
        }),
        fetchTrending(8),
      ]);
      setPosts(data);
      setTrending(trendData.items || []);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e.message || "Failed to load feed");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const id = setInterval(() => {
      load();
    }, 30000);
    return () => clearInterval(id);
  }, [load]);

  async function collectAndRefresh() {
    try {
      setLoading(true);
      setError("");
      await triggerCollect();
      await load();
    } catch (e) {
      setError(e.message || "Failed to trigger collection");
      setLoading(false);
    }
  }

  function applyTrending(term) {
    setFilters((f) => ({ ...f, keyword: term.replace(/^#/, "") }));
  }

  return (
    <Layout title="SignalFeed">
      <FilterBar filters={filters} setFilters={setFilters} onRefresh={collectAndRefresh} loading={loading} />

      <section className="trending-panel">
        <div className="section-head">
          <h2>Trending</h2>
          <span>{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : "Live"}</span>
        </div>
        <div className="trend-chips">
          {trending.length ? trending.map((item) => (
            <button type="button" key={item.name} className="trend-chip" onClick={() => applyTrending(item.name)}>
              {item.name}
              <span>{item.score}</span>
            </button>
          )) : <span className="empty">No trend data yet.</span>}
        </div>
      </section>

      {error ? <p className="error">{error}</p> : null}

      <section className="feed-grid">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </section>

      {!loading && posts.length === 0 ? <p className="empty">No posts matched your filters.</p> : null}
    </Layout>
  );
}
