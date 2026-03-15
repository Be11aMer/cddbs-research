---
title: "Building CDDBS: An LLM-Powered Disinformation Analysis System — Part 1: Architecture & Threat Model"
published: false
description: "How we designed a system that uses Gemini, SerpAPI, and structured intelligence tradecraft to detect disinformation narratives at scale."
tags: ai, security, python, webdev
series: "Building CDDBS"
---

## What is CDDBS?

CDDBS — the Cyber Disinformation Detection Briefing System — is an open-source intelligence analysis platform that detects disinformation narratives in media outlets and social media accounts. It ingests articles from the web, runs them through a structured LLM analysis pipeline, scores the output for quality, and matches it against a database of 18 known disinformation narratives.

The result is a professional intelligence briefing — the kind an analyst at a think tank or government agency would write — produced in under a minute.

This is the first post in a series where I'll walk through the technical architecture, the pipeline internals, the quality assurance system, and the operational infrastructure behind it. This isn't a weekend project write-up. CDDBS has been through five development sprints, 169 tests, and a production deployment on Render. The goal of this series is to show how the pieces fit together — and why we made the decisions we did.

## The Problem We're Solving

Disinformation analysis is labor-intensive. A trained analyst reviewing a single media outlet for narrative alignment might spend hours reading articles, cross-referencing known campaigns, and writing up findings with proper attribution. Scale that to dozens of outlets across multiple platforms, and you have a staffing problem that no newsroom or research lab can afford.

The core question CDDBS answers: **Can an LLM produce analyst-grade intelligence briefings if you give it the right structure, the right evidence, and the right constraints?**

The answer is yes — with caveats. The LLM (Google Gemini) is powerful at synthesis, but terrible at self-assessment. It will hallucinate confidence levels, fabricate URLs, and present speculation as fact unless you engineer around those failure modes explicitly. That engineering is the subject of this series.

## Threat Model: What We're Looking For

CDDBS tracks 18 disinformation narratives organized into 8 categories. These aren't hypothetical — they're drawn from documented campaigns catalogued by organizations like EUvsDisinfo, the Atlantic Council's DFRLab, and Stanford's Internet Observatory.

Here's the taxonomy:

| Category | Narratives | Example Keywords |
|----------|-----------|------------------|
| Anti-NATO / Western Alliance | 3 | encirclement, broken promises, Cold War relic |
| Anti-EU / European Instability | 3 | EU collapse, sanctions backfire, Islamization |
| Ukraine Conflict Revisionism | 4 | denazification, Azov, Maidan coup, biolabs |
| Western Hypocrisy | 3 | Western propaganda, Guantanamo, election fraud |
| Global South Appeals | 1 | BRICS, multipolar world, anti-colonial |
| Health Disinformation | 1 | bioweapon, Big Pharma |
| Election Interference Denial | 1 | Russiagate hoax, Steele dossier |
| Telegram Amplification | 2 | forwarding chains, censorship refugee |

Each narrative has a unique ID (e.g., `ukraine_001`), a set of detection keywords, and metadata about propagation patterns. The system doesn't just flag keywords — it counts hits, calculates a confidence level (high/moderate/low based on match density), and deduplicates across the full report text and individual articles.

This is deliberately a **signature-based** approach, not ML-based. Keyword matching is deterministic, auditable, and runs offline without a model. That matters when your users are analysts who need to explain *why* a match was flagged.

## Architecture Overview

CDDBS is a three-tier application:

```
┌─────────────────────────────┐
│   React 18 + TypeScript     │
│   MUI 6 / TanStack Query    │
│   Vite (dev) / Nginx (prod) │
└──────────────┬──────────────┘
               │ HTTP
┌──────────────▼──────────────┐
│   FastAPI + SQLAlchemy       │
│   Background task pipeline   │
│   Quality scorer + Narratives│
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│   PostgreSQL (12 tables)     │
│   Neon managed (production)  │
└─────────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
 SerpAPI              Google Gemini
 (article fetch)      (LLM analysis)
```

The backend is a FastAPI application with 34 endpoints. The frontend is a React SPA with Redux Toolkit for state and TanStack React Query for data fetching. PostgreSQL stores everything — reports, articles, quality scores, narrative matches, and tester feedback.

