# Metabase Incident Playbook

## Trigger
- Symptom (downtime/slow dashboards/failed alerts):
- Start time:
- Affected collections/teams:

## Roles
- Incident lead:
- Comms owner:
- Database owner:

## Containment
- [ ] Announce incident (Slack/email channel)
- [ ] Disable problematic dashboards/alerts if causing load
- [ ] Verify DB health; reduce concurrency if needed
- [ ] Enable maintenance page if full outage

## Diagnosis
- [ ] Check Metabase logs (app + DB connectivity)
- [ ] Test connection for each data source
- [ ] Check cache status and recent deploys/upgrades
- [ ] Review DB metrics (CPU, locks, slow queries)
- [ ] Verify sync/analyze jobs status

## Resolution
- [ ] Apply fix (index, cache adjust, rollback deploy, restart app)
- [ ] Re-run failing questions; validate load time
- [ ] Re-enable alerts/subscriptions
- [ ] Confirm dashboards render for target groups

## Postmortem
- Impact summary (duration, users, dashboards)
- Root cause:
- Fix applied:
- Follow-ups (owners + due dates):
- Update runbooks/alerts:
