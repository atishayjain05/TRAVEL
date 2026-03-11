import { useState, useEffect } from 'react';
import api from '../api.js';

function StatCard({ label, value, sub, icon, accent }) {
  return (
    <div
      className="rounded-2xl border p-5 card-hover relative overflow-hidden"
      style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      {/* Subtle glow */}
      <div
        className="absolute top-0 right-0 w-20 h-20 rounded-full opacity-10 blur-2xl"
        style={{ background: accent || 'var(--accent)', transform: 'translate(30%, -30%)' }}
      />
      <div className="flex items-start justify-between mb-4">
        <div
          className="flex items-center justify-center rounded-xl text-xl"
          style={{ width: 44, height: 44, background: 'var(--bg-deep)', border: '1px solid var(--border)' }}
        >
          {icon}
        </div>
        <div
          className="w-2 h-2 rounded-full"
          style={{ background: accent || 'var(--accent)', boxShadow: `0 0 8px ${accent || 'var(--accent)'}` }}
        />
      </div>
      <div className="font-display font-bold text-3xl leading-none mb-1" style={{ color: 'var(--text-primary)' }}>
        {value}
      </div>
      <div className="font-display font-medium text-sm" style={{ color: 'var(--text-secondary)' }}>{label}</div>
      {sub && <div className="font-mono text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{sub}</div>}
    </div>
  );
}

function ScanHistoryRow({ scan }) {
  const statusColor = {
    completed: 'var(--success)',
    running: 'var(--accent)',
    failed: 'var(--danger)',
    pending: 'var(--warning)',
  }[scan.status] || 'var(--text-muted)';

  return (
    <div
      className="flex items-center gap-4 px-4 py-3 rounded-xl border transition-colors"
      style={{ background: 'var(--bg-deep)', borderColor: 'var(--border)' }}
    >
      <div
        className="w-2 h-2 rounded-full shrink-0"
        style={{ background: statusColor, boxShadow: `0 0 6px ${statusColor}` }}
      />
      <div className="flex-1 min-w-0">
        <div className="font-display font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
          {scan.city}
          {scan.food_category && (
            <span className="font-mono font-normal text-xs ml-2" style={{ color: 'var(--text-muted)' }}>
              • {scan.food_category}
            </span>
          )}
        </div>
        <div className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
          {new Date(scan.created_at).toLocaleString()}
        </div>
      </div>
      <div className="text-right shrink-0">
        <div className="font-display font-bold text-sm" style={{ color: 'var(--accent)' }}>
          {scan.restaurants_found}
        </div>
        <div className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>found</div>
      </div>
      <div
        className="font-mono text-xs px-2 py-1 rounded-lg capitalize"
        style={{ background: 'var(--bg-panel)', color: statusColor, border: `1px solid ${statusColor}33` }}
      >
        {scan.status}
      </div>
    </div>
  );
}

export default function Dashboard({ navigate }) {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [s, h] = await Promise.all([
          api.getStats(),
          api.getScanHistory({ limit: 6 }),
        ]);
        setStats(s);
        setHistory(h.items || []);
      } catch (e) {
        console.error('Dashboard load error:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" style={{ color: 'var(--text-muted)' }}>
        <svg className="animate-spin-slow" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        </svg>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-float-up">
      {/* Header */}
      <div>
        <h2 className="font-display font-bold text-2xl mb-1" style={{ color: 'var(--text-primary)' }}>
          Welcome back
          <span className="font-serif italic ml-2" style={{ color: 'var(--accent)', fontWeight: 400 }}>
            Scout
          </span>
        </h2>
        <p className="font-mono text-sm" style={{ color: 'var(--text-muted)' }}>
          Here's your restaurant intelligence overview
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="Total Restaurants"
          value={(stats?.total_restaurants || 0).toLocaleString()}
          icon="🍽️"
          accent="var(--accent)"
        />
        <StatCard
          label="Cities Scanned"
          value={stats?.cities_scanned || 0}
          icon="🗺️"
          accent="#69e8f0"
        />
        <StatCard
          label="Avg. Rating"
          value={stats?.average_rating ? `${stats.average_rating}★` : '—'}
          sub="Google Reviews"
          icon="⭐"
          accent="#f4a261"
        />
        <StatCard
          label="Sources Analyzed"
          value={(stats?.sources_analyzed || 0).toLocaleString()}
          icon="📡"
          accent="#d880d8"
        />
      </div>

      {/* Source Breakdown + CTA */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Breakdown */}
        <div
          className="lg:col-span-2 rounded-2xl border p-5"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
        >
          <h3 className="font-display font-semibold text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            Source Breakdown
          </h3>
          {stats?.source_breakdown && Object.keys(stats.source_breakdown).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(stats.source_breakdown).map(([source, count]) => {
                const total = stats.sources_analyzed || 1;
                const pct = Math.round((count / total) * 100);
                const colors = {
                  youtube: '#ff6b6b',
                  instagram: '#d880d8',
                  tiktok: '#69e8f0',
                  blog: 'var(--accent)',
                  blogs: 'var(--accent)',
                };
                return (
                  <div key={source}>
                    <div className="flex justify-between mb-1.5">
                      <span className={`tag tag-${source}`}>{source}</span>
                      <span className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="rounded-full overflow-hidden" style={{ height: 4, background: 'var(--bg-deep)' }}>
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${pct}%`, background: colors[source] || 'var(--accent)' }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="font-mono text-sm" style={{ color: 'var(--text-muted)' }}>
              No data yet — run your first scan!
            </p>
          )}
        </div>

        {/* Quick Actions */}
        <div
          className="rounded-2xl border p-5 flex flex-col justify-between"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
        >
          <div>
            <h3 className="font-display font-semibold text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
              Quick Actions
            </h3>
            <p className="font-mono text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
              Discover restaurants in any city automatically with AI
            </p>
          </div>
          <div className="space-y-2">
            <button
              onClick={() => navigate('scan')}
              className="w-full py-3 rounded-xl font-display font-bold text-sm transition-all"
              style={{ background: 'var(--accent)', color: '#0c0f0a' }}
            >
              ⚡ New Scan
            </button>
            <button
              onClick={() => navigate('restaurants')}
              className="w-full py-3 rounded-xl font-display font-semibold text-sm transition-all border"
              style={{ background: 'transparent', color: 'var(--text-secondary)', borderColor: 'var(--border)' }}
            >
              View All Restaurants
            </button>
          </div>
        </div>
      </div>

      {/* Recent Scans */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-sm" style={{ color: 'var(--text-secondary)' }}>
            Recent Scans
          </h3>
          <button
            onClick={() => navigate('scan')}
            className="font-mono text-xs hover:underline"
            style={{ color: 'var(--accent)' }}
          >
            + New scan
          </button>
        </div>
        {history.length === 0 ? (
          <div
            className="rounded-xl border p-8 text-center"
            style={{ borderColor: 'var(--border)', borderStyle: 'dashed' }}
          >
            <div className="text-3xl mb-2">🔍</div>
            <p className="font-display font-semibold" style={{ color: 'var(--text-secondary)' }}>
              No scans yet
            </p>
            <p className="font-mono text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
              Start scanning cities to build your restaurant database
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {history.map((scan) => <ScanHistoryRow key={scan.id} scan={scan} />)}
          </div>
        )}
      </div>
    </div>
  );
}
