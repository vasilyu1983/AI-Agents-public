# Gemini Router Test Cases

This document contains validation test cases to verify routing logic correctness.

---

## Test Case 1: AI Agent Architecture Design
**User Input**: "Design a production-ready AI agent for customer support with RAG and tool calling"
**Expected Route**: Agent: ai-agents-builder | Skill: ai-agents
**Rationale**: Task is agent architecture design, requires agent patterns and RAG integration
**Priority Rule**: 2 (Task-specific routing)

---

## Test Case 2: Backend API Development
**User Input**: "Create a REST API for user authentication with JWT and PostgreSQL"
**Expected Route**: Agent: backend-engineer | Skill: software-backend
**Rationale**: Backend API development with specific stack (JWT, PostgreSQL)
**Priority Rule**: 3 (Domain-specific routing - backend stack)

---

## Test Case 3: Frontend Component Development
**User Input**: "Build a Next.js dashboard with charts using shadcn/ui and Tailwind CSS"
**Expected Route**: Agent: frontend-engineer | Skill: software-frontend
**Rationale**: Frontend development with Next.js stack
**Priority Rule**: 3 (Domain-specific routing - frontend stack)

---

## Test Case 4: SQL Query Optimization
**User Input**: "Optimize this slow PostgreSQL query and suggest indexes"
**Expected Route**: Agent: sql-engineer | Skill: data-sql-optimization
**Rationale**: SQL performance tuning and indexing task
**Priority Rule**: 2 (Task-specific routing for SQL optimization)

---

## Test Case 5: LLM Fine-Tuning
**User Input**: "Fine-tune LLaMA 2 7B for medical question answering with LoRA"
**Expected Route**: Agent: llm-engineer | Skill: ai-llm
**Rationale**: LLM fine-tuning with dataset preparation and evaluation
**Priority Rule**: 2 (Task-specific routing for LLM fine-tuning)

---

## Test Case 6: RAG Pipeline Design
**User Input**: "Design a RAG system for legal document retrieval with reranking"
**Expected Route**: Agent: llm-engineer | Skill: ai-rag
**Rationale**: RAG pipeline architecture (LLM-focused use case)
**Priority Rule**: 2 (Task-specific routing for RAG)

---

## Test Case 7: Mobile App Development
**User Input**: "Build an iOS app with SwiftUI using MVVM architecture and Core Data"
**Expected Route**: Agent: mobile-engineer | Skill: software-mobile
**Rationale**: iOS-specific development with native stack
**Priority Rule**: 3 (Domain-specific routing - mobile iOS)

---

## Test Case 8: DevOps Infrastructure
**User Input**: "Create Terraform modules for AWS EKS cluster with monitoring and autoscaling"
**Expected Route**: Agent: devops-engineer | Skill: ops-devops-platform
**Rationale**: Infrastructure as code with Kubernetes and cloud
**Priority Rule**: 3 (Domain-specific routing - DevOps/IaC)

---

## Test Case 9: Data Science Modeling
**User Input**: "Build a churn prediction model with feature engineering and evaluation"
**Expected Route**: Agent: data-scientist | Skill: ai-ml-data-science
**Rationale**: End-to-end data science workflow (EDA, features, modeling)
**Priority Rule**: 3 (Domain-specific routing - data science)

---

## Test Case 10: Prompt Engineering
**User Input**: "Optimize this prompt for structured JSON extraction with validation"
**Expected Route**: Agent: prompt-engineer | Skill: ai-prompt-engineering
**Rationale**: Prompt optimization for structured outputs
**Priority Rule**: 2 (Task-specific routing for prompt engineering)

---

## Test Case 11: PRD Validation
**User Input**: "Review this PRD for completeness and suggest improvements"
**Expected Route**: Agent: prd-architect | Skill: docs-ai-prd
**Rationale**: PRD validation and quality checking using PRD skill
**Priority Rule**: 2 (Task-specific routing for PRD work)

---

## Test Case 12: Time Series Forecasting
**User Input**: "Forecast quarterly sales using ARIMA and Prophet with backtesting"
**Expected Route**: Agent: data-scientist | Skill: ai-ml-timeseries
**Rationale**: Time series specific forecasting task
**Priority Rule**: 2 (Task-specific routing for time series)

---

## Test Case 13: LLM Inference Optimization
**User Input**: "Optimize vLLM inference for Mistral 7B with quantization and batching"
**Expected Route**: Agent: llm-engineer | Skill: ai-llm-inference
**Rationale**: LLM serving and inference optimization
**Priority Rule**: 2 (Task-specific routing for LLM inference)

---

## Test Case 14: ML Model Deployment
**User Input**: "Deploy this scikit-learn model as a FastAPI endpoint with monitoring"
**Expected Route**: Agent: data-scientist | Skill: ai-mlops
**Rationale**: ML model deployment with API serving
**Priority Rule**: 2 (Task-specific routing for ML deployment)

---

## Test Case 15: Security Review (ML System)
**User Input**: "Audit this LLM chatbot for prompt injection vulnerabilities"
**Expected Route**: Agent: llm-engineer | Skill: ai-mlops
**Rationale**: ML/LLM security audit for safety threats
**Priority Rule**: 2 (Task-specific routing for ML security)

---

## Test Case 16: Technical SEO Audit
**User Input**: "Audit our SaaS marketing site for schema markup, crawl budget, and page speed issues"
**Expected Route**: Agent: leads-strategist | Skill: marketing-seo-technical
**Rationale**: Technical SEO request; marketing domain with SEO skill
**Priority Rule**: 2 (Task-specific routing for SEO)

---

