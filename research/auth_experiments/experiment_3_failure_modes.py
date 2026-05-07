"""
Experiment 3 — Failure Modes: Revocation, Key Compromise, and Token Binding
============================================================================

Goal: Understand what happens when things go wrong — and what mechanisms
      exist to limit damage.

Structure:
  Part A  — Token theft: TTL as the primary damage control lever
  Part B  — Key compromise: rotation as the only reliable revocation
  Part C  — DPoP binding: making a stolen token useless without the client key
  Part D  — Hybrid model: key-bound short-lived tokens

Run:  python experiment_3_failure_modes.py

Prerequisites: Experiments 1 and 2 complete and implemented.

This experiment introduces the concept of proof-of-possession (PoP):
a token that is cryptographically bound to the client's key pair.
Even if an attacker steals the token, they cannot use it without also
possessing the private key. This is the core idea behind RFC 9449 (DPoP).
"""

import time
from unittest.mock import patch

from shared import (
    generate_keypair, sign, verify, new_nonce, now,
    b64url_encode, b64url_decode, json_encode, json_decode,
    section, result, observe,
)
from experiment_2_assertion_layer import AuthService, TokenVerifier


# ===========================================================================
# PART A — Token theft and TTL
#
# A bearer token is like a key: whoever holds it can use it.
# The TTL is the only built-in damage control mechanism in a stateless system.
#
# Observe: how does TTL change the attacker's options?
# ===========================================================================

section("PART A — Token theft: TTL as damage control")

auth_private, auth_public = generate_keypair()


def simulate_token_theft(ttl_seconds: int, theft_delay_seconds: int) -> dict:
    """
    Simulate: a token is issued, stolen after theft_delay_seconds,
    and the attacker attempts to use it.

    Returns a dict with observations.
    """
    auth = AuthService(auth_private, token_ttl_seconds=ttl_seconds)
    verifier = TokenVerifier(auth_public)

    # Issue token
    token = auth.issue_token(user_id="analyst_1", role="analyst")
    issue_time = now()

    # Simulate time passing (mock time)
    stolen_at = issue_time + theft_delay_seconds

    observations = {
        "ttl": ttl_seconds,
        "theft_delay": theft_delay_seconds,
        "token_valid_at_theft": stolen_at < (issue_time + ttl_seconds),
        "damage_window_remaining": max(0, (issue_time + ttl_seconds) - stolen_at),
    }

    # Attempt to use stolen token at theft time
    with patch("shared.now", return_value=stolen_at):
        try:
            verifier_at_theft = TokenVerifier(auth_public)
            claims = verifier_at_theft.verify(token)
            observations["attacker_succeeded"] = True
            observations["attacker_identity"] = claims["sub"]
        except Exception as e:
            observations["attacker_succeeded"] = False
            observations["failure_reason"] = str(e)

    return observations


print("\n  Scenario: token stolen at different points in its lifetime\n")

# Run several scenarios and observe
scenarios = [
    (300, 10),    # 5min TTL, stolen after 10s — long damage window
    (300, 290),   # 5min TTL, stolen near expiry — short window
    (3600, 10),   # 1hr TTL, stolen after 10s — very long damage window
    (60, 10),     # 1min TTL, stolen after 10s — moderate window
    (60, 61),     # 1min TTL, stolen after expiry — no window
]

for ttl, delay in scenarios:
    obs = simulate_token_theft(ttl, delay)
    damage = obs["damage_window_remaining"]
    succeeded = obs["attacker_succeeded"]
    observe(
        f"TTL={ttl:4}s, stolen at t+{delay:3}s",
        f"attack {'SUCCEEDED' if succeeded else 'FAILED   '} | damage window: {damage:4}s"
    )

print("""
  ┌──────────────────────────────────────────────────────────────────┐
  │  Key insight:                                                     │
  │  With no revocation mechanism, TTL is your only control.         │
  │  Short TTL = small damage window, but requires refresh tokens.   │
  │  Long TTL = convenient, but a stolen token grants long access.   │
  │                                                                   │
  │  CDDBS-Edge tradeoff:                                            │
  │  Edge tokens may need to be valid for 24h–7d (offline use).      │
  │  This means a stolen edge token has a long damage window.        │
  │  → Key binding (Part C) becomes critical for edge credentials.   │
  └──────────────────────────────────────────────────────────────────┘
""")


