# Signed Embed JWT Examples

Use these examples when the requirement is embedded dashboards or questions in an external app. For multi-tenant isolation, pair this with [../references/tenants-routing.md](../references/tenants-routing.md).

## Python

```python
import time
import jwt

METABASE_SITE_URL = "https://metabase.example.com"
METABASE_EMBED_SECRET = "replace-me"

payload = {
    "resource": {"dashboard": 42},
    "params": {"customer_id": 123},
    "exp": int(time.time()) + 600,
}

token = jwt.encode(payload, METABASE_EMBED_SECRET, algorithm="HS256")
embed_url = f"{METABASE_SITE_URL}/embed/dashboard/{token}"
print(embed_url)
```

## Node.js

```javascript
const jwt = require("jsonwebtoken");

const payload = {
  resource: { dashboard: 42 },
  params: { customer_id: 123 },
  exp: Math.round(Date.now() / 1000) + 600,
};

const token = jwt.sign(payload, process.env.METABASE_EMBED_SECRET);
const url = `${process.env.METABASE_URL}/embed/dashboard/${token}`;
console.log(url);
```
