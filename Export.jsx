import { useState } from 'react';
import api from '../api.js';

function ExportCard({ title, desc, icon, children }) {
  return (
    <div
      className="rounded-2xl border p-6 card-hover"
      style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <div className="flex items-center gap-4 mb-5">
        <div
          className="flex items-center justify-center rounded-xl text-2xl"
          style={{ width: 52, height: 52, background: 'var(--bg-deep)', border: '1px solid var(--border)' }}
        >
          {icon}
        </div>
        <div>
          <h3 className="font-display font-bold text-lg" style={{ color: 'var(--text-primary)' }}>{title}</h3>
          <p className="font-mono text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{desc}</p>
        </div>
      </div>
      {children}
    </div>
  );
}

const inputStyle = {
  background: 'var(--bg-deep)',
  border: '1px solid var(--border)',
  color: 'var(--text-primary)',
  borderRadius: 10,
  padding: '10px 14px',
  fontSize: 13,
  fontFamily: "'DM Mono', monospace",
  outline: 'none',
  width: '100%',
};

export default function Export() {
  // CSV
  const [csvCity, setCsvCity] = useState('');
  const [csvMinConf, setCsvMinConf] = useState('');
  const [csvLoading, setCsvLoading] = useState(false);
  const [csvSuccess, setCsvSuccess] = useState(false);

  // Sheets
  const [sheetsCity, setSheetsCity] = useState('');
  const [sheetsName, setSheetsName] = useState('FoodScout AI Export');
  const [sheetsLoading, setSheetsLoading] = useState(false);
  const [sheetsResult, setSheetsResult] = useState(null);
  const [sheetsError, setSheetsError] = useState(null);

  const handleCsvExport = async () => {
    setCsvLoading(true);
    setCsvSuccess(false);
    try {
      await api.downloadCsv({
        city: csvCity || undefined,
        min_confidence: csvMinConf || undefined,
      });
      setCsvSuccess(true);
    } catch (e) {
      alert('Export failed: ' + e.message);
    } finally {
      setCsvLoading(false);
    }
  };

  const handleSheetsExport = async () => {
    setSheetsLoading(true);
    setSheetsResult(null);
    setSheetsError(null);
    try {
      const res = await api.exportToSheets({
        city: sheetsCity || null,
        spreadsheet_name: sheetsName,
      });
      setSheetsResult(res);
    } catch (e) {
      setSheetsError(e.message);
    } finally {
      setSheetsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto animate-float-up">
      {/* Header */}
      <div className="mb-8">
        <h2 className="font-display font-bold text-2xl mb-1" style={{ color: 'var(--text-primary)' }}>
          Export Data
        </h2>
        <p className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
          Download or sync your restaurant data
        </p>
      </div>

      <div className="space-y-5">
        {/* CSV Export */}
        <ExportCard
          title="Download CSV"
          desc="Export restaurants as a CSV file for Excel, Sheets, or any tool"
          icon="📄"
        >
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label className="block font-mono text-xs mb-1.5" style={{ color: 'var(--text-muted)' }}>
                Filter by city
              </label>
              <input
                type="text"
                value={csvCity}
                onChange={(e) => setCsvCity(e.target.value)}
                placeholder="All cities"
                style={inputStyle}
              />
            </div>
            <div>
              <label className="block font-mono text-xs mb-1.5" style={{ color: 'var(--text-muted)' }}>
                Min. confidence score
              </label>
              <select
                value={csvMinConf}
                onChange={(e) => setCsvMinConf(e.target.value)}
                style={{ ...inputStyle, cursor: 'pointer' }}
              >
                <option value="">All restaurants</option>
                <option value="30">30+ confidence</option>
                <option value="50">50+ confidence</option>
                <option value="70">70+ confidence</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleCsvExport}
            disabled={csvLoading}
            className="w-full py-3 rounded-xl font-display font-bold text-sm transition-all flex items-center justify-center gap-2"
            style={{
              background: csvLoading ? 'var(--bg-deep)' : 'var(--accent)',
              color: csvLoading ? 'var(--text-muted)' : '#0c0f0a',
              border: '1px solid var(--border)',
              cursor: csvLoading ? 'not-allowed' : 'pointer',
            }}
          >
            {csvLoading ? (
              <>
                <svg className="animate-spin-slow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                </svg>
                Generating CSV...
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                Download CSV
              </>
            )}
          </button>

          {csvSuccess && (
            <p className="font-mono text-xs mt-3 text-center" style={{ color: 'var(--success)' }}>
              ✓ CSV downloaded successfully
            </p>
          )}
        </ExportCard>

        {/* Google Sheets Export */}
        <ExportCard
          title="Export to Google Sheets"
          desc="Create a live Google Spreadsheet with all restaurant data"
          icon="📊"
        >
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label className="block font-mono text-xs mb-1.5" style={{ color: 'var(--text-muted)' }}>
                Filter by city (optional)
              </label>
              <input
                type="text"
                value={sheetsCity}
                onChange={(e) => setSheetsCity(e.target.value)}
                placeholder="All cities"
                style={inputStyle}
              />
            </div>
            <div>
              <label className="block font-mono text-xs mb-1.5" style={{ color: 'var(--text-muted)' }}>
                Spreadsheet name
              </label>
              <input
                type="text"
                value={sheetsName}
                onChange={(e) => setSheetsName(e.target.value)}
                style={inputStyle}
              />
            </div>
          </div>

          {/* Credentials warning */}
          <div
            className="flex items-start gap-3 p-3 rounded-xl mb-4"
            style={{ background: 'rgba(244,162,97,0.08)', border: '1px solid rgba(244,162,97,0.2)' }}
          >
            <span style={{ color: 'var(--accent-warm)', fontSize: 16, flexShrink: 0 }}>⚠</span>
            <div>
              <p className="font-display font-semibold text-xs mb-0.5" style={{ color: 'var(--accent-warm)' }}>
                Requires Service Account
              </p>
              <p className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
                Set <code style={{ color: 'var(--text-secondary)' }}>GOOGLE_SHEETS_CREDENTIALS_FILE</code> in your .env
                with a Google Service Account JSON key file.
              </p>
            </div>
          </div>

          <button
            onClick={handleSheetsExport}
            disabled={sheetsLoading}
            className="w-full py-3 rounded-xl font-display font-bold text-sm transition-all flex items-center justify-center gap-2"
            style={{
              background: sheetsLoading ? 'var(--bg-deep)' : 'var(--bg-card)',
              color: sheetsLoading ? 'var(--text-muted)' : 'var(--text-primary)',
              border: '1px solid var(--border)',
              cursor: sheetsLoading ? 'not-allowed' : 'pointer',
            }}
          >
            {sheetsLoading ? (
              <>
                <svg className="animate-spin-slow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                </svg>
                Exporting...
              </>
            ) : '→ Export to Google Sheets'}
          </button>

          {sheetsResult && (
            <div className="mt-3 p-3 rounded-xl" style={{ background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.2)' }}>
              <p className="font-mono text-xs mb-1" style={{ color: 'var(--success)' }}>
                ✓ {sheetsResult.rows_exported} restaurants exported
              </p>
              <a
                href={sheetsResult.spreadsheet_url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-mono text-xs hover:underline"
                style={{ color: 'var(--accent)' }}
              >
                Open Spreadsheet ↗
              </a>
            </div>
          )}
          {sheetsError && (
            <p className="font-mono text-xs mt-3" style={{ color: 'var(--danger)' }}>
              ✗ {sheetsError}
            </p>
          )}
        </ExportCard>

        {/* Data columns info */}
        <div
          className="rounded-2xl border p-5"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
        >
          <h4 className="font-display font-semibold text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
            Exported Columns
          </h4>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
            {[
              'Name', 'City', 'Area', 'Google Rating', 'Review Count',
              'Speciality', 'Source Type', 'Source URL', 'YouTube Channel',
              'Google Maps Link', 'Confidence Score', 'Discovered At',
            ].map((col) => (
              <div key={col} className="flex items-center gap-2">
                <span style={{ color: 'var(--accent)', fontSize: 10 }}>◆</span>
                <span className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>{col}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
