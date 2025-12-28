# Price Tracker - Wishlist & Price Monitoring

A self-hosted, mono-user price tracking application for personal use. Monitor your wishlist items across multiple e-commerce platforms and get notified when prices drop.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.4-brightgreen.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Wishlist Management**: Add products from any e-commerce website with URLs
- **Automated Price Tracking**: Regular scraping with Celery workers
- **Price History**: Track price evolution over time with charts
- **Smart Alerts**: Get notified when prices drop below your target
- **Multi-Platform Support**: Generic parser system configurable per domain
- **Self-Hosted**: Complete control over your data on your own VPS
- **No Authentication Required**: Designed for personal, local use

## Architecture

### Backend
- **FastAPI**: High-performance REST API
- **PostgreSQL**: Robust data persistence
- **Celery**: Distributed task queue for scraping jobs
- **Redis**: Message broker and caching layer
- **Playwright + BeautifulSoup**: Powerful web scraping capabilities
- **SQLAlchemy**: ORM with Alembic migrations

### Frontend
- **Vue 3**: Modern, reactive UI framework
- **Vite**: Lightning-fast development and build tool
- **TailwindCSS**: Utility-first styling
- **Pinia**: State management
- **Chart.js**: Price history visualization

### Workers
- **Celery Beat**: Scheduled scraping tasks
- **Celery Workers**: Parallel scraping execution
- **Generic Parser Engine**: Configurable CSS/XPath selectors per domain

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- Ports 8000 (API), 5173 (Frontend), 5432 (PostgreSQL), 6379 (Redis)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd price-tracker
git checkout v1  # Development branch
```

2. Configure environment variables:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. Launch with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:5173 (Phase N - not implemented yet)
- API Docs: http://localhost:8001/docs
- API Health: http://localhost:8001/health

### Development

Stop services:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

Rebuild after changes:
```bash
docker-compose up -d --build
```

## Quick Start (Docker)

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

**TL;DR:**
```bash
git clone <repo-url> && cd price-tracker
git checkout v1
docker-compose up -d
# API will be available at http://localhost:8001
# Docs at http://localhost:8001/docs
```

**Test the API:**
```bash
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/products/
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API Framework | FastAPI | REST API with automatic OpenAPI docs |
| Database | PostgreSQL | Relational data storage |
| ORM | SQLAlchemy | Database models and queries |
| Migrations | Alembic | Database schema versioning |
| Task Queue | Celery | Asynchronous scraping jobs |
| Message Broker | Redis | Celery backend and caching |
| Scraping | Playwright + BeautifulSoup | Dynamic and static page scraping |
| Frontend Framework | Vue 3 (Composition API) | Reactive UI |
| Build Tool | Vite | Fast dev server and bundler |
| Styling | TailwindCSS | Utility-first CSS |
| State Management | Pinia | Vue state management |
| Charts | Chart.js | Price history visualization |
| Containerization | Docker + Docker Compose | Service orchestration |

## Branching Strategy

- `main`: Production-ready code (stable releases)
- `v1`: Active development branch (MVP features)
- Feature branches: `feature/<name>` merged into `v1`

## Development Status

**🟢 Completed (4/25 phases)** - API fully functional!

### ✅ Phase A: Repository Initialization
- [x] Git repository setup (main + v1 branches)
- [x] Project structure
- [x] Documentation files

### ✅ Phase B: Backend Foundation
- [x] FastAPI application skeleton
- [x] Database models (Product, PriceHistory, Alert, ParserConfig)
- [x] PostgreSQL integration with Alembic
- [x] Complete configuration system

### ✅ Phase C: CRUD API Endpoints
- [x] Pydantic schemas with validation
- [x] 6 REST endpoints (list, get, create, update, delete, domains)
- [x] Pagination + filtering + sorting
- [x] API tested and working

### ✅ Phase T: Docker Compose (Minimal)
- [x] PostgreSQL 16 + Redis 7 + FastAPI services
- [x] Auto-migration on startup
- [x] Health checks
- [x] Complete deployment guide

### 🟡 Next: Phase D-M (Backend Completion)
- [ ] Generic parser engine (Phase D)
- [ ] Site-specific parsers (Phase E-G)
- [ ] Parser admin API (Phase H)
- [ ] Celery workers + scheduler (Phase I-J)
- [ ] Price history API (Phase K)
- [ ] Promo detection (Phase L)
- [ ] Alert system (Phase M)

### Remaining Phases (21/25)
See [CHANGELOG.md](CHANGELOG.md) for detailed breakdown of all phases.

## Contributing

This is a personal project, but contributions are welcome!

### Commit Guidelines
- Use atomic commits (one logical change per commit)
- Write clear, descriptive commit messages
- Follow conventional commits format: `type(scope): message`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
  - Example: `feat(parser): add Amazon product scraper`

### Development Workflow
1. Create feature branch from `v1`
2. Implement changes with tests
3. Submit pull request to `v1`
4. Code review and merge

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Project Status

Currently in MVP development (v1 branch). Not production-ready.
