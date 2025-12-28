# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Completed (2025-12-28)

**Phase A - Repository Initialization** ✅
- Git repository with main + v1 branches
- Project structure (backend/ + frontend/)
- Documentation files (README, LICENSE, CHANGELOG, ARCHITECTURE)
- .gitignore for Python, Node.js, Docker, IDE files

**Phase B - Backend Data Models** ✅
- SQLAlchemy models: Product, PriceHistory, Alert, ParserConfig
- Pydantic Settings configuration
- Database connection with pooling (PostgreSQL)
- Alembic migrations system (initial schema 001)
- Complete requirements.txt with dependencies

**Phase C - CRUD API Endpoints** ✅
- Pydantic schemas with validation
- 6 REST endpoints: list, get, create, update, delete, domains
- Pagination (page/page_size) + filtering (status, domain) + sorting
- Automatic domain extraction from URL
- HTTP status codes (200, 201, 204, 404, 400)
- CORS configured for Vue frontend

**Phase T - Docker Compose (Minimal)** ✅
- 3 services: PostgreSQL 16, Redis 7, FastAPI
- Backend Dockerfile (Python 3.12 + Playwright)
- Auto-migration on API startup
- Hot reload for development
- Health checks for dependencies
- Volume persistence for data
- QUICKSTART.md guide with curl examples
- API tested and working on http://localhost:8001
- Fixed Playwright installation (removed --with-deps)
- Changed API port from 8000 to 8001

**Phase D - Generic Parser Engine** ✅
- BaseParser abstract class with ProductData dataclass
- Plugin architecture (parsers register by domain)
- ParserEngine with domain routing
- HTTP fetching with httpx
- Playwright integration for JavaScript rendering
- BeautifulSoup for static HTML parsing
- Price extractors (EUR/USD formats)
- Currency detection
- Comprehensive error handling

**Phase E - Amazon Parser** ✅
- Supports amazon.fr and amazon.be
- Playwright for JavaScript rendering (45s timeout)
- 10+ price selectors with JSON-LD fallback
- 4 title selectors
- 5 image selectors (data-old-hires, src, data-a-dynamic-image)
- Promo detection (deal badges + strikethrough)
- Availability check (multilingual: FR/EN/NL)
- High-resolution image extraction

**Phase F - FR Sites Parsers** ✅
- Cdiscount parser (static HTML)
- Fnac parser (static HTML)
- Boulanger parser (static HTML)
- Multiple CSS selectors per field
- EUR currency detection
- BeautifulSoup for fast parsing
- Error handling and logging

**Phase G - BE Sites Parsers** ✅
- Bol.com parser (static HTML)
- Coolblue parser (static HTML)
- Multilingual support (FR/NL)
- CSS selectors with fallbacks
- Image extraction (src + data-src)
- BeautifulSoup parsing

**Phase H - Parser Config Admin API** ✅
- 7 REST endpoints for parser configs
- GET /api/v1/parser-configs/ - List all configs
- GET /api/v1/parser-configs/{id} - Single config
- GET /api/v1/parser-configs/domain/{domain} - By domain
- POST /api/v1/parser-configs/ - Create (validates duplicates)
- PUT /api/v1/parser-configs/{id} - Update
- DELETE /api/v1/parser-configs/{id} - Delete
- POST /api/v1/parser-configs/{id}/test - Test with URL
- JSON selectors storage
- Domain auto-normalization

**Phase I+J - Celery Workers System** ✅
- Celery configuration (Europe/Paris timezone)
- track_product_price() task with retry policy
- schedule_all_products_tracking() periodic task
- Celery Beat scheduler (hourly at minute 0)
- Docker services: worker + beat
- Retry policy: 3 retries, exponential backoff (2^retry)
- Rate limiting: 5s delay between same-domain requests
- Error tracking: marks ERROR after 5 consecutive failures
- Smart scheduling: respects check_frequency_hours
- Price history creation with duration tracking
- Product updates (price, name, image, timestamps)
- Docker Compose updated to 5 services

### In Progress

**Next: Phases K-M** (Backend finalization)
- Phase K: Price history API (7d/30d/90d/all + statistics)
- Phase L: Promo detection integration
- Phase M: Alert system (price target, drops, promos)

### Technical Details

**Database Schema:**
- products: wishlist items with tracking status
- price_history: time-series price data
- alerts: price change notifications
- parser_configs: domain-specific scraping configs (JSON selectors)

**API Endpoints (Products):**
- GET /api/v1/products/ - List products (paginated, filtered, sorted)
- GET /api/v1/products/domains - Unique domains
- GET /api/v1/products/{id} - Single product
- POST /api/v1/products/ - Create product
- PUT /api/v1/products/{id} - Update product
- DELETE /api/v1/products/{id} - Delete product

**API Endpoints (Parser Configs):**
- GET /api/v1/parser-configs/ - List all configs
- GET /api/v1/parser-configs/{id} - Single config
- GET /api/v1/parser-configs/domain/{domain} - By domain
- POST /api/v1/parser-configs/ - Create config
- PUT /api/v1/parser-configs/{id} - Update config
- DELETE /api/v1/parser-configs/{id} - Delete config
- POST /api/v1/parser-configs/{id}/test - Test config with URL

**Parsers Implemented (6 sites):**
- Amazon FR/BE (Playwright - JavaScript rendering)
- Cdiscount (BeautifulSoup - static HTML)
- Fnac (BeautifulSoup - static HTML)
- Boulanger (BeautifulSoup - static HTML)
- Bol.com (BeautifulSoup - static HTML)
- Coolblue (BeautifulSoup - static HTML)

**Worker System:**
- Celery workers for background price tracking
- Celery Beat scheduler (hourly automatic checks)
- Retry policy with exponential backoff
- Rate limiting per domain (5s delay)
- Error tracking and auto-disable after 5 failures
- Price history creation
- Product status management

**Infrastructure:**
- PostgreSQL 16 with proper indexes and cascade deletes
- Redis 7 for Celery broker and caching
- FastAPI with automatic OpenAPI documentation
- Docker Compose with 5 services (postgres, redis, api, worker, beat)
- Playwright for JavaScript rendering (Amazon)
- BeautifulSoup for static HTML parsing
