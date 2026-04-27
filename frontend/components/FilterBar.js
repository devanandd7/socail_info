export default function FilterBar({ filters, setFilters, onRefresh, loading }) {
  return (
    <section className="filter-bar">
      <select
        value={filters.platform}
        onChange={(e) => setFilters((f) => ({ ...f, platform: e.target.value }))}
      >
        <option value="">All platforms</option>
        <option value="twitter">X</option>
        <option value="reddit">Reddit</option>
      </select>

      <input
        placeholder="Keyword"
        value={filters.keyword}
        onChange={(e) => setFilters((f) => ({ ...f, keyword: e.target.value }))}
      />

      <select
        value={filters.ai_category}
        onChange={(e) => setFilters((f) => ({ ...f, ai_category: e.target.value }))}
      >
        <option value="">Any category</option>
        <option value="Product Launch">Product Launch</option>
        <option value="Funding News">Funding News</option>
        <option value="Important Update">Important Update</option>
        <option value="Noise">Noise</option>
      </select>

      <label className="toggle">
        <input
          type="checkbox"
          checked={filters.use_ai}
          onChange={(e) => setFilters((f) => ({ ...f, use_ai: e.target.checked }))}
        />
        AI filtering
      </label>

      <button onClick={onRefresh} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh feed"}
      </button>
    </section>
  );
}
