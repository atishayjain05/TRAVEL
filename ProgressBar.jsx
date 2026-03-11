export default function ProgressBar({ value = 0, label = '', step = '' }) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>
          {step || label}
        </span>
        <span className="font-display font-bold text-sm" style={{ color: 'var(--accent)' }}>
          {Math.round(value)}%
        </span>
      </div>
      <div
        className="relative w-full rounded-full overflow-hidden"
        style={{ height: 8, background: 'var(--bg-deep)' }}
      >
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
          style={{
            width: `${value}%`,
            background: value < 100
              ? 'linear-gradient(90deg, var(--accent-muted), var(--accent))'
              : 'var(--success)',
            boxShadow: value > 0 ? '0 0 12px rgba(168,224,99,0.4)' : 'none',
          }}
        />
        {value > 0 && value < 100 && (
          <div
            className="absolute inset-y-0 right-0 w-16 opacity-60"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(168,224,99,0.3), transparent)',
              animation: 'shimmer 1.5s linear infinite',
              backgroundSize: '200% auto',
            }}
          />
        )}
      </div>
    </div>
  );
}