# ===========================================================================
# PART B — Key compromise and rotation
#
# If the auth service's signing key is compromised, an attacker can issue
# arbitrary tokens. The only remediation is key rotation.
#
# Observe: what happens to previously issued tokens when the key rotates?
# ===========================================================================

section("PART B — Key compromise and rotation")


class RotatingAuthService(AuthService):
    """
    An auth service that supports key rotation.

    When compromised, we generate a new key pair. All tokens signed by
    the old key become invalid immediately. This is the "nuclear option" —
    blunt but complete.

    An alternative is versioned keys (keep old keys active for one TTL window,
    then retire them). This is how JWKS key rotation works in practice.
    """

    def __init__(self):
        private_key, self.current_public = generate_keypair()
        super().__init__(private_key, token_ttl_seconds=3600)
        self._key_version = 1

    def rotate_key(self):
        """Generate a new signing key pair. All old tokens become unverifiable."""
        new_private, self.current_public = generate_keypair()
        self.private_key = new_private
        self._key_version += 1
        print(f"  [RotatingAuthService] Key rotated → version {self._key_version}")
        print("  [RotatingAuthService] All tokens signed by previous key are now INVALID")


# Setup
rotating_auth = RotatingAuthService()

# Issue token before compromise
token_before_rotation = rotating_auth.issue_token(user_id="analyst_1", role="analyst")
result("Token issued before key rotation", True)

# Verify it works
verifier_v1 = TokenVerifier(rotating_auth.current_public)
try:
    claims = verifier_v1.verify(token_before_rotation)
    result("Token valid before rotation", True)
except Exception as e:
    result("Token valid before rotation", False, str(e))

# Simulate key compromise + rotation
print()
rotating_auth.rotate_key()
print()

# Old verifier (has old public key) — token still verifies here
try:
    claims = verifier_v1.verify(token_before_rotation)
    result("Old verifier still accepts pre-rotation token (expected)", True)
    observe("→ insight", "verifiers must update their public key on rotation")
except Exception as e:
    result("Old verifier still accepts pre-rotation token", False, str(e))

# New verifier (has new public key) — token is now invalid
verifier_v2 = TokenVerifier(rotating_auth.current_public)
try:
    claims = verifier_v2.verify(token_before_rotation)
    result("New verifier rejects pre-rotation token", False, "UNEXPECTED — should have been rejected")
except Exception as e:
    result("New verifier rejects pre-rotation token (expected)", True)
    observe("→ insight", "key rotation is immediate revocation for all old tokens")

# New token — valid with new key
token_after_rotation = rotating_auth.issue_token(user_id="analyst_1", role="analyst")
try:
    claims = verifier_v2.verify(token_after_rotation)
    result("New token (post-rotation) valid", True)
except Exception as e:
    result("New token (post-rotation) valid", False, str(e))

print("""
  ┌──────────────────────────────────────────────────────────────────┐
  │  Key rotation as revocation:                                      │
  │  + Complete: all old tokens invalidated immediately               │
  │  + No revocation list needed                                      │
  │  - Blunt: legitimate active sessions also invalidated             │
  │  - Verifiers must update their public key (distribution problem)  │
  │                                                                   │
  │  Graceful rotation alternative (JWKS pattern):                   │
  │  Keep old key active for one TTL window, then retire.             │
  │  Active sessions survive; new tokens use the new key.             │
  └──────────────────────────────────────────────────────────────────┘
""")


# ===========================================================================
# PART C — DPoP binding: token + key = credential
#
# DPoP (Demonstrating Proof of Possession) binds a token to a client's
# key pair. The token contains the client's public key (in the "cnf" claim).
# On each request, the client also presents a short-lived DPoP proof:
# a signature over {method, URL, timestamp, token_hash}.
#
# An attacker with the token but not the private key cannot produce a
# valid DPoP proof → the stolen token is useless.
#
# This re-derives RFC 9449.
# ===========================================================================

section("PART C — DPoP binding: making stolen tokens useless")

# New auth service for this experiment
dpop_auth_private, dpop_auth_public = generate_keypair()
dpop_auth = AuthService(dpop_auth_private, token_ttl_seconds=300)


