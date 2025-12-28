# Architecture

Documentation detaillee a venir.

## Vue d'ensemble

- Backend API (FastAPI)
- Frontend SPA (Vue 3)
- Workers (Celery + Redis)
- Database (PostgreSQL)
- Scraping (Playwright + BeautifulSoup)

## Components

### Backend (FastAPI)
- REST API endpoints for product and price management
- SQLAlchemy ORM for database operations
- Alembic for database migrations
- Pydantic schemas for request/response validation

### Frontend (Vue 3)
- Single Page Application with Vue Router
- Pinia for state management
- TailwindCSS for styling
- Axios for API communication

### Workers (Celery)
- Scheduled price scraping tasks
- Celery Beat for periodic execution
- Redis as message broker
- Playwright for dynamic content scraping

### Database (PostgreSQL)
- Product catalog
- Price history tracking
- Alert configurations
- Scraping metadata

### Parser Engine
- Generic, configurable parsers
- Domain-specific selector configurations
- Support for both static (BeautifulSoup) and dynamic (Playwright) scraping
- Fallback mechanisms

## Data Flow

1. User adds product URL via Frontend
2. API stores product in PostgreSQL
3. Celery Beat schedules scraping task
4. Worker fetches price using configured parser
5. Price history updated in database
6. Frontend displays price evolution and alerts

## Deployment

- Docker Compose orchestrates all services
- Nginx reverse proxy (future enhancement)
- Self-hosted on VPS
- No external dependencies for MVP
