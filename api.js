/**
 * FoodScout AI — API Client
 * All communication with the FastAPI backend.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  // Handle blob responses (CSV download)
  if (options._blob) return res.blob();

  return res.json();
}

// ── Scans ────────────────────────────────────────────────────────────────────

export const api = {
  /** Start a city scan */
  startScan: (payload) =>
    request('/api/scan-city', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  /** Get scan status by ID */
  getScanStatus: (scanId) => request(`/api/scan/${scanId}`),

  /** Get scan history */
  getScanHistory: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/api/scan-history${q ? `?${q}` : ''}`);
  },

  // ── Restaurants ──────────────────────────────────────────────────────────

  /** List restaurants with filters */
  getRestaurants: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== '' && v !== null)
    ).toString();
    return request(`/api/restaurants${q ? `?${q}` : ''}`);
  },

  /** Get restaurants for a specific city */
  getRestaurantsByCity: (city, params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/api/restaurants/${encodeURIComponent(city)}${q ? `?${q}` : ''}`);
  },

  /** Delete a restaurant */
  deleteRestaurant: (id) =>
    request(`/api/restaurants/${id}`, { method: 'DELETE' }),

  // ── Stats ────────────────────────────────────────────────────────────────

  /** Dashboard stats */
  getStats: () => request('/api/stats'),

  // ── Export ───────────────────────────────────────────────────────────────

  /** Download CSV */
  downloadCsv: async (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== '')
    ).toString();
    const blob = await request(`/api/export/csv${q ? `?${q}` : ''}`, { _blob: true });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `foodscout_restaurants.csv`;
    a.click();
    URL.revokeObjectURL(url);
  },

  /** Export to Google Sheets */
  exportToSheets: (payload) =>
    request('/api/export/google-sheets', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  /** Health check */
  health: () => request('/health'),
};

export default api;
