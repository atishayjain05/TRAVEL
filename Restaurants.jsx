import { useState, useEffect, useCallback } from 'react';
import RestaurantTable from '../components/RestaurantTable.jsx';
import api from '../api.js';

const SORT_OPTIONS = [
  { value: 'confidence_score', label: 'Confidence' },
  { value: 'google_rating', label: 'Rating' },
  { value: 'review_count', label: 'Reviews' },
  { value: 'name', label: 'Name' },
  { value: 'created_at', label: 'Date Added' },
];

const SOURCE_OPTIONS = ['', 'youtube', 'instagram', 'tiktok', 'blog'];

export default function Restaurants() {
  const [restaurants, setRestaurants] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const limit = 50;

  // Filters
  const [search, setSearch] = useState('');
  const [city, setCity] = useState('');
  const [sourceType, setSourceType] = useState('');
  const [minRating, setMinRating] = useState('');
  const [minConfidence, setMinConfidence] = useState('');
  const [sortBy, setSortBy] = useState('confidence_score');
  const [sortDir, setSortDir] = useState('desc');

  const fetchRestaurants = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        limit,
        offset: page * limit,
        sort_by: sortBy,
        sort_dir: sortDir,
      };
      if (search) params.search = search;
      if (city) params.city = city;
      if (sourceType) params.source_type = sourceType;
      if (minRating) params.min_rating = minRating;
      if (minConfidence) params.min_confidence = minConfidence;

      const data = await api.getRestaurants(params);
      setRestaurants(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error('Fetch restaurants error:', e);
    } finally {
      setLoading(false);
    }
  }, [page, search, city, sourceType, minRating, minConfidence, sortBy, sortDir]);

  useEffect(() => {
    const timer = setTimeout(fetchRestaurants, 300);
    return () => clearTimeout(timer);
  }, [fetchRestaurants]);

  // Reset page when filters change
  useEffect(() => { setPage(0); }, [search, city, sourceType, minRating, minConfidence]);

  const handleDelete = async (id) => {
    if (!confirm('Delete this restaurant?')) return;
    try {
      await api.deleteRestaurant(id);
      fetchRestaurants();
    } catch (e) {
      alert('Delete failed: ' + e.message);
    }
  };

  const totalPages = Math.ceil(total / limit);

  const inputStyle = {
    background: 'var(--bg-deep)',
    border: '1px solid var(--border)',
    color: 'var(--text-primary)',
    borderRadius: 10,
    padding: '8px 12px',
    fontSize: 13,
    fontFamily: "'DM Mono', monospace",
    outline: 'none',
  };

  return (
    <div className="max-w-7xl mx-auto animate-float-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl mb-1" style={{ color: 'var(--text-primary)' }}>
            Restaurants
            <span className="font-mono font-normal text-base ml-3" style={{ color: 'var(--text-muted)' }}>
              {total.toLocaleString()} total
            </span>
          </h2>
          <p className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
            All discovered restaurants across all cities
          </p>
        </div>
        <button
          onClick={() => api.downloadCsv({ city: city || undefined })}
          className="flex items-center gap-2 px-4 py-2 rounded-xl font-display font-semibold text-sm border transition-all"
          style={{ background: 'transparent', color: 'var(--accent)', borderColor: 'var(--accent-muted)' }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div
        className="rounded-2xl border p-4 mb-5 grid gap-3"
        style={{
          background: 'var(--bg-card)',
          borderColor: 'var(--border)',
          gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
        }}
      >
        {/* Search */}
        <div className="col-span-full lg:col-span-2">
          <input
            type="text"
            placeholder="Search restaurants, specialities..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ ...inputStyle, width: '100%' }}
          />
        </div>

        {/* City */}
        <input
          type="text"
          placeholder="Filter by city"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          style={inputStyle}
        />

        {/* Source */}
        <select
          value={sourceType}
          onChange={(e) => setSourceType(e.target.value)}
          style={{ ...inputStyle, cursor: 'pointer' }}
        >
          <option value="">All sources</option>
          {SOURCE_OPTIONS.slice(1).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        {/* Min rating */}
        <select
          value={minRating}
          onChange={(e) => setMinRating(e.target.value)}
          style={{ ...inputStyle, cursor: 'pointer' }}
        >
          <option value="">Any rating</option>
          {[3, 3.5, 4, 4.5].map((r) => (
            <option key={r} value={r}>{r}★ and above</option>
          ))}
        </select>

        {/* Min confidence */}
        <select
          value={minConfidence}
          onChange={(e) => setMinConfidence(e.target.value)}
          style={{ ...inputStyle, cursor: 'pointer' }}
        >
          <option value="">Any confidence</option>
          <option value="30">30+ (Low)</option>
          <option value="50">50+ (Medium)</option>
          <option value="70">70+ (High)</option>
          <option value="90">90+ (Very High)</option>
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{ ...inputStyle, cursor: 'pointer' }}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>Sort: {o.label}</option>
          ))}
        </select>

        <button
          onClick={() => setSortDir((d) => d === 'desc' ? 'asc' : 'desc')}
          className="flex items-center justify-center gap-2 rounded-xl transition-all"
          style={{ ...inputStyle, cursor: 'pointer', color: 'var(--text-secondary)' }}
        >
          {sortDir === 'desc' ? '↓ Desc' : '↑ Asc'}
        </button>
      </div>

      {/* Table */}
      <RestaurantTable
        restaurants={restaurants}
        loading={loading}
        onDelete={handleDelete}
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-5">
          <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
            Page {page + 1} of {totalPages} ({total.toLocaleString()} results)
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1.5 rounded-lg font-mono text-xs border transition-all"
              style={{
                background: 'var(--bg-card)',
                borderColor: 'var(--border)',
                color: page === 0 ? 'var(--text-muted)' : 'var(--text-secondary)',
                cursor: page === 0 ? 'not-allowed' : 'pointer',
              }}
            >
              ← Prev
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const p = Math.max(0, Math.min(page - 2, totalPages - 5)) + i;
              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className="px-3 py-1.5 rounded-lg font-mono text-xs border transition-all"
                  style={{
                    background: p === page ? 'var(--accent)' : 'var(--bg-card)',
                    borderColor: p === page ? 'var(--accent)' : 'var(--border)',
                    color: p === page ? '#0c0f0a' : 'var(--text-secondary)',
                    cursor: 'pointer',
                  }}
                >
                  {p + 1}
                </button>
              );
            })}
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1.5 rounded-lg font-mono text-xs border transition-all"
              style={{
                background: 'var(--bg-card)',
                borderColor: 'var(--border)',
                color: page >= totalPages - 1 ? 'var(--text-muted)' : 'var(--text-secondary)',
                cursor: page >= totalPages - 1 ? 'not-allowed' : 'pointer',
              }}
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
