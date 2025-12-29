# Price Tracker API - Product Endpoints

Base URL: `http://localhost:8000/api/v1`

## Endpoints Created

### 1. List Products (with pagination & filtering)
**GET** `/api/v1/products/`

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 50, max: 100) - Items per page
- `status` (enum, optional) - Filter by status: `active`, `error`, `not_trackable`, `paused`
- `domain` (string, optional) - Filter by domain (e.g., `amazon.fr`)
- `sort_by` (string, default: `created_at`) - Sort field
- `sort_order` (enum, default: `desc`) - Sort order: `asc` or `desc`

**Response:** `ProductList` schema
```json
{
  "products": [...],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
```

### 2. Get Unique Domains
**GET** `/api/v1/products/domains`

**Response:** List of strings
```json
["amazon.fr", "cdiscount.com", "fnac.com"]
```

### 3. Get Single Product
**GET** `/api/v1/products/{product_id}`

**Response:** `ProductResponse` schema
```json
{
  "id": 1,
  "name": "Product name",
  "url": "https://...",
  "domain": "amazon.fr",
  "current_price": 49.99,
  "currency": "EUR",
  "target_price": 39.99,
  ...
}
```

### 4. Create Product
**POST** `/api/v1/products/`

**Request Body:** `ProductCreate`/`ProductCreateRequest` schema (domain optional)
```json
{
  "name": "Product name",
  "url": "https://amazon.fr/product/...",
  "target_price": 39.99,
  "image_url": "https://...",
  "check_frequency_hours": 24,
  "tags": "electronics,wishlist",
  "notes": "Wait for discount"
}
```

**Response:** `ProductResponse` schema (201 Created)

**Validations:**
- URL must start with `http://` or `https://`
- Domain is automatically extracted from the URL when omitted and normalized (lowercase, `www.` removed)
- `name`: 1-500 characters
- `target_price`: >= 0
- `check_frequency_hours`: 1-168 (1 week max)
- `tags`: max 500 characters

### 5. Update Product
**PUT** `/api/v1/products/{product_id}`

**Request Body:** `ProductUpdate` schema (all fields optional)
```json
{
  "name": "Updated name",
  "target_price": 29.99,
  "status": "paused",
  "notes": "Updated notes"
}
```

**Response:** `ProductResponse` schema

### 6. Delete Product
**DELETE** `/api/v1/products/{product_id}`

**Response:** 204 No Content

**Note:** Cascade deletes all related `price_history` and `alerts` records.

## Product Status Enum
- `active` - Product is being actively tracked
- `error` - Last scraping attempt failed
- `not_trackable` - Product page structure not supported
- `paused` - User paused tracking

## Error Responses

**404 Not Found**
```json
{
  "detail": "Product not found"
}
```

**400 Bad Request**
```json
{
  "detail": "Validation error message"
}
```

## Notes
- Domain is automatically extracted from URL when creating/updating
- Domain prefix `www.` is automatically removed
- Pagination calculates `total_pages` automatically
- All timestamps in UTC
- Frontend can access via CORS from `http://localhost:5173`
