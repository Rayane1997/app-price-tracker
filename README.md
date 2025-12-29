# Price Tracker - Wishlist & Price Monitoring

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.4-brightgreen.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-297%20passing-success.svg)

A self-hosted, mono-user price tracking application that monitors your wishlist items across multiple e-commerce platforms and alerts you when prices drop below your target.

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Docker Installation (Recommended)](#docker-installation-recommended)
  - [Manual Installation](#manual-installation)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Docker Services](#docker-services)
- [Configuration](#configuration)
- [Supported E-commerce Sites](#supported-e-commerce-sites)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

### Wishlist Management
- **Easy Product Addition**: Add products from any supported e-commerce site using just the URL
- **Multi-Platform Support**: Track products from Amazon, Cdiscount, Fnac, Boulanger, Bol.com, and Coolblue
- **Product Details**: Automatic extraction of product name, price, image, and availability
- **Domain Filtering**: Organize and filter your wishlist by e-commerce platform

### Automated Price Tracking
- **Regular Monitoring**: Celery-powered scheduled scraping at configurable intervals
- **Smart Scraping**: Adaptive parsing using both static HTML and JavaScript rendering (Playwright)
- **Price History**: Complete historical price data stored in PostgreSQL
- **Reliable Workers**: Distributed task queue with automatic retries on failures

### Price History & Analytics
- **Visual Charts**: Interactive price evolution graphs powered by Chart.js
- **Statistics**: Min/max/average price calculations with trend analysis
- **Historical Data**: Complete price change tracking with timestamps
- **Export-Ready**: API endpoints return data in JSON format for easy integration

### Smart Alerts
- **Target Prices**: Set your desired price point for each product
- **Automatic Notifications**: Get alerted when prices drop below your target
- **Alert Management**: Mark alerts as read or dismiss them
- **Priority Filtering**: View only active, unread, or dismissed alerts

### Multi-Platform Support
- **Generic Parser System**: Configurable CSS/XPath selectors per domain
- **Site-Specific Parsers**: Optimized parsers for major e-commerce platforms
- **Promo Detection**: Identify promotional pricing and special offers
- **Currency Support**: Multi-currency handling (EUR, USD, GBP)

### Self-Hosted
- **Complete Privacy**: Your data stays on your own infrastructure
- **No Authentication**: Simplified setup for personal, local use
- **Docker-Ready**: One-command deployment with docker-compose
- **Open Source**: MIT licensed, fully customizable

---

## Screenshots

> Coming soon: Frontend interface screenshots

The application provides a REST API accessible at `http://localhost:8001/docs` with interactive Swagger documentation.

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.104.1 | High-performance REST API with automatic OpenAPI documentation |
| **PostgreSQL** | 16 | Robust relational database for data persistence |
| **SQLAlchemy** | 2.0.23 | Python ORM for database interactions |
| **Alembic** | 1.13.0 | Database schema migrations and version control |
| **Celery** | 5.3.4 | Distributed task queue for asynchronous scraping jobs |
| **Redis** | 7 | Message broker for Celery and caching layer |
| **Playwright** | 1.40.0 | Browser automation for JavaScript-rendered pages |
| **BeautifulSoup4** | 4.12.2 | HTML parsing for static page scraping |
| **Pydantic** | 2.5.0 | Data validation and settings management |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Vue 3** | 3.4.0 | Progressive JavaScript framework with Composition API |
| **Vite** | 5.0.0 | Lightning-fast development server and build tool |
| **TailwindCSS** | 3.4.0 | Utility-first CSS framework for rapid UI development |
| **Pinia** | 2.1.0 | Modern state management for Vue applications |
| **Chart.js** | 4.4.0 | Interactive charts for price history visualization |
| **Vue Chart.js** | 5.3.0 | Vue 3 wrapper for Chart.js integration |
| **Axios** | 1.6.0 | Promise-based HTTP client for API calls |

### DevOps & Testing
| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | - | Containerization platform |
| **Docker Compose** | 3.8 | Multi-container orchestration |
| **pytest** | 7.4+ | Python testing framework |
| **pytest-asyncio** | 0.21+ | Async test support |
| **pytest-cov** | 4.1+ | Code coverage reporting |

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                    Vue 3 + TailwindCSS                      │
│                   (http://localhost:5173)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                      FastAPI Backend                         │
│                   (http://localhost:8001)                    │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  Products    │ Price History│  Alerts & Parser Configs │ │
│  │  API (6)     │   API (3)    │       API (12)           │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└────────┬────────────────────────────────────────────────────┘
         │
    ┌────┴─────┬──────────────────────┬────────────────┐
    │          │                      │                │
┌───▼───┐  ┌──▼──────┐         ┌────▼────┐      ┌────▼─────┐
│PostgreSQL│ │  Redis   │         │ Celery  │      │  Celery  │
│   DB     │ │  Cache   │         │ Worker  │      │   Beat   │
│          │ │ & Broker │         │         │      │(Scheduler)│
└──────────┘ └──────────┘         └────┬────┘      └──────────┘
                                       │
                              ┌────────▼────────┐
                              │ Parser Engine   │
                              │ ┌─────────────┐ │
                              │ │  Amazon     │ │
                              │ │  Cdiscount  │ │
                              │ │  Fnac       │ │
                              │ │  Boulanger  │ │
                              │ │  Bol.com    │ │
                              │ │  Coolblue   │ │
                              │ │  Generic    │ │
                              │ └─────────────┘ │
                              └─────────────────┘
```

### Component Descriptions

**API Server (`api`)**
- FastAPI application serving REST endpoints
- Automatic OpenAPI/Swagger documentation
- Input validation with Pydantic schemas
- Database access via SQLAlchemy ORM

**Celery Worker (`worker`)**
- Executes asynchronous scraping tasks
- Parallel execution with multiple workers
- Automatic retry on failures
- Invokes parser engine for product data extraction

**Celery Beat (`beat`)**
- Scheduled task orchestrator
- Triggers periodic price checks (default: 24h intervals)
- Configurable per-product check frequency

**Database (`postgres`)**
- Stores products, price history, alerts, and parser configurations
- ACID-compliant transactions
- Automatic schema migrations with Alembic

**Cache & Broker (`redis`)**
- Celery message broker for task distribution
- Result backend for task status tracking
- Optional caching layer for API responses

**Frontend (`frontend`)**
- Reactive Vue 3 UI with Composition API
- Real-time price charts
- Product wishlist management
- Alert notifications

### Data Flow

1. **User adds product URL** → Frontend sends POST to `/api/v1/products/`
2. **API validates and stores** → Creates Product record in PostgreSQL
3. **Celery Beat triggers scraping** → Schedules `scrape_product_price` task
4. **Worker executes task** → Fetches page, invokes appropriate parser
5. **Parser extracts data** → Returns ProductData with name, price, image
6. **Price history updated** → Creates PriceHistory record with timestamp
7. **Alert check** → If price < target_price, creates Alert
8. **Frontend polls API** → Fetches updated data and displays charts

---

## Prerequisites

Before installing, ensure you have the following:

### Required Software
- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Verify: `docker --version && docker-compose --version`
- **Git** (version 2.30+)
  - Verify: `git --version`

### System Requirements
- **RAM**: Minimum 2GB, recommended 4GB (for all services)
- **Disk Space**: Minimum 5GB for Docker images and database
- **OS**: Linux, macOS, or Windows with WSL2

### Port Availability
The following ports must be free on your system:

| Port | Service | Purpose |
|------|---------|---------|
| **5173** | Frontend | Vue 3 development server |
| **8001** | API | FastAPI backend |
| **5432** | PostgreSQL | Database server |
| **6379** | Redis | Cache and message broker |

**Check port availability:**
```bash
# On Linux/macOS
lsof -i :5173 -i :8001 -i :5432 -i :6379

# On Windows (PowerShell)
netstat -ano | findstr "5173 8001 5432 6379"
```

---

## Quick Start

Get up and running in under 2 minutes:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/app-price-tracker.git
cd app-price-tracker
```

### 2. Start All Services
```bash
docker-compose up -d
```

**Expected output:**
```
Creating pricetracker-postgres ... done
Creating pricetracker-redis    ... done
Creating pricetracker-api      ... done
Creating pricetracker-worker   ... done
Creating pricetracker-beat     ... done
Creating pricetracker-frontend ... done
```

### 3. Verify Services Are Running
```bash
docker-compose ps
```

All services should show `Up` status.

### 4. Access the Application

- **Frontend**: http://localhost:5173 (Vue 3 interface)
- **API Documentation**: http://localhost:8001/docs (Swagger UI)
- **API Health Check**: http://localhost:8001/health

### 5. Test the API

```bash
# Check API health
curl http://localhost:8001/health

# Get all products (empty initially)
curl http://localhost:8001/api/v1/products/

# Create your first product
curl -X POST http://localhost:8001/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.fr/dp/B08N5WRWNW",
    "target_price": 299.99
  }'
```

That's it! Your price tracker is now running.

---

## Installation

### Docker Installation (Recommended)

This is the easiest method for deployment.

#### Step 1: Clone and Navigate
```bash
git clone https://github.com/yourusername/app-price-tracker.git
cd app-price-tracker
```

#### Step 2: Configure Environment (Optional)
```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit configuration (optional - defaults work fine)
nano backend/.env
```

**Key environment variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `DEFAULT_CHECK_FREQUENCY_HOURS`: How often to check prices (default: 24)

#### Step 3: Launch Services
```bash
# Start in detached mode
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

#### Step 4: Wait for Startup
Services take 10-30 seconds to fully initialize. Monitor with:
```bash
docker-compose logs -f api
```

Look for: `Application startup complete`

#### Step 5: Verify Installation
```bash
# Check all services are healthy
docker-compose ps

# Test API endpoint
curl http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

### Manual Installation

For development or non-Docker environments.

#### Backend Setup

**1. Install Python 3.12+**
```bash
python3 --version  # Should be 3.12 or higher
```

**2. Create Virtual Environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Install Playwright Browsers**
```bash
playwright install chromium
```

**5. Start PostgreSQL and Redis**
```bash
# Using Docker for database services only
docker run -d --name postgres \
  -e POSTGRES_USER=pricetracker \
  -e POSTGRES_PASSWORD=pricetracker \
  -e POSTGRES_DB=pricetracker \
  -p 5432:5432 postgres:16-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**6. Configure Environment**
```bash
cp .env.example .env
# Edit DATABASE_URL and REDIS_URL if needed
```

**7. Run Database Migrations**
```bash
alembic upgrade head
```

**8. Start Backend Services**

Terminal 1 - API Server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 - Celery Worker:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

Terminal 3 - Celery Beat:
```bash
celery -A app.workers.celery_app beat --loglevel=info
```

#### Frontend Setup

**1. Install Node.js 18+**
```bash
node --version  # Should be 18 or higher
```

**2. Install Dependencies**
```bash
cd frontend
npm install
```

**3. Configure API URL**
```bash
# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8001" > .env
```

**4. Start Development Server**
```bash
npm run dev
```

**Frontend will be available at:** http://localhost:5173

---

## Usage Guide

### Adding a Product to Your Wishlist

**Via API:**
```bash
curl -X POST http://localhost:8001/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.fr/dp/B08N5WRWNW",
    "name": "PlayStation 5",
    "target_price": 449.99
  }'
```

**Via Frontend:**
1. Navigate to http://localhost:5173
2. Click "Add Product" button
3. Paste the product URL
4. Optionally set a target price
5. Click "Save"

The system will automatically:
- Extract product name, price, and image
- Start tracking price changes
- Create alerts when price drops below target

> **Note:** When creating products via the API, the backend automatically derives and normalizes the `domain` from the provided URL, so you only need to send `name` and `url` (plus any optional fields).

### Setting Target Prices

**Update existing product:**
```bash
curl -X PUT http://localhost:8001/api/v1/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "target_price": 399.99
  }'
```

When the price drops below your target, an alert will be created automatically.

### Viewing Price History

**Get historical data:**
```bash
# Get all price points
curl http://localhost:8001/api/v1/products/1/price-history

# Get statistics (min/max/avg)
curl http://localhost:8001/api/v1/products/1/price-history/stats

# Get chart data (formatted for Chart.js)
curl http://localhost:8001/api/v1/products/1/price-history/chart
```

**Via Frontend:**
- Click on any product to view its price chart
- Charts show price evolution over time with min/max/avg lines

### Managing Alerts

**List all alerts:**
```bash
curl http://localhost:8001/api/v1/alerts/
```

**Filter alerts:**
```bash
# Only active alerts
curl http://localhost:8001/api/v1/alerts/?status=active

# Only unread alerts
curl http://localhost:8001/api/v1/alerts/?is_read=false
```

**Mark alert as read:**
```bash
curl -X PUT http://localhost:8001/api/v1/alerts/1/mark-read
```

**Dismiss alert:**
```bash
curl -X PUT http://localhost:8001/api/v1/alerts/1/dismiss
```

### Filtering and Searching

**Filter products by domain:**
```bash
curl http://localhost:8001/api/v1/products/?domain=amazon.fr
```

**List available domains:**
```bash
curl http://localhost:8001/api/v1/products/domains
```

**Pagination:**
```bash
curl "http://localhost:8001/api/v1/products/?skip=0&limit=20"
```

---

## API Documentation

### Interactive Documentation

Access the full Swagger UI at: **http://localhost:8001/docs**

Alternative ReDoc format: **http://localhost:8001/redoc**

### API Endpoints Overview

All endpoints are prefixed with `/api/v1`

#### Products API (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products/` | List all products with pagination |
| `GET` | `/products/{id}` | Get single product details |
| `GET` | `/products/domains` | List unique domains being tracked |
| `POST` | `/products/` | Add new product to wishlist |
| `PUT` | `/products/{id}` | Update product (name, target price) |
| `DELETE` | `/products/{id}` | Remove product from wishlist |

#### Price History API (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products/{id}/price-history` | Get all historical price points |
| `GET` | `/products/{id}/price-history/stats` | Get min/max/avg statistics |
| `GET` | `/products/{id}/price-history/chart` | Get chart-ready data format |

#### Alerts API (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/alerts/` | List all alerts with filters |
| `GET` | `/alerts/{id}` | Get single alert details |
| `PUT` | `/alerts/{id}/mark-read` | Mark alert as read |
| `PUT` | `/alerts/{id}/dismiss` | Dismiss alert |
| `DELETE` | `/alerts/{id}` | Delete alert permanently |

#### Parser Configs API (7 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/parser-configs/` | List all parser configurations |
| `GET` | `/parser-configs/{id}` | Get configuration by ID |
| `GET` | `/parser-configs/domain/{domain}` | Get configuration for domain |
| `POST` | `/parser-configs/` | Create new parser config |
| `PUT` | `/parser-configs/{id}` | Update parser configuration |
| `DELETE` | `/parser-configs/{id}` | Delete parser configuration |
| `POST` | `/parser-configs/{id}/test` | Test parser on sample URL |

#### Promo Detection API (2 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products/{id}/promo-status` | Check current promo status |
| `GET` | `/products/{id}/promo-history` | Get promotional history |

### Example API Calls

**Create a product:**
```bash
curl -X POST http://localhost:8001/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.cdiscount.com/informatique/r-laptop.html",
    "target_price": 799.99
  }'
```

**Get price statistics:**
```bash
curl http://localhost:8001/api/v1/products/1/price-history/stats
```

**Response:**
```json
{
  "product_id": 1,
  "total_entries": 15,
  "min_price": 749.99,
  "max_price": 899.99,
  "avg_price": 824.50,
  "current_price": 779.99,
  "price_drop_percentage": -13.34,
  "first_seen": "2025-01-15T10:00:00",
  "last_checked": "2025-01-29T14:30:00"
}
```

**Create parser configuration:**
```bash
curl -X POST http://localhost:8001/api/v1/parser-configs/ \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example-shop.com",
    "name_selector": "h1.product-title",
    "price_selector": "span.price-value",
    "image_selector": "img.product-image",
    "requires_javascript": false
  }'
```

---

## Development

### Running Tests

The project includes comprehensive test coverage with **297 tests**.

**Run all tests:**
```bash
cd backend
pytest
```

**Run with coverage report:**
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

**Run specific test categories:**
```bash
# Unit tests only
pytest tests/test_parsers.py tests/test_extractors.py

# API tests
pytest tests/test_api_products.py tests/test_api_alerts.py

# Integration tests
pytest tests/test_worker_flows.py
```

**Run with verbose output:**
```bash
pytest -v -s
```

**View coverage report:**
```bash
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

### Adding a New Parser

To support a new e-commerce site, create a parser class:

**1. Create parser file:**
```bash
cd backend/app/parsers
touch my_new_site_parser.py
```

**2. Implement BaseParser:**
```python
from .base import BaseParser, ProductData
from .engine import ParserEngine
from bs4 import BeautifulSoup

class MyNewSiteParser(BaseParser):
    @property
    def supported_domains(self) -> list[str]:
        return ['mynewsite.com', 'www.mynewsite.com']

    @property
    def requires_javascript(self) -> bool:
        return False  # True if site uses JS rendering

    async def parse(self, url: str) -> ProductData:
        engine = ParserEngine()
        html = await engine.fetch_html(url, use_playwright=self.requires_javascript)
        soup = engine.parse_html(html)

        return ProductData(
            name=self.extract_name(soup),
            price=self.extract_price(soup),
            currency=self.extract_currency(soup),
            image_url=self.extract_image(soup),
            raw_html=html[:1000]
        )

    def extract_name(self, soup: BeautifulSoup) -> str:
        return soup.select_one('h1.product-name').get_text(strip=True)

    def extract_price(self, soup: BeautifulSoup) -> float:
        price_text = soup.select_one('span.price').get_text()
        return float(price_text.replace('€', '').replace(',', '.').strip())
```

**3. Register parser:**
```python
# In backend/app/parsers/__init__.py
from .my_new_site_parser import MyNewSiteParser

# Add to parser registry
```

**4. Write tests:**
```python
# In backend/tests/test_parsers.py
@pytest.mark.asyncio
async def test_mynewsite_parser():
    parser = MyNewSiteParser()
    # Test with sample HTML or mocked responses
```

### Running Backend/Frontend Separately

**Backend only:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend only:**
```bash
cd frontend
npm run dev
```

**Hot reload is enabled by default** - changes to code will automatically restart the services.

### Debugging Tips

**Enable debug logging:**
```bash
# In backend/.env
LOG_LEVEL=DEBUG
```

**View real-time logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f worker
docker-compose logs -f api
```

**Access database directly:**
```bash
docker exec -it pricetracker-postgres psql -U pricetracker -d pricetracker
```

**Check Celery task status:**
```bash
docker exec -it pricetracker-worker celery -A app.workers.celery_app inspect active
```

---

## Docker Services

The application uses 6 Docker containers orchestrated by docker-compose:

### 1. postgres (Database)
- **Image**: `postgres:16-alpine`
- **Port**: 5432
- **Purpose**: PostgreSQL database for persistent storage
- **Data**: Stored in Docker volume `postgres_data`
- **Health Check**: `pg_isready` every 5 seconds

### 2. redis (Cache & Broker)
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Purpose**: Message broker for Celery + caching layer
- **Data**: Stored in Docker volume `redis_data`
- **Health Check**: `redis-cli ping` every 5 seconds

### 3. api (FastAPI Backend)
- **Build**: Custom from `backend/Dockerfile`
- **Port**: 8001 (mapped from internal 8000)
- **Purpose**: REST API server
- **Command**: Runs Alembic migrations then starts Uvicorn
- **Depends On**: postgres, redis

### 4. worker (Celery Worker)
- **Build**: Custom from `backend/Dockerfile`
- **Purpose**: Executes scraping tasks asynchronously
- **Command**: `celery worker`
- **Depends On**: postgres, redis, api

### 5. beat (Celery Beat Scheduler)
- **Build**: Custom from `backend/Dockerfile`
- **Purpose**: Schedules periodic price checks
- **Command**: `celery beat`
- **Depends On**: postgres, redis, worker

### 6. frontend (Vue 3 UI)
- **Image**: `node:18-alpine`
- **Port**: 5173
- **Purpose**: Development server for Vue frontend
- **Command**: `npm install && npm run dev`
- **Depends On**: api

### Common Docker Commands

**Start all services:**
```bash
docker-compose up -d
```

**Stop all services:**
```bash
docker-compose down
```

**Stop and remove volumes (resets database):**
```bash
docker-compose down -v
```

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

**Restart a service:**
```bash
docker-compose restart api
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

**Execute command in container:**
```bash
docker exec -it pricetracker-api bash
docker exec -it pricetracker-postgres psql -U pricetracker
```

**Check service health:**
```bash
docker-compose ps
```

---

## Configuration

### Environment Variables

All configuration is done via environment variables in `backend/.env`

#### Database Configuration
```bash
DATABASE_URL=postgresql://pricetracker:pricetracker@postgres:5432/pricetracker
```

#### Redis Configuration
```bash
REDIS_URL=redis://redis:6379/0
```

#### Celery Configuration
```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

#### API Configuration
```bash
API_TITLE=Price Tracker API
API_VERSION=1.0.0
API_PREFIX=/api/v1
```

#### Scraping Configuration
```bash
# User agent for HTTP requests
DEFAULT_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Request timeout in seconds
REQUEST_TIMEOUT=30

# Number of retry attempts on failure
MAX_RETRIES=3
```

#### Tracking Configuration
```bash
# How often to check prices (in hours)
DEFAULT_CHECK_FREQUENCY_HOURS=24
```

### Parser Configuration

Parsers can be configured dynamically via the API without code changes:

**Create generic parser for any site:**
```bash
curl -X POST http://localhost:8001/api/v1/parser-configs/ \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "name_selector": "h1.product-name",
    "price_selector": "span.price",
    "image_selector": "img.main-image",
    "availability_selector": "div.stock-status",
    "requires_javascript": false
  }'
```

### Frontend Configuration

Configure frontend in `frontend/.env`:

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8001
```

---

## Supported E-commerce Sites

The application includes pre-built parsers for the following platforms:

| Site | Domain | Country | Parser Type | Features |
|------|--------|---------|-------------|----------|
| **Amazon** | amazon.fr, amazon.be | FR, BE | JavaScript | Price, Name, Image, Availability |
| **Cdiscount** | cdiscount.com | FR | Static HTML | Price, Name, Image |
| **Fnac** | fnac.com | FR | Static HTML | Price, Name, Image, Reviews |
| **Boulanger** | boulanger.com | FR | Static HTML | Price, Name, Image, Availability |
| **Bol.com** | bol.com | NL, BE | Static HTML | Price, Name, Image |
| **Coolblue** | coolblue.nl, coolblue.be | NL, BE | Static HTML | Price, Name, Image |
| **Generic** | Any domain | - | Configurable | Customizable CSS selectors |

### Parser Capabilities

**Static HTML Parsers** (Faster)
- Cdiscount, Fnac, Boulanger, Bol.com, Coolblue
- Uses BeautifulSoup for parsing
- No browser overhead
- Faster scraping (~1-2 seconds per page)

**JavaScript Parsers** (More Reliable)
- Amazon (requires Playwright)
- Handles dynamically rendered content
- Full browser rendering
- Slower but more accurate (~5-10 seconds per page)

### Adding New Sites

You can add support for any e-commerce site:

1. **Use Generic Parser** (no code required):
   - Create parser config via API
   - Specify CSS selectors for price, name, image
   - Test with sample URL

2. **Write Custom Parser** (for complex sites):
   - Create new parser class extending `BaseParser`
   - Implement extraction logic
   - Add comprehensive tests

---

## Testing

### Test Structure

```
backend/tests/
├── test_api_products.py       # Products API endpoints (6 tests)
├── test_api_price_history.py  # Price history API (8 tests)
├── test_api_alerts.py          # Alerts API (12 tests)
├── test_api_parser_configs.py  # Parser configs API (15 tests)
├── test_parsers.py             # Parser implementations (85 tests)
├── test_extractors.py          # Price extraction utilities (45 tests)
├── test_promo_detector.py      # Promo detection logic (28 tests)
├── test_alert_generator.py     # Alert generation (22 tests)
├── test_models.py              # Database models (35 tests)
├── test_schemas.py             # Pydantic validation (25 tests)
└── test_worker_flows.py        # Celery integration (16 tests)
```

### Running Tests

**All tests (297 total):**
```bash
pytest
```

**Expected output:**
```
======================== 297 passed in 15.42s ========================
```

**With coverage:**
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Unit tests only:**
```bash
pytest tests/test_parsers.py tests/test_extractors.py tests/test_models.py
```

**Integration tests:**
```bash
pytest tests/test_worker_flows.py
```

**API tests:**
```bash
pytest tests/test_api_*.py
```

**Specific test:**
```bash
pytest tests/test_parsers.py::test_amazon_parser_fr -v
```

### Test Categories

**Unit Tests (180 tests)**
- Parser logic
- Price extraction
- Data validation
- Model operations

**Integration Tests (117 tests)**
- API endpoints
- Database operations
- Celery task execution
- End-to-end flows

### Coverage Reports

After running tests with `--cov`, view the HTML report:

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Current coverage:** ~85% (target: 90%+)

---

## Troubleshooting

### Common Issues

#### Port Already in Use

**Symptom:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find process using the port
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill the process or change port in docker-compose.yml
```

#### Database Connection Errors

**Symptom:**
```
could not connect to server: Connection refused
```

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart database service
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

#### Frontend Not Loading

**Symptom:**
- Blank page at http://localhost:5173
- Connection refused

**Solution:**
```bash
# Check if frontend container is running
docker-compose ps frontend

# Restart frontend service
docker-compose restart frontend

# View logs for errors
docker-compose logs -f frontend

# Manually rebuild node_modules
docker-compose exec frontend npm install
```

#### Worker Not Running

**Symptom:**
- Prices not updating
- Tasks stuck in queue

**Solution:**
```bash
# Check worker status
docker-compose ps worker

# View worker logs
docker-compose logs -f worker

# Restart worker
docker-compose restart worker

# Check Celery task queue
docker exec -it pricetracker-worker celery -A app.workers.celery_app inspect active
```

#### Parser Failures

**Symptom:**
```
ParserError: Could not extract price from page
```

**Solution:**
```bash
# Test parser configuration
curl -X POST http://localhost:8001/api/v1/parser-configs/1/test \
  -H "Content-Type: application/json" \
  -d '{"test_url": "https://example.com/product"}'

# Check if site structure changed
# Update CSS selectors in parser config

# Enable debug logging
# In backend/.env: LOG_LEVEL=DEBUG
docker-compose restart api worker
```

### Checking Logs

**All services:**
```bash
docker-compose logs -f
```

**Specific service:**
```bash
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f beat
```

**Last 100 lines:**
```bash
docker-compose logs --tail=100 worker
```

### Resetting Database

**Warning: This deletes all data!**

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm app-price-tracker_postgres_data

# Restart (migrations run automatically)
docker-compose up -d
```

### Health Checks

**API health:**
```bash
curl http://localhost:8001/health
```

**Database connection:**
```bash
docker exec -it pricetracker-postgres pg_isready -U pricetracker
```

**Redis connection:**
```bash
docker exec -it pricetracker-redis redis-cli ping
```

---

## Contributing

Contributions are welcome! This is a personal project, but I'm open to improvements.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with tests
4. **Run tests** to ensure nothing breaks:
   ```bash
   pytest
   ```
5. **Commit your changes** following conventional commits:
   ```bash
   git commit -m "feat(parser): add support for NewSite.com"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** to `main` branch

### Code Style Guide

**Python (Backend):**
- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 100 characters
- Use Black formatter (optional)
- Add docstrings for public methods

**JavaScript/Vue (Frontend):**
- Follow Vue 3 Composition API patterns
- Use ESLint for linting
- Prefer `const` over `let`
- Use meaningful variable names

### Commit Message Format

Follow conventional commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(parser): add Fnac.com scraper with promo detection
fix(api): correct pagination offset calculation
docs(readme): update installation instructions
test(parsers): add comprehensive tests for Amazon parser
```

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add entry to CHANGELOG.md
4. Request review from maintainers
5. Address any feedback
6. Squash commits if requested
7. Merge after approval

### Areas for Contribution

**High Priority:**
- Add parsers for new e-commerce sites
- Improve error handling in existing parsers
- Add frontend UI components
- Increase test coverage

**Medium Priority:**
- Performance optimizations
- Additional chart types for price history
- Email/webhook notifications for alerts
- Export data to CSV/JSON

**Low Priority:**
- Multi-user support with authentication
- Mobile app (React Native)
- Browser extension for easy product addition

---

## Roadmap

### Current Status (v1.0)

- ✅ Complete REST API with 23 endpoints
- ✅ 7 pre-built parsers (Amazon, Cdiscount, Fnac, etc.)
- ✅ Generic parser system for any site
- ✅ Price history tracking and visualization
- ✅ Alert system with target prices
- ✅ Promo detection
- ✅ Docker deployment
- ✅ 297 tests with 85%+ coverage

### Future Features (v2.0)

**Q1 2026:**
- [ ] Vue 3 frontend UI (currently API-only)
- [ ] Interactive price charts with drill-down
- [ ] Product search and filtering
- [ ] Dashboard with statistics

**Q2 2026:**
- [ ] Email notifications for price alerts
- [ ] Webhook support for integrations
- [ ] Data export (CSV, JSON, Excel)
- [ ] Backup/restore functionality

**Q3 2026:**
- [ ] Browser extension (Chrome/Firefox)
- [ ] One-click product addition from any site
- [ ] Historical price analysis and predictions
- [ ] Price drop probability calculator

**Q4 2026:**
- [ ] Multi-user support with authentication
- [ ] User roles and permissions
- [ ] Shared wishlists
- [ ] Mobile app (React Native)

### Known Limitations

- **Single user only**: No authentication system (designed for personal use)
- **No email notifications**: Alerts are API-only (webhook support planned)
- **Site-specific parsers**: Some sites may require updates when HTML changes
- **No price prediction**: Only historical tracking (ML predictions planned)
- **Limited currency support**: Primarily EUR (multi-currency improvements planned)

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Price Tracker Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See the [LICENSE](LICENSE) file for full details.

---

## Acknowledgments

### Technologies Used

This project wouldn't be possible without these amazing open-source projects:

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast Python web framework
- **[Vue.js](https://vuejs.org/)** - Progressive JavaScript framework
- **[PostgreSQL](https://www.postgresql.org/)** - World's most advanced open source database
- **[Celery](https://docs.celeryq.dev/)** - Distributed task queue
- **[Playwright](https://playwright.dev/)** - Browser automation framework
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** - HTML parsing library
- **[TailwindCSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Docker](https://www.docker.com/)** - Containerization platform

### Inspiration

Inspired by price tracking services like:
- Honey (browser extension)
- CamelCamelCamel (Amazon tracker)
- Keepa (price history charts)

But built with **complete data ownership** and **self-hosting** in mind.

### Special Thanks

- All open-source contributors who maintain the dependencies
- The FastAPI and Vue.js communities for excellent documentation
- Everyone who reports bugs and suggests features

---

## Support

### Getting Help

- **Documentation**: You're reading it!
- **API Docs**: http://localhost:8001/docs
- **Issues**: [GitHub Issues](https://github.com/yourusername/app-price-tracker/issues)

### Reporting Bugs

When reporting bugs, please include:

1. **Environment**: OS, Docker version, Python version
2. **Steps to reproduce**: Exact commands or actions taken
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Logs**: Relevant log output from `docker-compose logs`
6. **Screenshots**: If applicable

### Feature Requests

Open a GitHub issue with:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: What alternatives have you considered?

---

**Built with ❤️ for personal privacy and data ownership**

Star ⭐ this repo if you find it useful!
