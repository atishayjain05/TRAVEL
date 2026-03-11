import { useState, useEffect, useRef } from 'react';
import ScanForm from '../components/ScanForm.jsx';
import ProgressBar from '../components/ProgressBar.jsx';
import api from '../api.js';

const PIPELINE_STEPS = [
  { key: 'youtube', label: 'Collecting YouTube content', pct: 15 },
  { key: 'instagram', label: 'Scraping Instagram Reels', pct: 28 },
  { key: 'tiktok', label: 'Analyzing TikTok videos', pct: 40 },
  { key: 'blogs', label: 'Scanning food blogs', pct: 52 },
  { key: 'extract', label: 'Extracting restaurant mentions', pct: 65 },
  { key: 'maps', label: 'Verifying with Google Maps', pct: 78 },
  { key: 'dedupe', label: 'Deduplicating results', pct: 88 },
  { key: 'score', label: 'Calculating confidence scores', pct: 95 },
  { key: 'save', label: 'Saving to database', pct: 100 },
];

export default function ScanCity({ navigate }) {
  const [scanning, setScanning] = useState(false);
  const [scanId, setScanId] = useState(null);
  const [scanStatus, setScanStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [error, setError] = useState(null);
  const [completed, setCompleted] = useState(false);
  const pollRef = useRef(null);
  const stepIndex = useRef(0);

  // Simulate progress animation during scan
  useEffect(() => {
    if (!scanning || completed) return;

    const interval = setInterval(() => {
      setProgress((prev) => {
        const target = PIPELINE_STEPS[Math.min(stepIndex.current, PIPELINE_STEPS.length - 1)]?.pct || 95;
        if (prev < target - 2) {
          return prev + 0.8;
        }
        return prev;
      });

      // Advance step label every ~8s
      stepIndex.current = Math.min(
        Math.floor((Date.now() - stepStartRef.current) / 8000),
        PIPELINE_STEPS.length - 1
      );
      setCurrentStep(PIPELINE_STEPS[stepIndex.current]?.label || '');
    }, 300);

    return () => clearInterval(interval);
  }, [scanning, completed]);

  const stepStartRef = useRef(0);

  // Poll scan status
  useEffect(() => {
    if (!scanId) return;

    pollRef.current = setInterval(async () => {
      try {
        const status = await api.getScanStatus(scanId);
        setScanStatus(status);

        if (status.status === 'completed') {
          setProgress(100);
          setCurrentStep('Scan complete!');
          setCompleted(true);
          setScanning(false);
          clearInterval(pollRef.current);
        } else if (status.status === 'failed') {
          setError(status.error_message || 'Scan failed. Check backend logs.');
          setScanning(false);
          clearInterval(pollRef.current);
        }
      } catch (e) {
        console.error('Poll error:', e);
      }
    }, 3000);

    return () => clearInterval(pollRef.current);
  }, [scanId]);

  const handleSubmit = async (formData) => {
    setError(null);
    setCompleted(false);
    setProgress(0);
    setCurrentStep('Initiating scan...');
    stepIndex.current = 0;
    stepStartRef.current = Date.now();
    setScanning(true);

    try {
      const res = await api.startScan(formData);
      setScanId(res.scan_id);
    } catch (e) {
      setError(e.message);
      setScanning(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto animate-float-up">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div
            className="flex items-center justify-center rounded-xl text-2xl"
            style={{ width: 48, height: 48, background: 'var(--bg-card)', border: '1px solid var(--border)' }}
          >
            🔍
          </div>
          <div>
            <h2 className="font-display font-bold text-2xl" style={{ color: 'var(--text-primary)' }}>
              Scan City
            </h2>
            <p className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
              AI-powered restaurant discovery across social media & blogs
            </p>
          </div>
        </div>
      </div>

      {/* Scan Form Card */}
      <div
        className="rounded-2xl border p-6 mb-6"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        <ScanForm onSubmit={handleSubmit} loading={scanning} />
      </div>

      {/* Progress Panel */}
      {(scanning || completed || error) && (
        <div
          className="rounded-2xl border p-6 animate-float-up"
          style={{
            background: 'var(--bg-card)',
            borderColor: completed ? 'var(--accent-muted)' : error ? 'var(--danger)' : 'var(--border)',
          }}
        >
          <h3 className="font-display font-semibold text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            {error ? '⚠ Scan Error' : completed ? '✓ Scan Complete' : '◉ Scanning in Progress'}
          </h3>

          {error ? (
            <div>
              <p className="font-mono text-sm mb-4" style={{ color: 'var(--danger)' }}>{error}</p>
              <button
                onClick={() => { setError(null); setScanning(false); setScanId(null); }}
                className="font-display font-semibold text-sm px-4 py-2 rounded-lg"
                style={{ background: 'var(--bg-deep)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
              >
                Try Again
              </button>
            </div>
          ) : (
            <>
              <ProgressBar value={progress} step={currentStep} />

              {/* Pipeline steps */}
              <div className="mt-5 space-y-2">
                {PIPELINE_STEPS.map((step, i) => {
                  const done = progress >= step.pct;
                  const active = progress >= (PIPELINE_STEPS[i - 1]?.pct || 0) && !done;
                  return (
                    <div key={step.key} className="flex items-center gap-3">
                      <div
                        className="flex items-center justify-center rounded-full text-xs font-mono shrink-0"
                        style={{
                          width: 20, height: 20,
                          background: done ? 'var(--accent)' : active ? 'var(--bg-deep)' : 'var(--bg-panel)',
                          border: done ? 'none' : `1px solid ${active ? 'var(--accent-muted)' : 'var(--border)'}`,
                          color: done ? '#0c0f0a' : active ? 'var(--accent)' : 'var(--text-muted)',
                        }}
                      >
                        {done ? '✓' : i + 1}
                      </div>
                      <span
                        className="font-mono text-xs"
                        style={{ color: done ? 'var(--text-secondary)' : active ? 'var(--text-primary)' : 'var(--text-muted)' }}
                      >
                        {step.label}
                      </span>
                    </div>
                  );
                })}
              </div>

              {completed && scanStatus && (
                <div className="mt-5 pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-display font-bold text-2xl" style={{ color: 'var(--accent)' }}>
                        {scanStatus.restaurants_found}
                      </span>
                      <span className="font-mono text-sm ml-2" style={{ color: 'var(--text-secondary)' }}>
                        restaurants discovered
                      </span>
                    </div>
                    <button
                      onClick={() => navigate('restaurants')}
                      className="px-4 py-2 rounded-xl font-display font-semibold text-sm transition-all"
                      style={{ background: 'var(--accent)', color: '#0c0f0a' }}
                    >
                      View Results →
                    </button>
                  </div>
                  {scanStatus.scan_time && (
                    <p className="font-mono text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                      Completed in {scanStatus.scan_time}s
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Info section */}
      {!scanning && !completed && !error && (
        <div
          className="rounded-2xl border p-5"
          style={{ background: 'transparent', borderColor: 'var(--border)', borderStyle: 'dashed' }}
        >
          <h4 className="font-display font-semibold text-xs uppercase tracking-widest mb-3" style={{ color: 'var(--text-muted)' }}>
            How it works
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {[
              { icon: '📡', label: 'Multi-source discovery', desc: 'YouTube, Instagram, TikTok & blogs' },
              { icon: '🤖', label: 'AI extraction', desc: 'LLM identifies restaurant names' },
              { icon: '📍', label: 'Google Maps verify', desc: 'Validates location & enriches data' },
              { icon: '📊', label: 'Confidence scoring', desc: 'Ranks by mentions & reviews' },
            ].map((item) => (
              <div key={item.label} className="flex gap-3">
                <span className="text-xl shrink-0">{item.icon}</span>
                <div>
                  <div className="font-display font-semibold text-xs" style={{ color: 'var(--text-secondary)' }}>{item.label}</div>
                  <div className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
