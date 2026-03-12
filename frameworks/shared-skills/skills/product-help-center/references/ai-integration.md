# AI Integration

AI chatbot architecture, RAG pipelines, and platform integrations for help centers.

## Contents

- Modern AI Support Architecture (2025-2026)
- RAG Pipeline Design
- Semantic Search Setup
- AI-Friendly Content Writing
- Memory-Rich AI (2026 Trend)
- Agentic AI Capabilities
- Platform-Specific AI Setup
- Escalation & Handoff
- Monitoring & Optimization

## Modern AI Support Architecture (2025-2026)

### AI-First Support Flow

```
AI-FIRST SUPPORT FLOW (2025-2026)

User query
  -> Intent classification (question vs task, topic, urgency)
  -> Semantic search (RAG) (embedding, vector search, retrieval)
  -> Response generation (answer, citations/links, confidence score)

If confidence is high: direct answer + sources
If confidence is medium: answer + "Was this helpful?"
If confidence is low: ask a clarifying question or escalate
```

### Resolution Types

| Type | AI Action | Example |
|------|-----------|---------|
| **Informational** | Answer from KB | "What are your pricing plans?" |
| **Navigational** | Link to resource | "Where do I find invoices?" |
| **Transactional** | Execute task | "Cancel my subscription" |
| **Diagnostic** | Troubleshoot | "Why isn't my export working?" |
| **Escalation** | Hand to human | "I want to speak to a manager" |

## RAG Pipeline Design

### Document Chunking Strategy

```
CHUNKING PARAMETERS

Chunk size: 500-1000 tokens (optimal for retrieval)
Overlap: 50-100 tokens (preserve context)
Boundaries: Respect section headers, paragraphs

CHUNKING METHODS

1. Fixed-size: Simple, consistent
2. Semantic: Split by meaning (paragraphs, sections)
3. Hierarchical: Parent-child relationships

RECOMMENDED: Semantic chunking with header preservation

EXAMPLE

Original article (2000 tokens):
- Chunk 1: Title + Intro (400 tokens)
- Chunk 2: Section 1 (500 tokens)
- Chunk 3: Section 2 (500 tokens)
- Chunk 4: Section 3 + Conclusion (600 tokens)

Metadata per chunk:
- article_id
- section_title
- position (1/4, 2/4, etc.)
- url
- last_updated
```

### Embedding Model Selection

| Model | Dimensions | Speed | Quality | Cost |
|-------|------------|-------|---------|------|
| OpenAI text-embedding-3-small | 1536 | Fast | Good | Low |
| OpenAI text-embedding-3-large | 3072 | Medium | Best | Medium |
| Cohere embed-v3 | 1024 | Fast | Good | Low |
| Voyage-2 | 1024 | Fast | Excellent | Medium |
| Local (e5-large-v2) | 1024 | Varies | Good | Free |

**Recommendation**: Start with text-embedding-3-small, upgrade if quality issues.

### Vector Database Options

| Database | Best For | Managed Option |
|----------|----------|----------------|
| Pinecone | Production, scaling | Yes |
| Weaviate | Hybrid search | Yes (Cloud) |
| Qdrant | Self-hosted, filtering | Yes (Cloud) |
| Chroma | Prototyping, local | No |
| pgvector | PostgreSQL integration | Via Supabase |

### Retrieval Configuration

```
RETRIEVAL PARAMETERS

Top-K: 3-5 chunks (balance relevance vs. context)
Similarity threshold: 0.7-0.8 (filter weak matches)
Reranking: Yes (improves precision)

HYBRID SEARCH (Recommended)

Combine:
1. Semantic search (70% weight) - meaning
2. Keyword search (30% weight) - exact matches

Benefits:
- Catches exact error messages
- Handles product names, codes
- Better coverage than semantic alone
```

### Context Assembly

```
PROMPT TEMPLATE

You are a helpful support assistant for [Product].
Answer the user's question using ONLY the provided context.
If the context doesn't contain the answer, say so.
Always cite your sources.

Context:
---
{retrieved_chunks}
---

User Question: {query}

Instructions:
- Be concise and direct
- Use bullet points for steps
- Include relevant links
- If unsure, offer to connect with human support
```

## Semantic Search Setup

### Query Processing

```
QUERY ENHANCEMENT

1. Spell correction
   "passowrd reset" -> "password reset"

2. Synonym expansion
   "cost" -> "cost OR pricing OR price"

3. Query rewriting (LLM)
   "it's not working" -> "troubleshooting [detected feature]"

4. Intent extraction
   "how do I..." -> how-to intent
   "why is..." -> troubleshooting intent
   "what is..." -> conceptual intent
```

### Search Result Ranking

```
RANKING SIGNALS

1. Vector similarity score (0.0-1.0)
2. Keyword match (BM25)
3. Recency boost (newer content)
4. Popularity (view count)
5. Manual boost (featured content)

COMBINED SCORE

final_score = (
    0.5 * semantic_score +
    0.3 * keyword_score +
    0.1 * recency_score +
    0.1 * popularity_score
)
```

