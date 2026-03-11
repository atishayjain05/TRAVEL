import { useState } from 'react';

const SOURCES = [
  { id: 'youtube', label: 'YouTube', icon: '▶', color: '#ff6b6b' },
  { id: 'instagram', label: 'Instagram', icon: '◈', color: '#d880d8' },
  { id: 'tiktok', label: 'TikTok', icon: '♪', color: '#69e8f0' },
  { id: 'blogs', label: 'Blogs', icon: '◇', color: 'var(--accent)' },
];

const FOOD_CATEGORIES = [
  '', 'Street Food', 'Fine Dining', 'Seafood', 'Vegetarian', 'BBQ & Grill',
  'Noodles & Ramen', 'Pizza & Italian', 'Asian Fusion', 'Local Cuisine', 'Desserts & Cafes',
];

export default function ScanForm({ onSubmit, loading }) {
  const [city, setCity] = useState('');
  const [foodCategory, setFoodCategory] = useState('');
  const [numSources, setNumSources] = useState(20);
  const [selectedSources, setSelectedSources] = useState(['youtube', 'blogs']);

  const toggleSource = (id) => {
    setSelectedSources((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!city.trim()) return;
    if (selectedSources.length === 0) return;
    onSubmit({
      city: city.trim(),
      food_category: foodCategory,
      sources: selectedSources,
      num_sources: numSources,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {/* City */}
      <div>
        <label className="block font-display font-semibold text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
          City Name <span style={{ color: 'var(--accent)' }}>*</span>
        </label>
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="e.g. Bangkok, Singapore, New York..."
          required
          className="w-full px-4 py-3 rounded-xl font-mono text-sm outline-none transition-all"
          style={{
            background: 'var(--bg-deep)',
            border: '1px solid var(--border)',
            color: 'var(--text-primary)',
          }}
          onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--accent-muted)')}
          onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--border)')}
        />
      </div>

      {/* Food Category */}
      <div>
        <label className="block font-display font-semibold text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
          Food Category
        </label>
        <select
          value={foodCategory}
          onChange={(e) => setFoodCategory(e.target.value)}
          className="w-full px-4 py-3 rounded-xl font-mono text-sm outline-none transition-all appearance-none cursor-pointer"
          style={{
            background: 'var(--bg-deep)',
            border: '1px solid var(--border)',
            color: foodCategory ? 'var(--text-primary)' : 'var(--text-muted)',
          }}
        >
          <option value="">All food types</option>
          {FOOD_CATEGORIES.slice(1).map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Number of sources */}
      <div>
        <label className="block font-display font-semibold text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
          Sources to Scan
          <span className="font-mono font-normal ml-2" style={{ color: 'var(--accent)' }}>{numSources}</span>
        </label>
        <input
          type="range"
          min={5}
          max={200}
          step={5}
          value={numSources}
          onChange={(e) => setNumSources(Number(e.target.value))}
          className="w-full cursor-pointer"
          style={{ accentColor: 'var(--accent)' }}
        />
        <div className="flex justify-between font-mono text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
          <span>5 (fast)</span>
          <span>200 (thorough)</span>
        </div>
      </div>

      {/* Sources selector */}
      <div>
        <label className="block font-display font-semibold text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
          Discovery Sources
        </label>
        <div className="grid grid-cols-2 gap-3">
          {SOURCES.map((source) => {
            const active = selectedSources.includes(source.id);
            return (
              <button
                key={source.id}
                type="button"
                onClick={() => toggleSource(source.id)}
                className="flex items-center gap-3 px-4 py-3 rounded-xl border transition-all text-left"
                style={{
                  background: active ? 'rgba(168,224,99,0.06)' : 'var(--bg-deep)',
                  borderColor: active ? 'var(--accent-muted)' : 'var(--border)',
                  color: active ? source.color : 'var(--text-muted)',
                }}
              >
                <span className="text-lg">{source.icon}</span>
                <div>
                  <div className="font-display font-semibold text-sm">{source.label}</div>
                </div>
                {active && (
                  <span className="ml-auto" style={{ color: 'var(--accent)' }}>✓</span>
                )}
              </button>
            );
          })}
        </div>
        {selectedSources.length === 0 && (
          <p className="font-mono text-xs mt-2" style={{ color: 'var(--danger)' }}>
            Select at least one source
          </p>
        )}
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading || !city.trim() || selectedSources.length === 0}
        className="w-full py-4 rounded-xl font-display font-bold text-base transition-all relative overflow-hidden"
        style={{
          background: loading ? 'var(--bg-card)' : 'var(--accent)',
          color: loading ? 'var(--text-muted)' : '#0c0f0a',
          cursor: loading ? 'not-allowed' : 'pointer',
          border: '1px solid var(--border)',
        }}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin-slow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
            Scanning...
          </span>
        ) : (
          '⚡ Start Discovery Scan'
        )}
      </button>
    </form>
  );
}
