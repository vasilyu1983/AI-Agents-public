# Onboarding Documentation

Patterns for developer onboarding docs that reduce time-to-productivity without duplicating existing content.

---

## Onboarding Doc Types

Each type serves a different moment in the ramp-up.

| Doc Type | Purpose | When Used | Owner |
|----------|---------|-----------|-------|
| **Quickstart** | First working build in < 30 min | Day 1, hour 1 | Platform/DevEx team |
| **Environment setup** | Full local dev environment | Day 1-2 | Platform/DevEx team |
| **Architecture walkthrough** | System map and key decisions | Day 2-3 | Tech lead |
| **First PR guide** | End-to-end contribution flow | Day 3-5 | Onboarding buddy |
| **Service catalog** | What each service does, who owns it | Week 1-2 | Engineering org |
| **On-call guide** | Alerting, escalation, runbooks | Week 3-4 | SRE/platform team |

---

## Day 1 to Week 4 Structure

Organize the ramp-up as a checklist, not a wall of text.

**Day 1 -- Build and run:**
- [ ] Clone repo and run quickstart
- [ ] Verify local build passes tests
- [ ] Access Slack channels, Jira board, CI dashboard
- [ ] Meet onboarding buddy

**Day 2-3 -- Understand the system:**
- [ ] Read architecture walkthrough
- [ ] Walk through 2-3 recent PRs with buddy
- [ ] Identify the 3 services you will work in most
- [ ] Read ADRs for those services

**Week 1 -- First contribution:**
- [ ] Pick a `good-first-issue` ticket
- [ ] Follow the first PR guide end-to-end
- [ ] Get PR reviewed, address feedback, merge
- [ ] Attend team standup and retro

**Week 2-3 -- Deepen context:**
- [ ] Read on-call runbooks for your team's services
- [ ] Shadow an on-call shift or incident review
- [ ] Complete a medium-complexity ticket independently

**Week 4 -- Validate and close:**
- [ ] Buddy confirms independent ticket capability
- [ ] Give feedback on the onboarding docs themselves

---

## What to Include vs What to Link

Onboarding docs rot fast when they duplicate content maintained elsewhere. Use this decision guide.

**Include directly:** Steps unique to onboarding (account provisioning, first-day checklist), curated reading order, and context that does not exist elsewhere (team norms, unwritten conventions).

**Link to, never copy:** README setup instructions, ADRs, API reference, CI/CD pipeline docs, on-call runbooks.

**Rule:** If the source doc has its own owner and update cadence, link to it. If you copy it, it will diverge within one quarter.

---

## Buddy and Mentor Documentation

The buddy carries context that is hard to write down. Reduce the bus factor with lightweight handoff notes.

**Buddy handoff template:**

```markdown
## Onboarding Buddy Notes — [New Hire Name]

**Start date:** YYYY-MM-DD | **Buddy:** [Name] | **Team:** [Team]

### Key context to share early
- [Gotcha or unwritten rule #1]
- [Which Slack channels to watch]

### Suggested first tickets
- [JIRA-123] — Good scope, touches the main service
- [JIRA-456] — Small fix, good for learning the PR flow

### People to meet
- [Name] — Owns [service], good for architecture questions

### Notes from pairing sessions
- [Date]: [Topic]. [What they understood / what needs follow-up]
```

Keep these notes in a private doc (Notion, Google Doc), not in the repo. They contain names and are time-bound.

---

## Measuring Effectiveness

Track these to know if onboarding docs are working.

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Time to first PR merged | < 5 business days | Git log: first commit by new hire |
| Self-service resolution rate | > 70% of setup questions | Survey or Slack thread analysis |
| Onboarding doc feedback score | > 4/5 | End-of-week-1 survey |
| Setup issues reported | < 2 per new hire | Slack #onboarding channel |
| Time to independent ticket completion | < 3 weeks | Jira data |

**Feedback loop:** Every new hire edits or flags at least one onboarding doc issue before week 4 ends. This keeps docs current and gives the new hire agency.

---

## Templates

### Quickstart Template

```markdown
# Quickstart — Get a local build running in under 30 minutes.

## Prerequisites
- [Language] [version]+
- [Tool] [version]+
- Access to [VPN / internal registry] (request via [link])

## Steps
1. Clone: `git clone [repo-url] && cd [repo-name]`
2. Install: `[install command]`
3. Configure: `cp .env.example .env` — see [config guide] for values
4. Run: `[run command]`
5. Verify: Open [URL]. You should see [expected result].

## Troubleshooting
- **[Common error]**: [Fix]
- Still stuck? Ask in #[slack-channel].
```

### Environment Setup Checklist

```markdown
- [ ] IDE installed and configured ([link to IDE settings])
- [ ] Git configured (name, email, GPG signing)
- [ ] SSH key added to GitHub
- [ ] VPN and internal package registry authenticated
- [ ] Docker Desktop running, local database seeded
- [ ] All tests pass locally
- [ ] CI dashboard accessible
- [ ] Slack channels joined: #[team], #[engineering], #[incidents]
```

---

## Anti-Patterns

- **Info dump.** A 50-page onboarding doc nobody reads. Break it into the checklist structure above. No single doc should exceed 2 pages of content the reader must act on.
- **Stale quickstart.** The most common onboarding failure. If the quickstart does not work on a clean machine, nothing else matters. Test it monthly.
- **Tribal knowledge gates.** "Ask Sarah, she knows how that works." If it is not written down, it does not scale. The buddy handoff template exists to capture this.
- **Duplicated setup instructions.** Quickstart copies the README, then both diverge. Link to the README. One source of truth.
- **No feedback loop.** New hires silently struggle. Require every new hire to file at least one doc improvement by week 4.
- **Onboarding docs owned by nobody.** Assign an explicit owner. Review quarterly. Stale onboarding docs are worse than no onboarding docs because they erode trust.

---

## Related Resources

- [readme-best-practices.md](readme-best-practices.md) - README standards to link from quickstart
- [contributing-guide-standards.md](contributing-guide-standards.md) - First PR workflow patterns
- [production-gotchas-guide.md](production-gotchas-guide.md) - Tribal knowledge documentation
