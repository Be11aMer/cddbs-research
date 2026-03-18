# CDDBS Compliance Practices

**Project**: Cyber Disinformation Detection Briefing System (CDDBS)
**Last Updated**: 2026-03-18
**Context**: Practical compliance measures implemented across Sprints 1-7

---

## Purpose

This folder documents the **practical compliance measures** implemented in the CDDBS project. These are not theoretical frameworks — they are concrete engineering practices, CI/CD configurations, and architectural decisions that address EU regulatory requirements.

The goal is to create **reusable principles** that can be applied to any software project facing similar compliance obligations, particularly as the **EU Cyber Resilience Act (CRA) enforcement begins in summer 2026**.

---

## Documents

| Document | Description |
|----------|-------------|
| [EU Regulatory Landscape](./eu_regulatory_landscape.md) | Overview of DSGVO, CRA, and EU AI Act as they apply to CDDBS |
| [CI/CD Compliance Pipeline](./ci_cd_compliance_pipeline.md) | Secret detection, documentation drift, branch policy enforcement |
| [Data Protection (DSGVO)](./data_protection_dsgvo.md) | BYOK architecture, data minimization, no PII storage |
| [Cyber Resilience Act (CRA)](./cyber_resilience_act_cra.md) | Vulnerability handling, SBOM readiness, update mechanism, documentation |
| [EU AI Act](./eu_ai_act.md) | Transparency, human oversight, risk classification for AI-assisted analysis |
| [Separation of Concerns](./separation_of_concerns.md) | Research vs production repo separation and why it matters |
| [Sprint-by-Sprint Compliance Log](./sprint_compliance_log.md) | What was done in each sprint from a compliance perspective |

---

## Key Principle

> **Compliance is not a checkbox exercise — it's an engineering discipline.**
>
> Every measure documented here was implemented because it makes the system more secure, more maintainable, and more trustworthy. The regulatory alignment is a natural consequence of good engineering, not the other way around.

---

## Applicable Regulations

| Regulation | Enforcement Date | Relevance to CDDBS |
|------------|-----------------|---------------------|
| **DSGVO** (GDPR) | In force since May 2018 | Personal data processing, BYOK architecture, data minimization |
| **EU Cyber Resilience Act (CRA)** | Core obligations: Sep 2026, Full: Sep 2027 | Vulnerability handling, security-by-design, SBOM, documentation |
| **EU AI Act** | Risk-based obligations: Aug 2025–Aug 2027 | AI system transparency, human oversight, risk assessment |

---

## How to Use This Documentation

1. **For CDDBS contributors**: Understand why certain architectural decisions were made and what compliance requirements they satisfy
2. **For other projects**: Adapt the practices documented here to your own codebase — the CI/CD pipeline, branching strategy, and data protection patterns are directly reusable
3. **For auditors/reviewers**: This folder provides evidence of compliance-by-design throughout the development lifecycle
