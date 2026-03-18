# Separation of Concerns: Research vs Production

**Last Updated**: 2026-03-18
**Implemented Since**: Project inception (Sprint 1)
**Relevant Regulations**: CRA (change management), DSGVO (data protection), EU AI Act (testing vs deployment)

---

## Architecture Decision

CDDBS maintains two separate repositories:

| Repository | Purpose | Branch Policy |
|-----------|---------|---------------|
| `cddbs-research` | Research, experimentation, sprint planning, documentation, compliance | Feature branches from `main` |
| `cddbs-prod` | Production application (FastAPI + React + PostgreSQL) | Feature branches from `development` → `main` |

---

## Why Separate Repositories?

### 1. Risk Isolation

Research code (Jupyter notebooks, experimental scripts, prototype adapters) is inherently exploratory. It may:
- Use unpinned dependencies
- Contain debug output with sample data
- Include experimental prompts that aren't production-ready
- Have incomplete error handling

**Keeping research separate from production prevents experimental code from accidentally reaching users.**

### 2. Different Quality Standards

| Aspect | Research Repo | Production Repo |
|--------|--------------|-----------------|
| Test coverage | Focused (80+ tests on frameworks) | Comprehensive (132+ tests on all endpoints) |
| Linting | Not enforced | Ruff linting in CI |
| Documentation | Sprint plans, research notes | DEVELOPER.md (45KB), API reference |
| Dependencies | Exploratory (notebooks, visualization) | Pinned, minimal |
| CI pipeline | Schema validation, notebook checks | Full: lint + test + docs drift + secret scan + branch policy |

### 3. Compliance Clarity

| Regulation | Benefit of Separation |
|------------|----------------------|
| CRA | Production repo has full CRA-aligned CI; research repo has lighter checks appropriate for experimentation |
| DSGVO | Research notebooks may contain sample data; production code enforces data minimization |
| EU AI Act | Research contains prompt experiments; production uses reviewed, versioned prompts |

### 4. Branching Policy Differences

**Production (`cddbs-prod`)**:
```
feature/* → development → main
              ↑              ↑
         CI validates    Only development
         all checks      can merge here
```

**Research (`cddbs-research`)**:
```
feature/* → main
              ↑
         CI validates
         (lighter checks)
```

Production requires the development integration branch as a staging area. Research allows direct-to-main merges because the risk of experimental code reaching users is zero — it's a different repository.

---

## The Integration Bridge: Patches

Research findings are transferred to production via **patch files**, not direct code sharing:

```
cddbs-research                          cddbs-prod
    │                                       │
    ├── Research & prototype                │
    │                                       │
    ├── Generate patch file ────────────────┤
    │   patches/sprintN_changes.patch       │
    │                                       ├── Apply patch
    │                                       ├── Run full CI
    │                                       ├── Code review
    │                                       └── Merge to development → main
```

### Why Patches Instead of Shared Code?

1. **Explicit transfer**: Every line of code crossing from research to production is visible in a patch diff
2. **CI validation**: Production CI runs on the applied patch; any quality issues are caught
3. **Audit trail**: The patch file + integration log document exactly what changed and why
4. **No dependency coupling**: Production doesn't depend on research repo structure

### Integration Log Pattern

Each sprint produces a `docs/sprint_N_integration_log.md` documenting:
- Files added/modified
- New API endpoints
- New environment variables
- Prerequisites (which sprints must be applied first)
- Verification checklist

---

## Sprint Documentation Flow

```
Sprint Planning (research)
    │
    ├── docs/sprint_N_backlog.md      ← Tasks, acceptance criteria
    ├── docs/sprint_N_context.md      ← Architecture decisions
    │
    ▼
Implementation (prod, from development branch)
    │
    ├── Code changes on feature branch
    ├── CI validation
    ├── PR review → development → main
    │
    ▼
Sprint Close (research)
    │
    ├── patches/sprintN_changes.patch ← Exported if needed
    ├── docs/sprint_N_integration_log.md
    ├── retrospectives/sprint_N.md
    └── Updated execution plan
```

---

## Practical Benefits Observed

### Sprint 4 (Research → Production Integration)
The clean separation allowed Sprint 4 to be a focused integration sprint. Research modules (quality scorer, narrative matcher, platform adapters) were copied into production with clear boundaries. No research-only code leaked into production.

### Sprint 6 (CI Hardening)
Production CI was hardened with secret scanning, docs drift detection, and branch policy enforcement. Research CI remained lighter. If both were in one repo, the strict CI would either slow down research or be weakened for production.

### Sprint 6 (Open Source Release)
When adding LICENSE, SECURITY.md, and CONTRIBUTING.md, only the production repo needed these. Research repo maintains its own lighter governance appropriate for internal development.

---

## Reusable Practice

> **For any project with research and production components**: Separate the codebases. Use explicit integration mechanisms (patches, PRs, package publishing) to transfer validated research into production. This prevents the "research prototype becomes production system" anti-pattern that causes security and quality issues.

### Minimum Separation Checklist

- [ ] Research and production in separate repositories (or at minimum, separate CI pipelines)
- [ ] Different branch policies (research: lighter; production: stricter)
- [ ] Explicit integration mechanism with audit trail
- [ ] Production CI validates everything that enters from research
- [ ] Documentation of what was transferred and why (integration logs)
