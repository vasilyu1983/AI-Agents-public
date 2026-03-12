# dlt Pipeline Setup Template

*Purpose: Set up data loading pipelines with dlt (data load tool) for ELT workflows.*

## Installation

```bash
pip install dlt[postgres]  # For Postgres destination
pip install dlt[snowflake]  # For Snowflake
pip install dlt[bigquery]   # For BigQuery
pip install dlt[duckdb]     # For DuckDB
```

## Project Structure

```
my_pipeline/
├── .dlt/
│   ├── config.toml       # Configuration
│   └── secrets.toml      # Credentials (gitignored)
├── pipelines/
│   ├── github_pipeline.py
│   └── stripe_pipeline.py
└── requirements.txt
```

## Basic Pipeline Example

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# Define pipeline
pipeline = dlt.pipeline(
    pipeline_name="github_data",
    destination="duckdb",
    dataset_name="github_raw"
)

# Load data
source = rest_api_source({
    "client": {
        "base_url": "https://api.github.com/repos/dlt-hub/dlt/"
    },
    "resources": ["issues", "pulls"]
})

load_info = pipeline.run(source)
print(load_info)
```

## Configuration (.dlt/config.toml)

```toml
[sources.github]
owner = "dlt-hub"
repo = "dlt"

[destination.postgres]
credentials = "postgres://user:password@localhost:5432/db"

[destination.snowflake]
database = "ANALYTICS"
schema = "RAW_DATA"
```

## Secrets (.dlt/secrets.toml)

```toml
[sources.github.credentials]
access_token = "ghp_your_token_here"

[destination.postgres.credentials]
database = "analytics"
username = "etl_user"
password = "your_password"
host = "localhost"
port = 5432
```

## Run Pipeline

```python
if __name__ == "__main__":
    load_info = pipeline.run(source)
    
    # Check for errors
    print(f"Load info: {load_info}")
    
    # Query loaded data
    with pipeline.sql_client() as client:
        result = client.execute_sql("SELECT COUNT(*) FROM issues")
        print(f"Loaded {result[0][0]} issues")
```

## Best Practices

- BEST: Use .dlt/secrets.toml for credentials (never commit)
- BEST: Enable schema evolution for dynamic APIs
- BEST: Use incremental loading for large datasets
- BEST: Add error handling and retries
- BEST: Monitor pipeline runs with logging
