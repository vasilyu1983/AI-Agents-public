# Legal Compliance for AEO Monitoring

Legal considerations, ToS compliance, and risk mitigation for building AEO monitoring tools.

## Disclaimer

**This document is for educational purposes only and does not constitute legal advice.**

Consult with qualified legal counsel before implementing any monitoring system. Laws and platform terms of service change frequently.

## Risk Assessment Matrix

| Approach | ToS Risk | Legal Risk | Detection Risk | Recommendation |
| -------- | -------- | ---------- | -------------- | -------------- |
| Official APIs | None | None | None | RECOMMENDED |
| Commercial scraping (reputable) | Transferred | Provider liability | Low | Acceptable |
| DIY web scraping | High | Medium-High | High | NOT RECOMMENDED |
| Bypassing authentication | Very High | High | Very High | NEVER |
| Violating robots.txt | Very High | High | Very High | NEVER |

## Platform Terms of Service

### Perplexity

**API Terms**: [perplexity.ai/terms](https://www.perplexity.ai/terms)

**Key points**:

- API use permitted for building applications
- Must comply with rate limits
- No reselling of API access
- Attribution may be required

**Risk level**: Low (API designed for this use case)

### Google Gemini

**API Terms**: [ai.google.dev/terms](https://ai.google.dev/terms)

**Key points**:

- API use permitted within usage policies
- Prohibited uses: harmful content generation, deception
- Must comply with rate limits
- Google reserves right to revoke access

**Risk level**: Low (official API)

### Anthropic Claude

**API Terms**: [anthropic.com/legal/aup](https://www.anthropic.com/legal/aup)

**Key points**:

- API use permitted for legitimate applications
- Must comply with Acceptable Use Policy
- Prohibited: generating harmful content, surveillance
- Rate limits must be respected

**Risk level**: Low (official API)

### OpenAI

**API Terms**: [openai.com/policies/terms-of-use](https://openai.com/policies/terms-of-use)

**Key points**:

- API use permitted
- Usage policies apply
- Must not circumvent safeguards
- Output ownership clarified

**Risk level**: Low (official API)

### ChatGPT Web Interface

**Terms**: [openai.com/policies/terms-of-use](https://openai.com/policies/terms-of-use)

**Key points**:

- Automated access prohibited
- Scraping explicitly forbidden
- Session token extraction violates ToS
- Account termination for violations

**Risk level**: HIGH (scraping violates ToS)

### Google Search / AI Overviews

**Terms**: [google.com/intl/en/policies/terms/](https://www.google.com/intl/en/policies/terms/)

**Key points**:

- Automated queries prohibited
- Must respect robots.txt
- Scraping search results violates ToS
- Legal action precedent exists

**Risk level**: VERY HIGH

## Legal Precedents

### hiQ Labs v. LinkedIn (2022)

**Ruling**: Scraping publicly accessible data is not a CFAA violation.

**Implications**:

- Public data scraping may be legal
- BUT violating ToS can still result in breach of contract claims
- Does NOT apply to authenticated content

### Reddit v. Perplexity AI (2024)

**Allegations**:

- Unauthorized data collection
- ToS violations
- Potential copyright infringement

**Status**: Ongoing litigation

**Implications**:

- Even large AI companies face legal challenges
- Data sourcing practices under scrutiny

### X (Twitter) v. Various (2023-2024)

**Policy**: $15,000 liquidated damages per 1M posts accessed without consent

**Implications**:

- Platforms increasingly aggressive about enforcement
- Financial penalties can be substantial

## robots.txt Obligations

### Must Always Respect

```
User-agent: *
Disallow: /private/
```

**Legal basis**: Violating robots.txt may strengthen claims against you.

### AI Crawler Blocks

Many websites now block AI crawlers:

```
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: PerplexityBot
Disallow: /
```

Trend: crawler blocking is increasingly common. Validate access via crawl logs, robots checks, and platform policies before investing in monitoring at scale.

## Compliance Checklist

### Before Building

```
[ ] Using official APIs where available
[ ] Legal review of planned activities
[ ] ToS review for each platform
[ ] Budget for commercial services where needed
[ ] Data retention policy defined
[ ] Security measures for API keys
```

### During Operation

```
[ ] Respecting rate limits
[ ] Not bypassing authentication
[ ] Not accessing restricted content
[ ] Logging access for audit trail
[ ] Monitoring for ToS changes
```

### Data Handling

```
[ ] Only storing necessary data
[ ] Not extracting copyrighted content (only metadata/citations)
[ ] Implementing data retention limits
[ ] Secure storage for collected data
[ ] Access controls for sensitive data
```

## Safe Practices

### DO

- Use official APIs
- Respect rate limits
- Implement exponential backoff
- Log all API calls for audit
- Monitor ToS changes
- Use commercial scraping services for high-risk platforms
- Store only metadata, not full content

### DON'T

- Scrape web interfaces when APIs exist
- Bypass authentication
- Ignore robots.txt
- Store copyrighted content
- Share API keys
- Exceed rate limits
- Build tools that could be used for harassment

## Commercial Scraping Services

### Due Diligence Checklist

When selecting a commercial scraping provider:

```
[ ] Clear terms of service
[ ] Compliance certifications (SOC 2, etc.)
[ ] Liability insurance
[ ] Track record with AI platforms
[ ] Data handling practices
[ ] Geographic data residency options
[ ] Indemnification clauses
```

### Recommended Providers

| Provider | Compliance | Indemnification | Notes |
| -------- | ---------- | --------------- | ----- |
| BrightData | SOC 2 | Yes | Enterprise focus |
| Oxylabs | SOC 2 | Yes | Good for AI platforms |
| Scrapeless | Limited | Check terms | Budget option |

## Jurisdiction Considerations

### United States

- CFAA (Computer Fraud and Abuse Act) applies
- State laws vary (California CCPA, etc.)
- hiQ precedent provides some protection for public data

### European Union

- GDPR applies to personal data
- Database Directive protects compilations
- Stricter enforcement environment

### United Kingdom

- UK GDPR post-Brexit
- Computer Misuse Act applies
- CDPA (copyright) considerations

## Disclaimer Language

Include in your application:

```
This tool monitors publicly available AI-generated responses
using official APIs where available. It does not access
private data, bypass authentication, or violate platform
terms of service. Users are responsible for ensuring their
use complies with applicable laws and platform terms.
```

## Incident Response

If you receive a cease-and-desist or ToS violation notice:

1. **Stop immediately** - Cease all related activities
2. **Preserve records** - Don't delete logs or data
3. **Consult legal counsel** - Don't respond without advice
4. **Assess scope** - Determine what data/access is involved
5. **Document compliance efforts** - Show good faith

## Regular Review

Schedule quarterly reviews:

- [ ] Check ToS updates for each platform
- [ ] Review legal developments in AI/scraping
- [ ] Audit actual usage vs. permitted usage
- [ ] Update compliance documentation
- [ ] Retrain team on policies

## Ethical Monitoring

AEO monitoring involves two distinct types of data collection with different ethical profiles:

### Bot Analytics (Observing Your Own Server)

**What it is**: Analyzing your own server access logs to see which AI bots crawl your content.

**Ethical status**: Fully ethical and legal — you own your server logs.

**What you learn**:

- Which AI crawlers visit your site (GPTBot, ClaudeBot, PerplexityBot)
- How frequently they crawl
- Which pages they access most
- Whether your content is being ingested

**No legal concerns**: This is equivalent to standard web analytics.

### Citation Tracking (Querying APIs)

**What it is**: Sending queries to AI platform APIs and analyzing whether your brand or URLs appear in responses.

**Ethical status**: Ethical when using official APIs within terms of service.

**What you learn**:

- Whether AI platforms cite your content
- How your brand is represented
- Competitor citation patterns

**Legal considerations**:

- Use official APIs only (see risk matrix above)
- Respect rate limits
- Do not store copyrighted content (only metadata: was your URL cited? Y/N)
- Do not attempt to manipulate AI responses

### Key Distinction

Bot analytics is passive observation of your own infrastructure. Citation tracking is active querying of external services. Both are legitimate when done correctly, but citation tracking requires careful compliance with platform ToS.

## Summary

**Safest approach**: Use official APIs exclusively

**Acceptable risk**: Commercial scraping services with strong compliance

**Avoid**: DIY web scraping of AI platforms

**Never**: Bypass authentication, violate robots.txt, or store copyrighted content
