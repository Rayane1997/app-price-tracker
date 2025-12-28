# Quick Start Guide

## Prerequisites

- Docker & Docker Compose installed
- Git
- Ports 8000 (API), 5432 (PostgreSQL), 6379 (Redis) available

## Setup

### 1. Clone & Configure

```bash
git clone <repo-url>
cd price-tracker
git checkout v1
```

### 2. Environment Variables

The default `.env.example` is already configured for Docker. No changes needed for local development.

### 3. Start Services

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Start Redis
- Build and start FastAPI backend
- Run database migrations automatically

### 4. Verify

Check all services are running:
```bash
docker-compose ps
```

Check API health:
```bash
curl http://localhost:8000/health
```

API Documentation:
- OpenAPI Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Test CRUD Endpoints

**Create a product:**
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "url": "https://www.amazon.fr/product/123",
    "domain": "amazon.fr",
    "target_price": 50.0,
    "check_frequency_hours": 24
  }'
```

**List products:**
```bash
curl http://localhost:8000/api/v1/products/
```

**Get single product:**
```bash
curl http://localhost:8000/api/v1/products/1
```

**Update product:**
```bash
curl -X PUT http://localhost:8000/api/v1/products/1 \
  -H "Content-Type: application/json" \
  -d '{"target_price": 40.0}'
```

**Delete product:**
```bash
curl -X DELETE http://localhost:8000/api/v1/products/1
```

## Useful Commands

**View logs:**
```bash
docker-compose logs -f api
```

**Stop services:**
```bash
docker-compose down
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

**Access PostgreSQL:**
```bash
docker exec -it pricetracker-postgres psql -U pricetracker -d pricetracker
```

**Access Redis CLI:**
```bash
docker exec -it pricetracker-redis redis-cli
```

**Run database migrations:**
```bash
docker-compose exec api alembic upgrade head
```

**Create new migration:**
```bash
docker-compose exec api alembic revision --autogenerate -m "description"
```

## Troubleshooting

**Port already in use:**
Edit `docker-compose.yml` and change the port mappings.

**Database connection errors:**
Wait for PostgreSQL to be ready (check with `docker-compose logs postgres`)

**Permission errors:**
On Linux, you may need to run Docker commands with `sudo` or add your user to the `docker` group.

## Next Steps

- Frontend setup (Phase N)
- Parser implementation (Phase D-G)
- Celery workers setup (Phase I-J)
- Monitoring and logs (Phase S)
