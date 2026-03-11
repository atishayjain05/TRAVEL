import { useState } from 'react';

function StarRating({ rating }) {
  if (!rating) return <span style={{ color: 'var(--text-muted)' }}>—</span>;
  const stars = Math.round(rating);
  return (
    <span className="flex items-center gap-1">
      <span style={{ color: '#f4a261' }}>{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
      <span className="font-mono text-xs ml-1" style={{ color: 'var(--text-secondary)' }}>{rating.toFixed(1)}</span>
    </span>
  );
}

function SourceTag({ type }) {
  return <span className={`tag tag-${type || 'unknown'}`}>{type || 'unknown'}</span>;
}

function ConfidenceBadge({ score }) {
  const color = score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--accent-warm)' : 'var(--text-muted)';
  return (
    <div className="flex items-center gap-2">
      <div
        className="rounded-full"
        style={{ width: 6, height: 6, background: color, flexShrink: 0, boxShadow: `0 0 6px ${color}` }}
      />
      <span className="font-mono text-xs font-medium" style={{ color }}>
        {score}
      </span>
    </div>
  );
}

export default function RestaurantTable({ restaurants, loading, onDelete }) {
  const [sortKey, setSortKey] = useState('confidence_score');
  const [sortDir, setSortDir] = useState('desc');

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'desc' ? 'asc' : 'desc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <span style={{ opacity: 0.2 }}>↕</span>;
    return <span style={{ color: 'var(--accent)' }}>{sortDir === 'desc' ? '↓' : '↑'}</span>;
  };

  const thStyle = {
    padding: '10px 14px',
    textAlign: 'left',
    fontSize: 11,
    fontFamily: "'DM Mono', monospace",
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    color: 'var(--text-muted)',
    borderBottom: '1px solid var(--border)',
    whiteSpace: 'nowrap',
    cursor: 'pointer',
    userSelect: 'none',
  };

  const tdStyle = {
    padding: '12px 14px',
    borderBottom: '1px solid rgba(42,53,38,0.5)',
    verticalAlign: 'middle',
    fontSize: 13,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20" style={{ color: 'var(--text-muted)' }}>
        <div className="text-center">
          <svg className="animate-spin-slow mx-auto mb-3" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          <p className="font-mono text-sm">Loading restaurants...</p>
        </div>
      </div>
    );
  }

  if (!restaurants || restaurants.length === 0) {
    return (
      <div className="flex items-center justify-center py-20" style={{ color: 'var(--text-muted)' }}>
        <div className="text-center">
          <div className="text-5xl mb-4">🍽️</div>
          <p className="font-display font-semibold text-lg mb-1" style={{ color: 'var(--text-secondary)' }}>
            No restaurants found
          </p>
          <p className="font-mono text-sm">Run a city scan to discover restaurants</p>
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border" style={{ borderColor: 'var(--border)' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 900 }}>
        <thead style={{ background: 'var(--bg-panel)' }}>
          <tr>
            {[
              { key: 'name', label: 'Restaurant' },
              { key: 'city', label: 'City / Area' },
              { key: 'google_rating', label: 'Rating' },
              { key: null, label: 'Speciality' },
              { key: 'source_type', label: 'Source' },
              { key: null, label: 'Maps' },
              { key: 'confidence_score', label: 'Confidence' },
              { key: null, label: '' },
            ].map(({ key, label }) => (
              <th
                key={label}
                style={thStyle}
                onClick={() => key && handleSort(key)}
              >
                {label} {key && <SortIcon col={key} />}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {restaurants.map((r, i) => (
            <tr
              key={r.id || i}
              style={{ background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)' }}
              onMouseOver={(e) => (e.currentTarget.style.background = 'var(--bg-card)')}
              onMouseOut={(e) => (e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)')}
            >
              <td style={tdStyle}>
                <div className="font-display font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {r.name}
                </div>
                {r.source_url && (
                  <a
                    href={r.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-mono text-xs hover:underline"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    View source ↗
                  </a>
                )}
              </td>
              <td style={tdStyle}>
                <div className="font-mono text-sm" style={{ color: 'var(--text-primary)' }}>{r.city}</div>
                {r.area && (
                  <div className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>{r.area}</div>
                )}
              </td>
              <td style={tdStyle}>
                <StarRating rating={r.google_rating} />
                {r.review_count > 0 && (
                  <div className="font-mono text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {r.review_count.toLocaleString()} reviews
                  </div>
                )}
              </td>
              <td style={tdStyle}>
                <span className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {r.speciality || '—'}
                </span>
              </td>
              <td style={tdStyle}>
                <SourceTag type={r.source_type} />
                {r.youtube_channel && (
                  <div className="font-mono text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    {r.youtube_channel}
                  </div>
                )}
              </td>
              <td style={tdStyle}>
                {r.google_maps_link ? (
                  <a
                    href={r.google_maps_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 font-mono text-xs hover:underline"
                    style={{ color: 'var(--accent)' }}
                  >
                    Maps ↗
                  </a>
                ) : (
                  <span style={{ color: 'var(--text-muted)' }}>—</span>
                )}
              </td>
              <td style={tdStyle}>
                <ConfidenceBadge score={r.confidence_score || 0} />
              </td>
              <td style={tdStyle}>
                {onDelete && (
                  <button
                    onClick={() => onDelete(r.id)}
                    className="p-1.5 rounded-lg transition-colors"
                    style={{ color: 'var(--text-muted)' }}
                    title="Delete"
                    onMouseOver={(e) => (e.currentTarget.style.color = 'var(--danger)')}
                    onMouseOut={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6l-1 14H6L5 6" />
                      <path d="M10 11v6M14 11v6" />
                    </svg>
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
