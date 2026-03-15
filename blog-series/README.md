# Building CDDBS — Blog Series

Technical blog series about the Counter-Disinformation Database Briefing System.
Written for [dev.to](https://dev.to) publication.

## Posts

| # | Title | Focus |
|---|-------|-------|
| 1 | [Architecture & Threat Model](01-architecture-and-threat-model.md) | System overview, 18-narrative threat model, BYOK auth, database schema |
| 2 | [Inside the Analysis Pipeline](02-the-analysis-pipeline.md) | Article fetch, prompt engineering, LLM call, JSON parsing, async execution |
| 3 | [Scoring LLM Output Without Another LLM](03-quality-scoring-and-narratives.md) | 7-dimension quality rubric, narrative matching, evidence typing |
| 4 | [Multi-Platform Disinformation Detection](04-multi-platform-analysis.md) | Twitter/Telegram adapters, platform routing, cross-platform analysis |
| 5 | [From Prototype to Production](05-operational-maturity.md) | Batch analysis, export formats, metrics, production engineering |

## Publishing

All posts use dev.to frontmatter format. Set `published: true` when ready to publish.

Posts form a linked series via the `series: "Building CDDBS"` frontmatter field.

## Future Posts

As development continues past Sprint 5, additional posts may cover:
- Telegram Bot API live integration
- ML-based narrative matching
- Real-time monitoring and alerting
- Cross-platform identity correlation
- Frontend dashboard and visualization deep dives