def issue_dpop_token(
    auth_service: AuthService,
    user_id: str,
    client_public_key,
    role: str = "analyst",
) -> str:
    """
    Issue a token that is bound to the client's public key.

    IMPLEMENT ME:
    The token payload must include a "cnf" (confirmation) claim containing
    the client's public key. This is the binding — the verifier will check
    that request DPoP proofs are signed by the key in "cnf".

    Structure:
      payload["cnf"] = {"jwk": client_public_key_hex}

    Where client_public_key_hex is the hex encoding of the raw public key bytes.

    Hint: use shared.public_key_hex() if you add it to shared.py,
    or encode it inline.

    Everything else is the same as AuthService.issue_token().
    """
    # TODO: issue a token with cnf claim
    raise NotImplementedError("Implement issue_dpop_token()")


def create_dpop_proof(
    client_private_key,
    method: str,
    url: str,
    token: str,
) -> str:
    """
    Create a DPoP proof: a short-lived signed statement that the client
    is actively presenting this specific token for this specific request.

    The proof binds:
      - htm: HTTP method ("GET", "POST", etc.)
      - htu: HTTP URL (e.g., "https://cddbs.onrender.com/api/analysis-runs")
      - iat: timestamp (expires after 60 seconds)
      - jti: unique nonce (prevents proof replay)
      - ath: SHA-256 hash of the token (binds proof to this specific token)

    IMPLEMENT ME:
    1. Build payload: {htm, htu, iat: now(), exp: now()+60, jti: new_nonce(), ath: hash(token)}
       For ath: import hashlib; ath = hashlib.sha256(token.encode()).hexdigest()
    2. Build header: {"v": "cddbs.dpop.v1", "alg": "Ed25519"}
    3. Same signing format as Experiment 2 tokens
    4. Return the signed proof string
    """
    # TODO: implement DPoP proof creation
    raise NotImplementedError("Implement create_dpop_proof()")


def verify_dpop_request(
    token: str,
    dpop_proof: str,
    method: str,
    url: str,
    auth_public_key,
) -> dict:
    """
    Verify both the token AND the DPoP proof.

    IMPLEMENT ME:
    1. Verify the token (Experiment 2 TokenVerifier logic)
       - Check signature with auth_public_key
       - Check expiry
    2. Extract the cnf.jwk claim from the token payload
    3. Verify the DPoP proof signature using the cnf public key
       (not the auth service key — the CLIENT's key)
    4. Check the DPoP proof payload:
       - htm matches the request method
       - htu matches the request URL
       - iat is recent (within 60 seconds)
       - ath matches SHA-256(token)
    5. Return the token claims if all checks pass

    Why verify in this order?
    The token signature must be checked with the auth key first.
    Only after that do we know the cnf claim is trustworthy — because
    it was signed by the auth service, not the client.
    """
    # TODO: implement dual verification
    raise NotImplementedError("Implement verify_dpop_request()")


# Setup
client_private_dpop, client_public_dpop = generate_keypair()
attacker_private, attacker_public = generate_keypair()

try:
    # Client gets a bound token
    bound_token = issue_dpop_token(dpop_auth, "analyst_1", client_public_dpop)
    result("DPoP-bound token issued", True)

    # Normal request: client presents token + DPoP proof
    dpop_proof = create_dpop_proof(
        client_private_dpop,
        method="GET",
        url="https://cddbs.onrender.com/api/analysis-runs",
        token=bound_token,
    )
    claims = verify_dpop_request(
        bound_token, dpop_proof,
        method="GET",
        url="https://cddbs.onrender.com/api/analysis-runs",
        auth_public_key=dpop_auth_public,
    )
    result("Legitimate request (token + valid DPoP proof)", True)

    # Attack: stolen token, attacker presents it without their key matching
    attacker_proof = create_dpop_proof(
        attacker_private,  # attacker's key — doesn't match cnf in token
        method="GET",
        url="https://cddbs.onrender.com/api/analysis-runs",
        token=bound_token,
    )
    try:
        claims = verify_dpop_request(
            bound_token, attacker_proof,
            method="GET",
            url="https://cddbs.onrender.com/api/analysis-runs",
            auth_public_key=dpop_auth_public,
        )
        result("Stolen token with wrong key blocked", False, "UNEXPECTED — attack should have failed")
    except Exception as e:
        result("Stolen token with wrong key blocked (expected)", True)
        observe("→ insight", "token is useless without the client's private key")

    # Attack: attacker reuses legitimate DPoP proof on different URL
    try:
        claims = verify_dpop_request(
            bound_token, dpop_proof,  # same proof as legitimate request
            method="GET",
            url="https://cddbs.onrender.com/api/admin/users",  # different URL
            auth_public_key=dpop_auth_public,
        )
        result("Proof replay on different URL blocked", False, "UNEXPECTED")
    except Exception as e:
        result("Proof replay on different URL blocked (expected)", True)
        observe("→ insight", "the URL is bound into the proof — it can't be redirected")

