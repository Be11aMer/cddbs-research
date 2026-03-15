# CDDBS-Edge: Portable Offline Briefing System

**Status**: Concept — Experiment Phase 0 in planning
**Last updated**: March 2026

---

## The Problem It Solves

> *"What happens when the cloud goes down, the API gets blocked, or you're a journalist in a country that restricts internet access?"*

Current CDDBS — like all cloud-AI briefing tools — assumes:
- Reliable internet connectivity
- Access to US/EU-hosted APIs (Gemini, SerpAPI)
- No infrastructure-level censorship

This assumption fails in documented real-world scenarios:
- **Russia / Belarus**: Deep packet inspection blocks VPN and API endpoints
- **Iran**: Throttled international bandwidth, API address blocking
- **China**: Great Firewall blocks most external AI API endpoints
- **Field reporting**: Remote locations without reliable connectivity
- **Infrastructure disruption**: Cyberattacks on cloud providers, power grid events

CDDBS-Edge answers: can we run a meaningful disinformation briefing system with **no external API calls, on a device that fits in a bag**?

---

## Core Design Concept

```
[Data Input]
  └── RSS/news articles exported to USB stick
      OR minimal wifi (RSS-only fetch, no API keys needed for feeds)

[Compute — Raspberry Pi 5, 8GB RAM]
  ├── Ollama serving Phi-3 Mini 3.8B (local LLM)
  ├── CDDBS pipeline (modified):
  │    fetch.py    → reads local article exports
  │    analyze.py  → calls localhost:11434/api/generate (Ollama, not Gemini)
  │    briefing.py → formats structured output
  └── MQTT broker (Mosquitto)
         └── publishes briefing to topic: cddbs/briefing/latest

[Display — TBD via experiment]
  ├── Option A: Waveshare 7.5" e-ink HAT (Pi GPIO)
  │            → sunlight-readable, ~0W when static, field-optimal
  ├── Option B: HDMI monitor (simpler, higher bandwidth)
  └── Option C: MQTT subscriber on phone/laptop/Home Assistant
                → wireless, most flexible for demos
```

**Decision needed**: Display approach — e-ink HAT vs MQTT external vs both.
*Both options will be prototyped to determine which serves the journalist field scenario better.*

---

## Target Hardware

**Primary target:**
- **Raspberry Pi 5** (8GB RAM) — best Pi for local LLM inference
  - ~4–6 tokens/sec with Phi-3 Mini Q4_K_M via llama.cpp
  - 300-token briefing ≈ 1–2 minutes generation time
  - ~5–8W power draw → 20,000mAh power bank = 10–12 hours field use
  - Approx. cost: ~$80 board + SD card + case

**Alternative (budget):**
- **Raspberry Pi 4** (4GB RAM) — can run Phi-3 Mini Q4 (tight but feasible)
  - Slower: ~2–3 tokens/sec
  - 300-token briefing ≈ 2–4 minutes

**Not considered (for now):**
- Orange Pi / Libre Computer — possible but Ollama support less mature
- Jetson Nano — more capable for inference but more expensive + power hungry

---

## Local Model Selection

**Primary choice: Phi-3 Mini 3.8B (Microsoft)**
- Runs comfortably on Pi 5 8GB at Q4_K_M quantization
- Designed for reasoning with small parameter count — outperforms its size on analytical tasks
- Widely supported in Ollama, active community
- Context window: 128K tokens (handles full article sets)

**Alternatives to benchmark:**
- **Gemma 2 2B** — lighter, faster, but quality step-down
- **Llama 3.2 3B** — strong general reasoning, good Ollama integration
- **Phi-3.5 Mini** — updated version of Phi-3, worth testing

**Expected quality tradeoff:**
Local 3.8B models are noticeably less capable than Gemini 2.5 Flash on nuanced reasoning. The key question (Phase 0 experiment) is: *is the local briefing quality still actionable, even if less polished?*

---

## Experiment Roadmap

### Phase 0 — Software-Only (No Hardware Required)
**Goal:** Validate whether local LLM quality is workable before hardware investment.

**Tasks:**
- [ ] Install Ollama locally on development laptop
- [ ] Pull Phi-3 Mini: `ollama pull phi3:mini`
- [ ] Modify `analyze.py` — replace Gemini API call with Ollama API call
  - Change: `client.models.generate_content(...)` → `requests.post("http://localhost:11434/api/generate", ...)`
  - Adjust prompt format for Phi-3's instruction template
- [ ] Run 3–5 test briefings using existing sample articles
- [ ] Compare output to Gemini baseline (same articles, same prompt)
- [ ] Document quality delta: what's lost, what's preserved, what's acceptable for field use

