# CDDBS Sprint 1 Quick-Start Guide

**Sprint**: 1 - Briefing Format Redesign
**Duration**: February 3 - February 16, 2026
**Version Target**: v1.1.0

---

## Sprint Goal

Redesign the CDDBS intelligence briefing format based on professional intelligence analysis standards. Deploy v1.1.0 with enhanced briefing output tested on 10+ analyses with beta analyst feedback.

## Sprint 1 Success Criteria

- v1.1.0 deployed to staging
- New briefing format tested on 10+ analyses
- 2-3 beta analysts provide initial feedback
- Template validated: "Would I trust this?"

---

## Task Overview

### Infrastructure (Tasks 1.1-1.3)
- [x] 1.1 - Repository and project setup
- [ ] 1.2 - CI/CD pipeline (GitHub Actions)
- [ ] 1.3 - Database migration (Supabase)

### Research & Design (Tasks 2.1-2.2)
- [ ] 2.1 - Intelligence briefing format analysis (10 briefings)
- [ ] 2.2 - CDDBS template design (JSON schema + mockup)

### Implementation (Tasks 2.3-2.8)
- [ ] 2.3 - Backend: generate new briefing format
- [ ] 2.4 - System prompt revision (v1.1)
- [ ] 2.5 - Quality testing (10 RT analyses)
- [ ] 2.6 - Frontend UI update
- [ ] 2.7 - Deploy to staging
- [ ] 2.8 - Beta testing (2-3 analysts)

### Validation (Tasks 2.9-2.10)
- [ ] 2.9 - Collect beta feedback
- [ ] 2.10 - Sprint 1 retrospective

---

## Repository Structure

```
cddbs-research-draft/
├── research/                    # Research notebooks
│   └── briefing_format_analysis.ipynb
├── templates/                   # Briefing templates
│   └── intelligence_briefing.md
├── schemas/                     # JSON schemas
│   └── briefing_v1.json
├── retrospectives/              # Sprint retrospectives
├── docs/                        # Documentation
│   ├── cddbs_execution_plan.md
│   └── sprint_1_quickstart.md
└── README.md
```

---

## Repository Rules

- **NEVER** push to `cddbs-research` (public)
- **ALWAYS** push to `cddbs-research-draft` (working repo)
- Production code goes to `cddbs-prod` (Codeberg)

## Cost Management

- Database: Supabase free tier (500MB, no credit card)
- Render: Free tier (750 hrs/month)
- Gemini API: Monitor usage (15 RPM free tier)
