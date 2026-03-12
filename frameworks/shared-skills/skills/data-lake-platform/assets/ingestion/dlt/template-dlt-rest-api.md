# dlt REST API Source Template

*Purpose: Extract data from REST APIs using dlt's built-in REST API source for ELT pipelines.*

## Installation

```bash
pip install dlt[duckdb]  # Or your destination
pip install requests
```

## Basic REST API Source

### Simple API with Pagination

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# GitHub API example
source = rest_api_source({
    "client": {
        "base_url": "https://api.github.com/repos/dlt-hub/dlt/",
    },
    "resources": [
        "issues",
        "pulls",
        {
            "name": "issue_comments",
            "endpoint": {
                "path": "issues/comments",
                "params": {
                    "per_page": 100,
                },
            },
        },
    ],
})

pipeline = dlt.pipeline(
    pipeline_name="github_api",
    destination="duckdb",
    dataset_name="github_raw"
)

load_info = pipeline.run(source)
print(load_info)
```

## Pagination Strategies

### Offset Pagination

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
    },
    "resources": [
        {
            "name": "products",
            "endpoint": {
                "path": "products",
                "params": {
                    "limit": 100,
                },
                "paginator": {
                    "type": "offset",
                    "limit": 100,
                    "offset": 0,
                    "offset_param": "offset",
                    "limit_param": "limit",
                },
            },
        },
    ],
})
```

### Cursor Pagination

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
    },
    "resources": [
        {
            "name": "users",
            "endpoint": {
                "path": "users",
                "paginator": {
                    "type": "cursor",
                    "cursor_path": "response.next_cursor",
                    "cursor_param": "cursor",
                },
            },
        },
    ],
})
```

### Page Number Pagination

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
    },
    "resources": [
        {
            "name": "orders",
            "endpoint": {
                "path": "orders",
                "paginator": {
                    "type": "page_number",
                    "page_param": "page",
                    "total_path": "response.total_pages",
                    "base_page": 1,
                },
            },
        },
    ],
})
```

## Authentication

### Bearer Token

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "auth": {
            "type": "bearer",
            "token": dlt.secrets["sources.api.token"],
        },
    },
    "resources": ["data"],
})
```

### API Key (Header)

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "headers": {
            "X-API-Key": dlt.secrets["sources.api.api_key"],
        },
    },
    "resources": ["data"],
})
```

### OAuth2

```python
from dlt.sources.helpers.rest_client.auth import OAuth2ClientCredentials

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "auth": OAuth2ClientCredentials(
            access_token_url="https://auth.example.com/token",
            client_id=dlt.secrets["sources.api.client_id"],
            client_secret=dlt.secrets["sources.api.client_secret"],
        ),
    },
    "resources": ["data"],
})
```

## Advanced Patterns

### Nested Resources (Parent-Child)

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
    },
    "resources": [
        {
            "name": "customers",
            "endpoint": "customers",
        },
        {
            "name": "customer_orders",
            "endpoint": {
                "path": "customers/{customer_id}/orders",
                "params": {
                    "customer_id": {
                        "type": "resolve",
                        "resource": "customers",
                        "field": "id",
                    },
                },
            },
        },
    ],
})
```

### Rate Limiting

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "paginator": {
            "type": "auto",
            "maximum_retries": 5,
            "retry_backoff_factor": 2,
        },
    },
    "resources": ["data"],
})
```

### Custom Response Processing

```python
def process_response(response):
    """Transform API response before loading"""
    data = response.json()
    # Extract nested data
    return data.get("results", [])

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
    },
    "resources": [
        {
            "name": "products",
            "endpoint": "products",
            "response_actions": [
                {"status_code": 200, "action": process_response},
            ],
        },
    ],
})
```

## Real-World Examples

### Stripe API

```python
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.stripe.com/v1/",
        "auth": {
            "type": "bearer",
            "token": dlt.secrets["sources.stripe.api_key"],
        },
    },
    "resources": [
        {
            "name": "customers",
            "endpoint": {
                "path": "customers",
                "params": {
                    "limit": 100,
                },
                "paginator": {
                    "type": "cursor",
                    "cursor_path": "data.[-1].id",
                    "cursor_param": "starting_after",
                },
            },
        },
        {
            "name": "charges",
            "endpoint": {
                "path": "charges",
                "params": {
                    "limit": 100,
                },
            },
        },
    ],
})

pipeline = dlt.pipeline(
    pipeline_name="stripe_data",
    destination="postgres",
    dataset_name="stripe_raw"
)

load_info = pipeline.run(source)
```

### HubSpot API

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.hubapi.com/",
        "headers": {
            "Authorization": f"Bearer {dlt.secrets['sources.hubspot.access_token']}",
        },
    },
    "resources": [
        {
            "name": "contacts",
            "endpoint": {
                "path": "crm/v3/objects/contacts",
                "params": {
                    "limit": 100,
                },
                "paginator": {
                    "type": "cursor",
                    "cursor_path": "paging.next.after",
                    "cursor_param": "after",
                },
            },
        },
        {
            "name": "deals",
            "endpoint": {
                "path": "crm/v3/objects/deals",
                "params": {
                    "limit": 100,
                },
            },
        },
    ],
})
```

### Shopify API

```python
source = rest_api_source({
    "client": {
        "base_url": f"https://{dlt.secrets['sources.shopify.shop_name']}.myshopify.com/admin/api/2024-01/",
        "headers": {
            "X-Shopify-Access-Token": dlt.secrets["sources.shopify.access_token"],
        },
    },
    "resources": [
        {
            "name": "products",
            "endpoint": {
                "path": "products.json",
                "params": {
                    "limit": 250,
                },
                "paginator": {
                    "type": "header_link",
                    "links_path": "Link",
                },
            },
        },
        {
            "name": "orders",
            "endpoint": {
                "path": "orders.json",
                "params": {
                    "limit": 250,
                    "status": "any",
                },
            },
        },
    ],
})
```

## Error Handling

```python
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "timeout": 30,  # Request timeout in seconds
        "raise_for_status": True,  # Raise exception on HTTP errors
    },
    "resources": ["data"],
})

pipeline = dlt.pipeline(
    pipeline_name="api_data",
    destination="duckdb",
    dataset_name="api_raw"
)

try:
    load_info = pipeline.run(source)
    print(f"Loaded {load_info}")
except Exception as e:
    print(f"Pipeline failed: {e}")
    # Log error, send alert, etc.
```

## Configuration (.dlt/config.toml)

```toml
[sources.api]
base_url = "https://api.example.com/"
page_size = 100

[destination.postgres]
credentials = "postgres://user:password@localhost:5432/db"
```

## Secrets (.dlt/secrets.toml)

```toml
[sources.api]
api_key = "your_api_key_here"
token = "your_bearer_token_here"

[sources.stripe]
api_key = "sk_live_..."

[sources.hubspot]
access_token = "pat-..."

[sources.shopify]
shop_name = "your-shop"
access_token = "shpat_..."
```

## Best Practices

- BEST: Use secrets.toml for API keys and tokens
- BEST: Implement appropriate pagination for large datasets
- BEST: Add retry logic for transient failures
- BEST: Use cursor pagination when available (more reliable than offset)
- BEST: Respect API rate limits with backoff strategies
- BEST: Extract nested resources using parent-child relationships
- BEST: Process responses to extract relevant data structures
- BEST: Set appropriate timeouts for slow APIs