**Go/No-Go criteria for Phase 1:**
- Briefing is structurally complete (all 7 sections present)
- Narrative analysis is plausible (may miss subtlety, must not hallucinate badly)
- Quality score ≥ 45/70 (vs Gemini baseline of ~58–65/70)

---

### Phase 1 — Pi Deployment
**Goal:** Confirm the pipeline runs on target hardware at acceptable speed.

**Tasks:**
- [ ] Flash Pi 5 with Raspberry Pi OS 64-bit
- [ ] Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] Pull Phi-3 Mini, benchmark: tokens/sec, RAM usage, thermal behavior
- [ ] Transfer modified CDDBS pipeline to Pi
- [ ] Run end-to-end test (USB stick → analysis → formatted output)
- [ ] Document: speed, RAM ceiling, thermal throttling under sustained load

---

### Phase 2 — Display & Output
**Goal:** Determine the optimal output delivery method.

**Tasks:**
- [ ] Set up Mosquitto MQTT broker on Pi: `sudo apt install mosquitto`
- [ ] Modify briefing output to publish to MQTT topic: `cddbs/briefing/latest`
- [ ] Test Option A: MQTT subscriber on laptop/phone (Node-RED or MQTT Explorer)
- [ ] Test Option B: HDMI monitor (basic, validates MQTT flow)
- [ ] (Optional) Test Option C: Waveshare 7.5" e-ink HAT — requires Python driver setup
- [ ] Decision: pick primary display target based on usability and cost

---

### Phase 3 — Offline Data Ingestion
**Goal:** Solve the hardest UX problem — how does news get onto an air-gapped device?

**Design options to evaluate:**
- **USB stick workflow**: analyst downloads articles to USB on connected device, transfers to Pi
- **Minimal wifi RSS fetch**: Pi connects briefly (Tor circuit or limited wifi) to fetch RSS only — no API calls, no API keys exposed
- **Pre-loaded news cache**: Pi runs scheduled fetch when internet is available, stores articles locally for later offline analysis
- [ ] Design and document the data ingestion workflow
- [ ] Prototype the chosen option
- [ ] Security review: what metadata leaks during the brief connectivity window?

---

## Relevance to AI Trust & Governance

Building CDDBS-Edge develops knowledge and artifacts directly relevant to governance careers:

| Topic | How cddbs-edge addresses it |
|-------|----------------------------|
| **Infrastructure resilience** | Demonstrates AI systems can be designed to degrade gracefully without cloud dependency |
| **Digital sovereignty** | Practical artifact for policy discussions about AI access under censorship |
| **Access equity** | Shows that AI-assisted journalism tools can work without expensive API subscriptions |
| **Privacy-preserving AI** | Zero API calls = zero telemetry leakage to external providers |
| **Edge AI governance** | Raises questions: what governance frameworks apply to local, unmonitored AI deployment? |
| **Hardware + LLM** | Cross-disciplinary knowledge: quantization, hardware constraints, on-device inference |

This is not just a portfolio piece — it generates real research questions about AI governance at the infrastructure level that academic papers discuss but rarely implement.

---

## Open Questions

1. **Model quality floor**: What is the minimum acceptable briefing quality for a field journalist? This requires user research, not just benchmarking.
2. **Display UX**: Does an e-ink display work for multi-section briefings, or is scrolling too painful? A phone MQTT subscriber might be more practical.
3. **Update frequency**: How often would a field journalist realistically refresh news? This drives the data ingestion design.
4. **Multi-language local models**: Gemini handles non-English text well. Do small models? This matters for Russian/Farsi/Chinese-language media analysis.
5. **Security model**: What happens if the device is seized? Should briefings be stored? Encrypted? Never stored?

---

## References & Prior Art

- [llama.cpp on Raspberry Pi](https://github.com/ggerganov/llama.cpp) — the reference for local LLM on ARM
- [Ollama](https://ollama.com/) — easiest way to run local models, ARM builds available
- [Phi-3 Mini](https://azure.microsoft.com/en-us/blog/phi-3-5-mini-instruct-and-phi-3-5-moe-instruct/) — Microsoft's small reasoning model
- [Waveshare e-Paper HAT](https://www.waveshare.com/7.5inch-e-paper-hat.htm) — 7.5" e-ink display for Pi
- [Mosquitto MQTT](https://mosquitto.org/) — lightweight MQTT broker
- [EFF — Surveillance Self-Defense](https://ssd.eff.org/) — field security model for journalists (context for threat model)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Mar 2026 | Proceed with Phase 0 first | Validate model quality before hardware spend |
| Mar 2026 | Primary model: Phi-3 Mini 3.8B | Best reasoning/size tradeoff; fits Pi 5 8GB at Q4 |
| Mar 2026 | Display: both options to be prototyped | Not enough data yet to commit to e-ink vs MQTT |
