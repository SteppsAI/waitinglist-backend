# WaitingList Backend

FastAPI backend for the WaitingList project.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file with the following variables:
```
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your_host
POSTGRES_PORT=5432
POSTGRES_DB=your_database
RESEND_API_KEY=your_resend_api_key
```

3. Run the development server:
```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/waitlist/subscribe` - Subscribe to the waitlist

## Tech Stack

- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Resend (email service)
- SlowAPI (rate limiting)