### The BYOK Model

CDDBS uses a "Bring Your Own Key" authentication model. Users supply their own SerpAPI and Google Gemini API keys, stored in the browser's `localStorage`. Keys are sent with each analysis request and never persisted server-side.

This is a deliberate architectural choice:

- **Cost**: We don't pay for API calls. Users operate within their own quotas.
- **Privacy**: No key management, rotation, or breach surface on our end.
- **Simplicity**: No auth layer, no user accounts, no billing.

The trade-off is onboarding friction — users need their own API keys before they can run analyses. For a tool aimed at researchers and analysts, that's an acceptable gate.

## The Pipeline at 30,000 Feet

When a user clicks "New Analysis" and submits an outlet, the system executes a 6-stage pipeline:

```
1. Article Fetch    → SerpAPI Google News (or Twitter API v2)
2. LLM Analysis     → Gemini 2.5 Flash with structured system prompt
3. Persistence      → Report + Articles stored in PostgreSQL
4. Quality Scoring  → 7-dimension rubric, 70-point scale
5. Narrative Match  → Keyword detection against 18 known narratives
6. Result Assembly  → Briefing + scorecard + matches committed to DB
```

Critically, this pipeline runs **asynchronously**. The `POST /analysis-runs` endpoint returns immediately with a report ID and `"status": "queued"`. The actual pipeline runs in a background thread. The frontend polls every 3 seconds until the report is ready.

Stages 4 and 5 — quality scoring and narrative matching — are wrapped in `try/except` blocks. If they fail, the briefing is still delivered. This is a deliberate design choice: a briefing without a quality score is infinitely more useful than no briefing at all.

## Database Schema

Twelve tables store the full lifecycle of an analysis — from article ingestion to briefing delivery and webhook alerting:

```
outlets ──< articles >── reports ──< narrative_matches
                            │
                            ├── briefings (1:1)
                            │
batches ─────────────────── ┘ (via report_ids JSON)

topic_runs ──< topic_outlet_results

raw_articles (multi-source ingestion)
event_clusters (Sprint 6+)
narrative_bursts (Sprint 6+)
webhook_configs

feedback (standalone)
```

The key design decision here is the `Report` ↔ `Briefing` relationship. A `Report` stores the raw LLM response and the final briefing text. A `Briefing` stores the structured quality scorecard. They're 1:1 linked by `report_id`.

Narrative matches are stored as individual rows — one per detected narrative per report. This makes it trivial to query "which reports matched `ukraine_001`?" across the entire database.

The `Batch` model (added in Sprint 5) groups multiple reports under a single analysis request. It tracks progress with `completed_count` and `failed_count` fields, and stores linked report IDs in a JSON column.

Sprint 6 added four more tables: `raw_articles` (multi-source feed ingestion from RSS and GDELT), `event_clusters` and `narrative_bursts` (for event intelligence, populated in Sprint 7+), and `webhook_configs` (for outbound alerting via HMAC-signed webhooks).

## What's Coming in This Series

This post covered the *what* and *why*. The next posts go deep on the *how*:

- **Part 2**: The analysis pipeline in detail — how we fetch articles, construct prompts, parse LLM output, and handle failures.
- **Part 3**: The 7-dimension quality rubric — how we score LLM output without using another LLM.
- **Part 4**: Multi-platform analysis — how Twitter API v2 and Telegram adapters normalize heterogeneous data into a common format.
- **Part 5**: Operational maturity — batch analysis, export formats, metrics, and what it takes to go from "it works on my machine" to "it works in production."
- **Part 6**: Event intelligence at scale — the Sprint 6 multi-source ingestion pipeline (RSS + GDELT), TF-IDF deduplication, and webhook alerting.

Each post will include real code, real data flows, and real architectural trade-offs. If you're building LLM-powered analysis tools — or any system where LLM output quality matters — the patterns here apply well beyond disinformation detection.

---

*CDDBS is open source: production repository is at [github.com/Be11aMer/cddbs-prod](https://github.com/Be11aMer/cddbs-prod) and the research repository is at [github.com/Be11aMer/cddbs-research](https://github.com/Be11aMer/cddbs-research).*