## Test Case 17: Web E2E Automation
**User Input**: "Create Playwright tests for checkout flow with fixtures and visual comparisons"
**Expected Route**: Agent: test-architect | Skill: qa-testing-playwright
**Rationale**: Browser E2E automation task mapped to testing skill
**Priority Rule**: 2 (Task-specific routing for testing)

---

## Test Case 18: Document Automation
**User Input**: "Build an OCR pipeline to extract tables from PDFs and export to XLSX"
**Expected Route**: Agent: ai-agents-builder | Skill: document-pdf
**Rationale**: PDF-focused document workflow requiring OCR and extraction
**Priority Rule**: 2 (Task-specific routing for document automation)

---

## Edge Cases

### Edge Case 1: Explicit Agent Override
**User Input**: "agent: backend-engineer | Build a recommendation system"
**Expected Route**: Agent: backend-engineer | Skill: software-backend  
**Rationale**: User explicitly specified agent (Priority 1), even though task might fit data-scientist better
**Priority Rule**: 1 (Explicit user override)

---

### Edge Case 2: Explicit Skill Override
**User Input**: "skill: ai-rag | Optimize document chunking strategy"  
**Expected Route**: Agent: llm-engineer | Skill: ai-rag  
**Rationale**: User specified skill, router selects matching agent (llm-engineer uses ai-rag)  
**Priority Rule**: 1 (Explicit user override)

---

### Edge Case 3: Both Agent and Skill Override
**User Input**: "agent: frontend-engineer | skill: ops-devops-platform | Set up CI/CD for Next.js app"  
**Expected Route**: Agent: frontend-engineer | Skill: ops-devops-platform  
**Rationale**: User specified both, use exact combination even if unusual pairing
**Priority Rule**: 1 (Explicit user override)

---

### Edge Case 4: Ambiguous Multi-Domain Task
**User Input**: "Build a full-stack app with Next.js frontend and Node.js backend API"
**Expected Route**: Agent: backend-engineer | Skill: software-backend OR Agent: frontend-engineer | Skill: software-frontend  
**Rationale**: Multi-domain task; router chooses primary component (backend for API architecture, or could suggest breaking into subtasks)
**Priority Rule**: 3 (Domain-specific routing, choose most critical component)
**Notes**: Could also route to fullstack-dev command if available

---

### Edge Case 5: No Clear Technology Match
**User Input**: "Help me understand dependency injection patterns"
**Expected Route**: Agent: backend-engineer | Skill: software-backend  
**Rationale**: General software architecture question, fallback to backend (most likely context for DI)
**Priority Rule**: 4 (Default fallback)

---

### Edge Case 6: Cross-Domain with Security Focus
**User Input**: "Review this React component for XSS vulnerabilities"
**Expected Route**: Agent: frontend-engineer | Skill: software-frontend  
**Rationale**: Frontend security review (XSS is frontend concern, not ML security)
**Priority Rule**: 2 (Task-specific routing - code review) + 3 (Domain-specific - frontend)
**Notes**: Frontend-engineering skill includes security best practices

---

### Edge Case 7: Missing Skill Scenario
**User Input**: "Design a blockchain smart contract system"
**Expected Route**: Agent: backend-engineer | Skill: none
**Rationale**: No blockchain-specific skill exists; use general backend agent without skill
**Priority Rule**: 4 (Default fallback, conflict resolution: "skill missing")
**Notes**: Router should note limited blockchain expertise

---

### Edge Case 8: Conflicting Signals
**User Input**: "Optimize SQL query performance in a Python ML pipeline"
**Expected Route**: Agent: sql-engineer | Skill: data-sql-optimization  
**Rationale**: Primary task is SQL optimization (more specialized than general ML pipeline work)
**Priority Rule**: 2 (Task-specific routing) + Conflict resolution: choose most specialized
**Notes**: SQL optimization is the bottleneck, takes precedence over ML context

---

## Priority Rule Coverage

**Priority 1 (Explicit Override)**: Test Cases - Edge Cases 1, 2, 3
**Priority 2 (Task-Specific)**: Test Cases 1, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
**Priority 3 (Domain-Specific)**: Test Cases 2, 3, 7, 8, Edge Case 4
**Priority 4 (Fallback)**: Edge Cases 5, 7

---

## Domain Coverage

- **AI Systems**: Test Cases 1, 6, 18
- **Backend**: Test Cases 2, Edge Cases 4, 5, 7
- **Frontend**: Test Case 3, Edge Case 6
- **Database**: Test Case 4, Edge Case 8
- **LLM**: Test Cases 5, 6, 13, 15
- **Mobile**: Test Case 7
- **Infrastructure**: Test Case 8
- **Data Science**: Test Cases 9, 12, 14
- **Product**: Test Case 11
- **Prompting**: Test Case 10
- **Marketing/SEO**: Test Case 16
- **Testing/E2E**: Test Case 17
- **Documents/OCR**: Test Case 18


---

## Notes for Router Implementers

1. **Conflict Resolution**: When multiple agents could apply (Edge Case 4, 8), choose the most specialized for the primary task mentioned first
2. **Skill-Agent Pairing**: Some agents use multiple skills (llm-engineer uses 4 different skills depending on task)
3. **Override Precedence**: Always honor explicit user overrides even if pairing seems unusual (Edge Case 3)
4. **Missing Components**: Gracefully handle missing skills/agents by using available components (Edge Case 7)
5. **Multi-Step Tasks**: For complex multi-domain tasks, suggest breaking into subtasks or use most critical component
6. **Security Context**: Security reviews route to domain-specific agent (frontend for XSS, llm-engineer for prompt injection)
