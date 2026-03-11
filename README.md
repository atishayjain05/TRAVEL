# 🍜 FoodScout AI

> AI-powered restaurant discovery platform. Automatically discovers 1000+ restaurants in any city by analyzing YouTube videos, Instagram Reels, TikTok, and food blogs.

---

## Architecture Overview

```
FoodScout AI
├── FastAPI Backend      → REST API, scan orchestration
├── Celery Workers       → Async pipeline processing
├── Redis               → Task queue & result backend
├── PostgreSQL          → Restaurant & scan data storage
├── React + Vite Frontend → Modern SaaS dashboard
└── Scrapers            → Playwright-based content scrapers
```

### Discovery Pipeline

```
User triggers scan
      ↓
[YouTube API] [Instagram Scraper] [TikTok Scraper] [Blog Scraper]
      ↓
   LLM Extraction (Groq/OpenRouter/OpenAI)
      ↓
   Google Maps Verification
      ↓
   RapidFuzz Deduplication
      ↓
   Confidence Scoring
      ↓
   PostgreSQL Storage → Dashboard
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Playwright browsers

---

## Installation

### 1. Clone & Environment Setup

```bash
git clone <repo-url>
cd foodscout-ai

# Copy environment file
cp .env.example .env
# Edit .env with your API keys (see section below)
```

### 2. Python Backend

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Frontend

```bash
cd frontend
npm install
cd ..
```

### 4. PostgreSQL Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE foodscout;"

# Initialize schema
psql -U postgres -d foodscout -f database/schema.sql
```

---

## Environment Variables

Edit `.env` with your credentials:

```env
# Required for YouTube discovery
YOUTUBE_API_KEY=your_youtube_data_api_v3_key

# Required for restaurant verification
GOOGLE_MAPS_API_KEY=your_google_places_api_key

# Required for AI extraction (choose one):
# Option A: Groq (free tier available, fast)
OPENAI_API_KEY=your_groq_api_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama3-8b-8192

# Option B: OpenRouter
OPENAI_API_KEY=your_openrouter_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=meta-llama/llama-3-8b-instruct

# Option C: OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/foodscout

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Getting API Keys

| Key | Where to get |
|-----|-------------|
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) → Enable YouTube Data API v3 |
| `GOOGLE_MAPS_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) → Enable Places API |
| `OPENAI_API_KEY` (Groq) | [console.groq.com](https://console.groq.com) — free tier available |

---

## Running the Application

Open **4 terminal windows**:

### Terminal 1 — Backend API

```bash
source venv/bin/activate
cd foodscout-ai

# From project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

### Terminal 2 — Celery Worker

```bash
source venv/bin/activate
cd foodscout-ai

celery -A backend.workers.celery_worker.celery_app worker \
  --loglevel=info \
  --concurrency=2
```

### Terminal 3 — (Optional) Celery Flower Monitor

```bash
source venv/bin/activate
celery -A backend.workers.celery_worker.celery_app flower --port=5555
```

Flower dashboard: http://localhost:5555

### Terminal 4 — Frontend

```bash
cd foodscout-ai/frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Usage

1. Open http://localhost:5173
2. Click **Scan City** in the sidebar
3. Enter a city name (e.g., `Bangkok`, `New York`, `Singapore`)
4. Select discovery sources and number of sources to scan
5. Click **Start Discovery Scan**
6. Watch real-time progress as the AI discovers restaurants
7. View results in the **Restaurants** tab
8. Export to CSV or Google Sheets via the **Export** tab

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/scan-city` | Start a new city scan |
| `GET` | `/api/scan/{scan_id}` | Get scan status |
| `GET` | `/api/scan-history` | List all scans |
| `GET` | `/api/restaurants` | List restaurants (with filters) |
| `GET` | `/api/restaurants/{city}` | Get restaurants by city |
| `GET` | `/api/stats` | Dashboard analytics |
| `GET` | `/api/export/csv` | Download as CSV |
| `POST` | `/api/export/google-sheets` | Export to Google Sheets |

---

## Google Sheets Export Setup

To use the Google Sheets export feature:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a Service Account under **IAM & Admin**
3. Grant it **Google Sheets API** and **Google Drive API** access
4. Download the JSON key file
5. Set `GOOGLE_SHEETS_CREDENTIALS_FILE=/path/to/your/credentials.json` in `.env`

---

## Performance Notes

- **YouTube**: Uses official API (quota: 10,000 units/day free)
- **Instagram/TikTok**: Playwright-based, may need proxy rotation for high volume
- **Blog scraping**: Uses DuckDuckGo + requests (no API key needed)
- **Google Places**: 200 QPD free, then pay-as-you-go
- **Groq LLM**: Very fast (300+ tokens/s), generous free tier
- For 1000+ restaurants: scan with 100+ sources across multiple runs

---

## Project Structure

```
foodscout-ai/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings & env vars
│   ├── database.py          # SQLAlchemy setup
│   ├── api/
│   │   ├── scan_routes.py   # Scan endpoints
│   │   ├── restaurant_routes.py
│   │   └── export_routes.py
│   ├── models/
│   │   ├── restaurant_model.py
│   │   └── scan_model.py
│   ├── services/
│   │   ├── youtube_service.py
│   │   ├── instagram_service.py
│   │   ├── tiktok_service.py
│   │   ├── blog_service.py
│   │   ├── maps_service.py
│   │   ├── extraction_service.py
│   │   ├── dedupe_service.py
│   │   └── scoring_service.py
│   └── workers/
│       ├── celery_worker.py
│       └── scan_worker.py
├── scrapers/
│   ├── youtube_scraper.py
│   ├── instagram_scraper.py
│   ├── tiktok_scraper.py
│   └── blog_scraper.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── pages/
│   │   └── components/
│   └── package.json
├── database/
│   └── schema.sql
├── requirements.txt
├── .env.example
└── README.md
```

---

## Troubleshooting

**Database connection error**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432
# Create DB if missing
createdb foodscout
```

**Redis connection error**
```bash
redis-server  # Start Redis
redis-cli ping  # Should return PONG
```

**Playwright browsers not found**
```bash
playwright install chromium
```

**Celery not receiving tasks**
- Ensure Redis is running
- Check `CELERY_BROKER_URL` in .env matches your Redis instance

**No restaurants found**
- Verify `YOUTUBE_API_KEY` is valid and has YouTube Data API v3 enabled
- Try with just the `blogs` source first (no API key needed)
- Check backend logs: the Celery worker terminal shows detailed progress
