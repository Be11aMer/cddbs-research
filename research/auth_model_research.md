# Authentication Model Research
## Proof, Assertion, and Trust Propagation in CDDBS

**Status**: Active research — Sprint 10
**Last Updated**: 2026-04-02
**Companion code**: [`auth_experiments/`](auth_experiments/)
**Production auth target**: Sprint 10 (API key), Sprint 11 (passkeys + session tokens)

---

## The Core Question

Standard authentication tutorials teach you *what* to implement. This research asks *why* the constraints exist — by building from first principles and observing where things break.

The central distinction is between two fundamentally different operations:

**Proving identity** — a client demonstrates, in real time, that it possesses a secret. No pre-issued artifact. No offline verification possible. The verifier must be present.

**Asserting identity** — a trusted authority issues a self-contained statement that was produced earlier. The verifier checks the statement's integrity without contacting the authority. Works offline. Revocation is bounded by the statement's lifetime.

Every real-world auth system is a composition of these two operations. Understanding the boundary between them — when each is appropriate, and what fails when you use one where you need the other — is the goal of this research.

---

## Why This Matters for CDDBS

This is not purely academic. CDDBS has two deployment contexts with different properties:

| Context | Network | Auth service available? | What survives? |
|---------|---------|------------------------|----------------|
| Cloud (cddbs-prod) | Always-on | Yes | Either proof or assertion works |
| Edge (CDDBS-Edge) | Intermittent / offline | No | Only self-verifiable assertions |

The edge deployment forces a concrete answer to an abstract question: if the auth service is offline, what can the system still trust? The answer shapes not just Edge auth, but how the cloud system issues credentials that Edge can verify without calling home.

The constraints are identical to zero-trust environments: the auth service becomes an **issuer**, the core system becomes a **verifier**, and the issued artifact must be self-contained and cryptographically unforgeable.

---

## The Three-Layer Model

```
CLIENT                   AUTH SERVICE              CORE SYSTEM
  │                           │                         │
  │──── 1. PROOF ────────────▶│                         │
  │    (challenge-response,   │                         │
  │     proves key possession)│                         │
  │                           │                         │
  │◀─── 2. ASSERTION ─────────│                         │
  │    (signed token,         │                         │
  │     short-lived,          │                         │
  │     self-verifiable)      │                         │
  │                           │                         │
  │──── 3. VERIFICATION ──────────────────────────────▶│
       (present assertion,                              │
        core validates without                         │
        calling auth service)                          │
```

**Proof** establishes identity — only the auth service needs to see this.
**Assertion** propagates identity — auth service issues it, everything else verifies it.
**Verification** enforces identity — works without the auth service being present.

---

## Experiment Overview

Three experiments, each building on the previous. Each includes a "break it" phase where you deliberately exploit weaknesses and observe what fails.

### Experiment 1 — Raw Proof
**Goal**: Implement the minimum viable challenge-response. Understand what a signature proves and what it doesn't.

**You will implement**:
- Server: generate a challenge
- Client: sign the challenge with Ed25519
- Server: verify the signature against a known public key
- Attack simulations: replay and redirect

**You will discover**: a signature on a challenge proves key possession, but nothing about which service asked, when, or for what purpose. You will re-derive the minimum viable signed payload structure by necessity.

**Maps to**: WebAuthn `clientDataJSON`, why it contains `type`, `origin`, `challenge`, and `crossOriginFlag`.

### Experiment 2 — Assertion Layer
**Goal**: Convert a valid proof into a self-contained signed token. Understand offline verification.

**You will implement**:
- Auth service: issue a signed token (CDDBS token format, Ed25519)
- Verifier: validate the token without calling the auth service
- Simulate auth service going offline — observe what breaks and what doesn't
- Observe: proof establishment breaks; assertion verification continues

**You will discover**: the issuer and verifier need to share exactly one thing — the public key. Everything else (the identity, claims, expiry) can be encoded in the token and verified offline. This is the key insight behind every public-key-based token format.

**Maps to**: JWT with RS256/EdDSA, PASETO v4.public, OIDC ID tokens.

### Experiment 3 — Failure Modes and Key Binding
**Goal**: Understand revocation, key compromise, and token theft under real conditions.

**You will implement**:
- Token theft simulation: stolen token, varying TTLs, observe damage window
- Key compromise: rotate the signing key, observe which tokens survive
- DPoP binding: bind a token to the client's public key, replay it without the key

**You will discover**: offline verification makes revocation probabilistic and time-bounded. The only reliable revocation mechanism is key rotation (all tokens signed by the old key become invalid). Binding a token to a client key (proof of possession) eliminates the "stolen token" threat class — the token is useless without the corresponding private key.

**Maps to**: RFC 9449 (DPoP), token binding, certificate revocation philosophy.

---

## Expected Discoveries by Experiment