### Handling Edge Cases

| Scenario | Detection | Response |
|----------|-----------|----------|
| Off-topic | Low similarity scores | "I can help with [Product] questions..." |
| Ambiguous | Multiple high-scoring topics | "Did you mean X or Y?" |
| No results | All scores < threshold | "I couldn't find info on that. Let me connect you..." |
| Outdated query | References old feature | "That feature is now called X..." |

## AI-Friendly Content Writing

### Structure for AI Consumption

```
CONTENT RULES FOR RAG

DO:
- Clear, keyword-rich headings
- One concept per paragraph
- Explicit step numbering
- Tables for structured data
- Exact error messages (searchable)
- FAQ format (question as heading)

DON'T:
- Ambiguous pronouns ("it", "this")
- Implicit assumptions
- Marketing fluff in support docs
- Information buried in paragraphs
- Duplicate content across articles
```

### Metadata for AI

```markdown
ARTICLE FRONTMATTER

---
title: How to Reset Your Password
description: Step-by-step guide to reset password via email or phone
keywords: [password, reset, forgot, login, access]
category: account/security
audience: all-users
difficulty: beginner
last_updated: 2025-01-15
related: [enable-2fa, account-recovery, login-issues]
---
```

### Answer Extraction Optimization

```
STRUCTURE FOR DIRECT ANSWERS

Bad (AI must parse):
"You can find your API key in several places.
One option is the dashboard. Another is the
settings page under API section."

Good (AI extracts easily):
"Find your API key:
1. Go to Settings > API
2. Click 'Reveal Key'
3. Copy the key

Alternative: Dashboard > Quick Actions > API Key"
```

## Memory-Rich AI (2026 Trend)

Unlike stateless chatbots, memory-rich AI retains context across sessions for faster, more personalized support.

### Key Capabilities

```text
MEMORY-RICH AI BENEFITS

1. Context Retention
   - Remember previous conversations
   - Track user preferences
   - Recall past issues/resolutions

2. Personalization at Scale
   - Tailored responses based on history
   - Proactive suggestions from patterns
   - Reduced "repeat yourself" frustration

3. Faster Resolution
   - Skip re-identification steps
   - Reference previous context
   - Build on prior interactions
```

### Implementation Pattern

```text
MEMORY ARCHITECTURE

Session Start:
1. Retrieve user profile from CRM
2. Fetch last 5 conversation summaries from vector DB
3. Load relevant context into system prompt

During Conversation:
4. Store key facts extracted by LLM
5. Update preference signals
6. Track resolution outcomes

Session End:
7. Generate conversation summary
8. Store embeddings for future retrieval
9. Update user profile with new signals

STORAGE OPTIONS

- Short-term: Redis (session data, 24hr TTL)
- Long-term: Vector DB (conversation embeddings)
- Structured: PostgreSQL (user profiles, preferences)
```

### Memory Retrieval Query

```python
# Example: Retrieve relevant past context
def get_user_memory(user_id: str, current_query: str, limit: int = 5):
    # 1. Get user profile
    profile = db.get_user_profile(user_id)

    # 2. Semantic search past conversations
    query_embedding = embed(current_query)
    past_contexts = vector_db.search(
        collection="conversations",
        filter={"user_id": user_id},
        vector=query_embedding,
        limit=limit
    )

    # 3. Assemble memory context
    return {
        "profile": profile,
        "past_interactions": past_contexts,
        "preferences": profile.get("preferences", {})
    }
```

## Agentic AI Capabilities

### Task Execution (2025-2026)

```
AGENTIC ACTIONS

Level 1: Information retrieval
- Search knowledge base
- Summarize articles
- Provide links

Level 2: Simple actions
- Create support ticket
- Check order status
- Look up account info

Level 3: Transactional
- Process refund
- Cancel subscription
- Update account details

Level 4: Complex workflows
- Book appointment
- Escalate with context
- Multi-system lookup
```

### Tool Integration (Function Calling)

```python
TOOL DEFINITIONS (Example)

tools = [
    {
        "name": "check_order_status",
        "description": "Check the status of a customer order",
        "parameters": {
            "order_id": {"type": "string", "required": True}
        }
    },
    {
        "name": "process_refund",
        "description": "Process a refund for an order",
        "parameters": {
            "order_id": {"type": "string", "required": True},
            "reason": {"type": "string", "required": True},
            "amount": {"type": "number", "required": False}
        }
    },
    {
        "name": "create_ticket",
        "description": "Create a support ticket for human review",
        "parameters": {
            "subject": {"type": "string", "required": True},
            "description": {"type": "string", "required": True},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]}
        }
    }
]
```

### Model Context Protocol (MCP)

