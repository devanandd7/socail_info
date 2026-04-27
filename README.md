# SignalFeed

SignalFeed is a hybrid social signal intelligence app that collects, filters, and ranks high-signal posts from X and Reddit.

## Stack

- Backend: FastAPI + SQLAlchemy + APScheduler
- Frontend: Next.js 14 + React 18
- Bot: python-telegram-bot
- DB: SQLite by default, PostgreSQL-ready via `DATABASE_URL`

## Requirements

- Node.js 22+
- Python 3.11+
- `pip` available for your Python runtime

## Project Structure

- `backend/`
  - `main.py`
  - `api/`
  - `models/`
  - `services/`
  - `scraper/`
- `frontend/`
  - `pages/`
  - `components/`
  - `utils/`
- `bot/`
  - `telegram_bot.py`

## Backend Setup (Phase 1 Foundation)

1. Create env file:

   ```bash
   cd backend
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   python3 -m pip install --user --break-system-packages -r requirements.txt
   ```

3. Run API:

   ```bash
   ~/.local/bin/uvicorn main:app --reload --port 8000
   ```

4. Open docs:

   - http://localhost:8000/docs

### API Endpoints

- `GET /posts`
- `GET /filtered`
- `POST /sources`
- `GET /sources`
- `PUT /sources/{id}`
- `DELETE /sources/{id}`
- `POST /hashtags`
- `GET /hashtags`
- `PUT /hashtags/{id}`
- `DELETE /hashtags/{id}`
- `GET /trending`
- `POST /collect` (manual run for collectors)

## Data Collection

### Reddit (MVP + scalable)

- Uses PRAW when credentials are available
- Falls back to Reddit JSON endpoint without credentials

### X/Twitter Prototype Mode

- Selenium script with manual login in browser
- Enable by setting:
  - `USE_TWITTER_API=false`
   - `ENABLE_SELENIUM_X=true`
- Add `account` sources through `POST /sources`

### X/Twitter Scalable Mode

- Uses X official API v2
- Enable by setting:
  - `USE_TWITTER_API=true`
  - `TWITTER_BEARER_TOKEN=...`

## Filtering and Ranking

- Keyword filter: `launch`, `announcing`, `introducing`, `funding`, `release`
- Engagement threshold with configurable minimum
- Managed hashtags are tracked alongside keyword filtering and trending signals
- Optional AI classification into:
  - Product Launch
  - Funding News
  - Important Update
  - Noise
- Ranking score combines:
  - Engagement
  - Recency decay
  - AI confidence

## Frontend Setup

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Configure API URL:

   ```bash
   echo 'NEXT_PUBLIC_API_BASE=http://localhost:8000' > .env.local
   ```

3. Run:-

   ```bash
   npm run dev
   ```

4. Open:-

   - http://localhost:3000

## Frontend Behavior

- Feed auto-refreshes every 30 seconds
- Trending chips are shown on the feed and can populate the keyword filter
- Source management supports create, edit, disable, and delete
- Hashtag management supports create, edit, pause/resume, and delete

## Telegram Bot Setup (Phase 2)

1. Prepare env:

   ```bash
   cd bot
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   python3 -m pip install --user --break-system-packages -r requirements.txt
   ```

3. Configure token in `bot/.env`:

   ```env
   TELEGRAM_BOT_TOKEN=<your_bot_token>
   SIGNALFEED_API_BASE=http://localhost:8000
   DEFAULT_FILTER_MIN_ENGAGEMENT=10
   ```

4. Run bot:

   ```bash
   python telegram_bot.py
   ```

5. Optional local command-logic test without Telegram network:

   ```bash
   python telegram_bot.py --self-test
   ```

### Bot Commands

- `/start`
- `/latest`
- `/filter <keyword>`

## End-to-End Validation

With backend and frontend running, execute:

```bash
./scripts/smoke_test.sh
```

This verifies:

- backend health
- source and hashtag CRUD
- manual collection
- `/posts`, `/filtered`, and `/trending`
- frontend routes (`/` and `/sources`)
- bot `/latest` and `/filter` logic via self-test

## Docker Compose (One-Command Startup)

This repository includes [docker-compose.yml](docker-compose.yml) and Dockerfiles for backend/frontend/bot.

1. Start app stack (backend + frontend + db):

   ```bash
   docker compose up --build
   ```

2. Start with bot profile enabled:

   ```bash
   docker compose --profile bot up --build
   ```

3. Services:

- frontend: http://localhost:3000
- backend: http://localhost:8000
- db: localhost:5432

Note: set a real `TELEGRAM_BOT_TOKEN` before enabling the bot profile.

## Deployment

- Backend: Render or Railway
- Frontend: Vercel
- Database: Supabase or Neon Postgres by setting `DATABASE_URL`

## Best Practices Included

- Modular architecture for collectors and services
- Environment-based secrets and API keys
- Hybrid collection strategy for prototype/scalable rollout
- Scheduled background collection every 10-15 minutes via APScheduler

## MVP Roadmap

- Phase 1: Reddit + keyword filtering + basic feed
- Phase 2: Selenium X + Telegram alerts
- Phase 3: AI filtering + stronger ranking
- Phase 4: Fully API-driven ingestion