### From Experiment 1
1. **The replay problem**: a valid `(challenge, signature)` pair can be reused unless the challenge is nonce-based and single-use
2. **The redirect problem**: a signature produced for service A can be presented to service B unless the target service is bound into the signed data
3. **The timing problem**: a proof has no inherent expiry unless a timestamp is included and checked
4. **Minimum viable payload**: `{nonce, service_id, timestamp, intent}` — each field closes a specific attack

### From Experiment 2
5. **The issuer/verifier split**: once you have asymmetric keys, the verifier never needs to contact the issuer
6. **What "offline" actually means**: it means the verifier holds a copy of the public key; the issuer's availability is irrelevant after issuance
7. **Expiry as probabilistic revocation**: a 5-minute token limits damage windows without requiring a revocation list
8. **The single point of trust**: the public key distribution problem — how does the verifier know the public key is authentic?

### From Experiment 3
9. **TTL as the primary lever**: with no revocation list, token lifetime is the only control you have over compromise impact
10. **Key rotation as revocation**: rotating the signing key invalidates all previously issued tokens at once — blunt but complete
11. **Token binding eliminates a threat class**: a DPoP-bound token requires both the token *and* the client key to be valid — a stolen token alone is worthless
12. **The hybrid model**: short-lived token + key binding = replay resistance + offline verification + bounded revocation

---

## Connection to Production CDDBS Auth

### Sprint 10 (API key, current)
Simple: one high-entropy key, Argon2id hash in DB. Header-based. This exists to close the "all endpoints public" gap from Sprint 9. It is intentionally throwaway.

### Sprint 11 (Passkeys + session tokens)
WebAuthn is Experiment 1 + Experiment 2 at the protocol level:
- Registration: client proves possession of a newly generated key pair; server stores the public key
- Authentication: server issues a challenge; client signs it; server verifies; server issues a session token

Building Experiments 1 and 2 from scratch means Sprint 11's WebAuthn implementation will be legible rather than magic.

### CDDBS-Edge
Edge needs a credential issued when online that is verifiable when offline. This is Experiment 2's core mechanism. The concrete design:
- When online: authenticate via the standard cloud flow; auth service issues a long-lived (24h–7d) edge credential — a signed token containing user identity, role, and an expiry
- When offline: edge verifier holds the auth service public key; validates the credential locally
- Revocation: key rotation invalidates all edge credentials (nuclear option); short TTL is the gentler alternative

---

## Observation Log

*Record findings here as experiments run. Note where your predictions were wrong — those are the most valuable entries.*

### Experiment 1 Observations
*(fill in as you run)*

| Scenario | Expected | Actual | Insight |
|----------|----------|--------|---------|
| Naive replay | Should fail | | |
| Redirect to wrong service | Should fail | | |
| Missing timestamp | Should fail on expiry | | |
| Full payload binding | Should block all above | | |

### Experiment 2 Observations
*(fill in as you run)*

| Scenario | Expected | Actual | Insight |
|----------|----------|--------|---------|
| Auth service offline, verify existing token | Should succeed | | |
| Auth service offline, issue new token | Should fail | | |
| Tampered token payload | Should fail | | |
| Expired token | Should fail | | |

### Experiment 3 Observations
*(fill in as you run)*

| Scenario | TTL | Damage window | Insight |
|----------|-----|---------------|---------|
| Token stolen, TTL=5min | 5m | | |
| Token stolen, TTL=60min | 60m | | |
| Key rotated, old tokens | — | | |
| DPoP bound token, no key | — | | |
| DPoP bound token, with key | — | | |

---

## Standard Mappings

Once you've run all three experiments, these mappings should feel obvious rather than arbitrary:

| Concept built from scratch | Real-world standard | Why it exists |
|---------------------------|---------------------|---------------|
| Signed challenge with service binding | WebAuthn `clientDataJSON` | Closes redirect and origin attacks |
| Nonce + expiry in signed payload | JWT `jti` + `exp` claims | Closes replay and lifetime attacks |
| Public key verifies without issuer | JWT RS256 / PASETO v4.public | Enables offline verification |
| Token bound to client key | RFC 9449 DPoP | Eliminates stolen-token threat class |
| Key rotation as revocation | JWKS key rotation / certificate CRL | Handles key compromise at scale |
| Short-lived token + refresh | OAuth2 access + refresh token pattern | Balances security and UX |

---

## References

- [WebAuthn Level 3 Spec](https://www.w3.org/TR/webauthn-3/) — especially §6.1 (authenticator data), §13 (security considerations)
- [RFC 9449 — OAuth 2.0 DPoP](https://www.rfc-editor.org/rfc/rfc9449) — the standard your Experiment 3 key binding re-derives
- [PASETO Specification](https://github.com/paseto-standard/paseto-spec) — v4.public uses Ed25519 exactly as you'll implement in Experiment 2
- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) — authenticator assurance levels; useful context for where each experiment sits
- [JWT Best Practices — RFC 8725](https://www.rfc-editor.org/rfc/rfc8725) — many entries are exactly what Experiment 1 discovers by breaking things