```
MCP INTEGRATION (2025)

Purpose: Standardized protocol for AI-to-tool communication

Benefits:
- Plug-and-play tool connections
- Consistent authentication
- Built-in safety guardrails

Use cases:
- Connect AI to CRM (Salesforce, HubSpot)
- Access order management systems
- Query internal databases
- Trigger workflow automation
```

## Platform-Specific AI Setup

### Zendesk AI

```
ZENDESK AI FEATURES

1. Answer Bot
   - Suggests articles during ticket creation
   - Auto-resolve common questions
   - Learns from agent responses

2. Generative AI (2024+)
   - Draft article summaries
   - Suggest article updates
   - Tone adjustment

3. Intelligent Triage
   - Auto-categorize tickets
   - Priority prediction
   - Agent routing

SETUP STEPS

1. Enable AI in Admin > AI > Bots
2. Train on knowledge base
3. Set confidence thresholds
4. Configure escalation rules
5. Monitor resolution rates
```

### Intercom Fin AI

```
FIN AI FEATURES

1. Resolution
   - Answers from your content
   - Multi-turn conversations
   - Task execution (with tools)

2. Sources
   - Help Center articles
   - Website content
   - Custom data sources

3. Behavior
   - Customizable persona
   - Handoff rules
   - Business hours

PRICING

$0.99 per resolution
Resolution = AI successfully answers without human

SETUP STEPS

1. Install Fin (Settings > Fin)
2. Connect content sources
3. Test in Sandbox
4. Set live traffic %
5. Monitor Fin reports
```

### Freshdesk Freddy AI

```
FREDDY AI FEATURES

1. Auto-suggest
   - Canned responses
   - Solution articles
   - Similar tickets

2. Ticket classification
   - Category prediction
   - Priority assignment
   - Group routing

3. Customer-facing bot
   - Self-service answers
   - Ticket deflection
   - Agent handoff

INCLUDED IN: Pro ($49) and Enterprise plans

SETUP STEPS

1. Admin > Freddy > Enable
2. Train on ticket history
3. Configure bot flows
4. Set escalation triggers
5. Review suggestions quality
```

### Custom AI Implementation

```
BUILD YOUR OWN (Stack)

Frontend:
- Chat widget (custom or open-source)
- WebSocket for real-time

Backend:
- FastAPI / Node.js
- Message queue (Redis)
- Session management

AI Layer:
- LLM (Claude, GPT-4, Llama)
- RAG pipeline
- Function calling

Vector DB:
- Pinecone / Qdrant / pgvector

Integrations:
- Helpdesk API (tickets)
- CRM API (customer data)
- Webhooks (notifications)
```

## Escalation & Handoff

### Escalation Triggers

```
AUTO-ESCALATE WHEN

Confidence-based:
- AI confidence < 0.5
- Multiple failed attempts (>2)
- User frustration detected

Content-based:
- Billing disputes
- Legal/compliance
- Security incidents
- VIP customers

Explicit:
- User requests human
- Keywords: "speak to agent", "manager"
```

### Handoff Best Practices

```
SEAMLESS HANDOFF

1. Context transfer
   - Full conversation history
   - AI's attempted answers
   - Detected intent
   - Customer info

2. Warm introduction
   "[Agent name] will continue helping you.
   I've shared our conversation so you won't
   need to repeat anything."

3. No dead ends
   - Always offer alternative if no agents
   - Callback option
   - Email follow-up
```

### Human-AI Collaboration

```
AGENT ASSIST FEATURES

1. Suggested responses
   - Based on conversation context
   - From knowledge base
   - From similar resolved tickets

2. Real-time guidance
   - Policy reminders
   - Upsell opportunities
   - Compliance warnings

3. Auto-summarization
   - Ticket summary after resolution
   - Key points extraction
   - Follow-up suggestions
```

## Monitoring & Optimization

### AI Performance Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Resolution rate | % resolved without human | 60-80% |
| Containment rate | % stayed in AI flow | 70-85% |
| Accuracy | Correct answers (sampled) | >90% |
| CSAT (AI) | User satisfaction with AI | >75% |
| Escalation rate | % transferred to human | 15-30% |
| Avg. turns to resolution | Conversation length | <4 |

### Quality Assurance

```
AI QA PROCESS

Weekly:
- Review 50 random AI conversations
- Check accuracy of answers
- Identify hallucinations
- Flag edge cases

Monthly:
- Update content gaps found
- Retrain on new content
- Adjust confidence thresholds
- Review escalation patterns

Quarterly:
- Full accuracy audit
- Benchmark against competitors
- User satisfaction survey
- Cost-benefit analysis
```

### Continuous Improvement

```
FEEDBACK LOOP

1. Collect signals
   - Thumbs up/down
   - "Was this helpful?"
   - Escalation after AI answer
   - User corrections

2. Analyze patterns
   - Common failure modes
   - Missing content topics
   - Misunderstood queries

3. Improve
   - Add/update content
   - Tune prompts
   - Adjust thresholds
   - Add synonyms
```
