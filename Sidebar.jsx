const NAV_ITEMS = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </svg>
    ),
  },
  {
    id: 'scan',
    label: 'Scan City',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </svg>
    ),
    badge: 'NEW',
  },
  {
    id: 'restaurants',
    label: 'Restaurants',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 11l19-9-9 19-2-8-8-2z" />
      </svg>
    ),
  },
  {
    id: 'export',
    label: 'Export',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="15" x2="12" y2="3" />
      </svg>
    ),
  },
];

export default function Sidebar({ currentPage, navigate, open, setOpen }) {
  if (!open) return null;

  return (
    <aside
      className="flex flex-col shrink-0 border-r h-full"
      style={{
        width: 220,
        background: 'var(--bg-panel)',
        borderColor: 'var(--border)',
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b" style={{ borderColor: 'var(--border)' }}>
        <div
          className="flex items-center justify-center rounded-lg"
          style={{ width: 32, height: 32, background: 'var(--accent)', flexShrink: 0 }}
        >
          <span style={{ fontSize: 16 }}>🍜</span>
        </div>
        <div>
          <div className="font-display font-bold text-sm leading-none" style={{ color: 'var(--text-primary)' }}>
            FoodScout
          </div>
          <div className="font-mono text-xs mt-0.5" style={{ color: 'var(--accent)' }}>
            AI
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 p-3 flex-1">
        <div className="px-2 pb-2 pt-1">
          <span className="font-mono uppercase text-xs tracking-widest" style={{ color: 'var(--text-muted)' }}>
            Navigation
          </span>
        </div>
        {NAV_ITEMS.map((item) => {
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => navigate(item.id)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg w-full text-left transition-all relative"
              style={{
                background: active ? 'var(--bg-card)' : 'transparent',
                color: active ? 'var(--accent)' : 'var(--text-secondary)',
                border: active ? '1px solid var(--border)' : '1px solid transparent',
              }}
              onMouseOver={(e) => {
                if (!active) e.currentTarget.style.background = 'rgba(168,224,99,0.04)';
              }}
              onMouseOut={(e) => {
                if (!active) e.currentTarget.style.background = 'transparent';
              }}
            >
              {active && (
                <span
                  className="absolute left-0 top-1/2 -translate-y-1/2 rounded-r-full"
                  style={{ width: 3, height: 20, background: 'var(--accent)' }}
                />
              )}
              <span>{item.icon}</span>
              <span className="font-display font-medium text-sm flex-1">{item.label}</span>
              {item.badge && (
                <span
                  className="font-mono text-xs px-1.5 py-0.5 rounded"
                  style={{ background: 'rgba(168,224,99,0.15)', color: 'var(--accent)', fontSize: 9, letterSpacing: '0.08em' }}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-2">
          <div
            className="w-2 h-2 rounded-full"
            style={{ background: 'var(--success)', boxShadow: '0 0 6px rgba(74,222,128,0.5)' }}
          />
          <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
            System online
          </span>
        </div>
        <div className="font-mono text-xs mt-1" style={{ color: 'var(--text-muted)', opacity: 0.6 }}>
          v1.0.0
        </div>
      </div>
    </aside>
  );
}
