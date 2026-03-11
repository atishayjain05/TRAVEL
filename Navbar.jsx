export default function Navbar({ currentPage, navigate, toggleSidebar }) {
  const titles = {
    dashboard: 'Dashboard',
    scan: 'Scan City',
    restaurants: 'Restaurants',
    export: 'Export Data',
  };

  return (
    <header
      className="flex items-center justify-between px-6 py-4 border-b"
      style={{
        borderColor: 'var(--border)',
        background: 'var(--bg-panel)',
        minHeight: 64,
      }}
    >
      {/* Left: toggle + title */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg transition-colors"
          style={{ color: 'var(--text-secondary)' }}
          onMouseOver={(e) => (e.currentTarget.style.background = 'var(--bg-card)')}
          onMouseOut={(e) => (e.currentTarget.style.background = 'transparent')}
          title="Toggle sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <div>
          <h1 className="font-display font-bold text-lg leading-none" style={{ color: 'var(--text-primary)' }}>
            {titles[currentPage] || 'FoodScout AI'}
          </h1>
          <p className="text-xs mt-0.5 font-mono" style={{ color: 'var(--text-muted)' }}>
            AI-powered restaurant discovery
          </p>
        </div>
      </div>

      {/* Right: CTA */}
      <button
        onClick={() => navigate('scan')}
        className="flex items-center gap-2 px-4 py-2 rounded-lg font-display font-semibold text-sm transition-all"
        style={{
          background: 'var(--accent)',
          color: '#0c0f0a',
        }}
        onMouseOver={(e) => (e.currentTarget.style.opacity = '0.85')}
        onMouseOut={(e) => (e.currentTarget.style.opacity = '1')}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        Scan City
      </button>
    </header>
  );
}