except NotImplementedError as e:
    print(f"\n  ⚠  {e}\n")


# ===========================================================================
# PART D — Hybrid model summary
#
# Combining short-lived tokens + key binding gives:
# - Replay resistance (jti + short TTL)
# - Redirect resistance (URL in DPoP proof)
# - Stolen token resistance (cnf binding)
# - Offline verification (public key only)
# - Bounded revocation (TTL limits damage window)
#
# This is the full DPoP model (RFC 9449). You derived it by necessity.
# ===========================================================================

section("PART D — Hybrid model: what you've derived")

print("""
  The model you built in Parts A-C:

  ┌─────────────────────────────────────────────────────────────────────┐
  │  Client auth flow (full DPoP model):                                │
  │                                                                     │
  │  1. Prove identity (Experiment 1 challenge-response)                │
  │  2. Auth service issues bound token:                                │
  │        token = sign({sub, role, exp, jti, cnf: {client_pubkey}})   │
  │  3. Each request:                                                   │
  │        DPoP-Proof: sign({htm, htu, iat, jti, ath: hash(token)})    │
  │        Authorization: DPoP <token>                                  │
  │  4. Verifier checks:                                                │
  │        token signature (auth service key)                          │
  │        DPoP proof signature (client key from cnf)                  │
  │        URL, method, timestamp, token hash all match                │
  │                                                                     │
  │  Security properties achieved:                                      │
  │    ✓  No shared secrets in DB (client key is asymmetric)           │
  │    ✓  Stolen token is useless without client private key           │
  │    ✓  No replay (jti consumed, DPoP proof is single-use)           │
  │    ✓  No redirect (URL bound into DPoP proof)                      │
  │    ✓  Offline verification (only public keys needed)               │
  │    ✓  Bounded revocation (TTL limits damage window)                │
  │    ✓  Key rotation as emergency revocation                         │
  │                                                                     │
  │  This is RFC 9449 (DPoP). You derived it from first principles.    │
  └─────────────────────────────────────────────────────────────────────┘

  For CDDBS production auth (Sprint 11):
    - WebAuthn handles step 1 (proof) with hardware/device security
    - Session tokens (opaque) or short-lived DPoP-bound JWTs for step 2
    - DPoP is optional at Sprint 11 scope — standard session tokens
      are sufficient for 1-50 analysts; DPoP becomes valuable at scale

  For CDDBS-Edge:
    - Pre-issued edge credential = step 2 token, issued while online
    - Edge device holds client key pair; verifier holds auth public key
    - DPoP binding prevents credential theft on the edge device
    - TTL governs how long the edge credential remains valid offline
""")


# ===========================================================================
# FINAL REFLECTION
#
# 1. Every constraint in DPoP (URL binding, token hash, short-lived proof)
#    maps directly to an attack you simulated. Which attack does each field close?
#
# 2. In Part B, key rotation is the only complete revocation mechanism.
#    Why can't you "invalidate" a specific token without a revocation list?
#    What property of offline verification makes this impossible?
#
# 3. For CDDBS-Edge specifically: if the edge device is stolen, the attacker
#    has both the token AND the private key. What's the mitigation?
#    (Hint: device-level protection — TEE, Secure Enclave, or PIN-derived key)
#
# 4. Compare the auth system you built to WebAuthn Level 3.
#    Specifically: how does WebAuthn's registration flow map to your
#    key setup? How does authentication map to your combined proof + token flow?
# ===========================================================================

section("FINAL REFLECTION")
print("""
  1. Map each DPoP field to the attack it closes from Experiments 1-2.
  2. Why can't a specific token be invalidated without a revocation list?
  3. If an edge device is physically stolen (token + key), what's the mitigation?
  4. Map the full system to WebAuthn Level 3 registration + authentication.
""")
