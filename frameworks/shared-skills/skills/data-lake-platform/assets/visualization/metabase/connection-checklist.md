# Metabase Connection Checklist

## Inputs
- Database type / version:
- Host / port:
- Database name:
- Username (service account):
- Auth method (password / IAM / keyfile):
- SSL mode (require/verify-full):
- Time zone:

## Steps
- [ ] Create/rotate service account with least privilege
- [ ] Enable SSL and verify TLS cert
- [ ] Set `Maximum connections` (Metabase) to avoid DB starvation
- [ ] Configure `Use server SSL` and connection timeout
- [ ] Test connection from Metabase UI
- [ ] Save connection and trigger initial sync + analyze
- [ ] Add owner + rotation date + ticket link

## Post-Checks
- [ ] Permissions: assign groups/collections
- [ ] Row-level filters configured if needed
- [ ] Caching policy set (TTL, warmup)
- [ ] Alerting on connection failures enabled
