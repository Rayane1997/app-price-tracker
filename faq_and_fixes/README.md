# FAQ & Fixes

## Fix: Amazon `amazon.com.be` Parser Support

- **Issue**: Worker logs showed `No parser found for domain: amazon.com.be` when scraping Belgian Amazon URLs. The parser registry only exposed `amazon.fr` and `amazon.be`.
- **Resolution**: Added `amazon.com.be` to `AmazonParser.supported_domains`, updated parser unit tests, and redeployed/restarted the Celery worker so `parser_engine` re-registered the new domain.
- **Technical steps**:
  1. Edit `backend/app/parsers/amazon_parser.py` to include the extra domain in `supported_domains`.
  2. Extend `tests/test_parsers.py::TestAmazonParser` to cover the new domain and URL validation.
  3. Restart worker (`docker compose restart worker`) to reload parser registry inside the container.
  4. Trigger a manual scrape (`docker compose exec worker celery -A app.workers.celery_app call app.workers.tasks.track_product_price --args='[<product_id>]'`) to confirm parsing works.
- **Outcome**: Product 8 (`dji osmo pocket 3`) now fetches price/name/image and generates alerts successfully.

## FAQ

### How do I manually rerun a product scrape?
1. Get the product ID (`curl http://localhost:8001/api/v1/products/ | jq '.products[] | {id,name,url}'`).
2. From repo root (`/Users/rayane/Documents/git/app-price-tracker`), run:
   ```bash
   docker compose exec worker \
     celery -A app.workers.celery_app call app.workers.tasks.track_product_price \
     --args='[<PRODUCT_ID>]'
   ```
3. Check `docker compose logs --tail=100 worker` for the result and verify `/api/v1/products/<id>` updated.

### How can I debug "No parser found for domain ..." errors?
1. Confirm `backend/app/parsers/*` include the domain in `supported_domains`.
2. In the worker container, run `python -c "from app.parsers.amazon_parser import AmazonParser; print(AmazonParser().supported_domains)"` to see what's registered.
3. If the code changed locally, restart the worker: `docker compose restart worker` (the parser registry loads at import time).
4. Re-trigger the task to confirm the fix.

### What if the parser returns `price=None`?
1. Inspect worker logs around the execution for warnings like "Could not extract price".
2. Capture the HTML chunk by temporarily logging `product_data.raw_html` when debugging locally (avoid in production).
3. Update the parser selectors (e.g., `price_selectors` array in `AmazonParser`) to match the page structure.
4. Rerun `python3 -m pytest tests/test_parsers.py::TestAmazonParser` and the Celery task to validate.

### How do I run backend tests locally?
```bash
cd backend
python3 -m pytest
```
Use targeted runs for faster feedback, e.g. `python3 -m pytest tests/test_parsers.py::TestAmazonParser`.

### How can I inspect Celery logs quickly?
```bash
docker compose logs -f worker
```
Add `--tail=200` for a smaller snapshot. For Beat scheduling issues, inspect `docker compose logs beat`.
