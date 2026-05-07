"""
Experiment 2 — Assertion Layer: Converting Proof to Self-Verifiable Token
==========================================================================

Goal: After a valid proof (Experiment 1), the auth service issues a signed
      token that any verifier can check independently — without calling the
      auth service.

Structure:
  Part A  — Token format design and issuance
  Part B  — Offline verification (auth service "goes down")
  Part C  — Token tampering attacks
  Part D  — The public key distribution problem

Run:  python experiment_2_assertion_layer.py

Prerequisites: Experiment 1 complete. You should have a working SecureServer
               and SecureClient. This experiment imports from experiment_1 to
               reuse the proof step, then adds the assertion layer on top.

Token format (CDDBS-auth-v1, a minimal signed token):

  <header_b64>.<payload_b64>.<signature_b64>

  header:  {"v": "cddbs.auth.v1", "alg": "Ed25519"}
  payload: {"sub": "<user_id>", "iat": <unix>, "exp": <unix>, "jti": "<nonce>",
            "role": "analyst|admin", "iss": "cddbs.auth"}
  sig:     Ed25519 signature over "<header_b64>.<payload_b64>"

This is structurally identical to JWT (HS256 replaced with Ed25519). You are
building JWT from first principles.
"""

import json
from shared import (
    generate_keypair, sign, verify, new_nonce, now,
    b64url_encode, b64url_decode, json_encode, json_decode,
    NonceStore, section, result, observe,
)


# ===========================================================================
# PART A — Token format and issuance
#
# The AuthService holds a private key (the signing key).
# It issues tokens by signing a header + payload.
# Verifiers hold the corresponding public key.
# The AuthService never needs to be consulted again after issuance.
# ===========================================================================

section("PART A — Token issuance")

# The auth service's signing key pair.
# In production: the private key is stored in a secrets manager, never in code.
# The public key is published so verifiers can find it.
auth_private, auth_public = generate_keypair()

observe("auth service public key (share this with verifiers)",
        auth_public.public_bytes(
            __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding.Raw,
            __import__("cryptography.hazmat.primitives.serialization", fromlist=["PublicFormat"]).PublicFormat.Raw,
        ).hex()[:32] + "...")


class AuthService:
    """
    Issues signed tokens after successful proof verification.

    This is the only component that needs the private key.
    Everything else only needs the public key.
    """

    TOKEN_VERSION = "cddbs.auth.v1"
    ISSUER = "cddbs.auth"

    def __init__(self, private_key, token_ttl_seconds: int = 300):
        self.private_key = private_key
        self.token_ttl = token_ttl_seconds
        self._is_online = True  # simulate going offline in Part B

    def go_offline(self):
        """Simulate the auth service becoming unreachable."""
        self._is_online = False
        print("  [AuthService] ⚡ Auth service is now OFFLINE")

    def issue_token(self, user_id: str, role: str = "analyst") -> str:
        """
        Issue a signed token for an authenticated user.

        Called after a valid proof (Experiment 1 verify_proof returned True).
        The token encodes identity + claims + expiry, signed with our private key.

        IMPLEMENT ME:
        1. Check self._is_online — raise RuntimeError if offline
        2. Build the header dict: {"v": self.TOKEN_VERSION, "alg": "Ed25519"}
        3. Build the payload dict:
              sub  = user_id
              role = role
              iss  = self.ISSUER
              iat  = now()
              exp  = now() + self.token_ttl
              jti  = new_nonce()   ← unique token ID, prevents token replay
        4. Encode header and payload: b64url_encode(json_encode(dict))
        5. Build the signing input: f"{header_b64}.{payload_b64}".encode()
        6. Sign the input: sign(self.private_key, signing_input)
        7. Return: f"{header_b64}.{payload_b64}.{b64url_encode(sig)}"

        Note: you're building JWT RS256 from scratch, using Ed25519 instead of RSA.
        """
        if not self._is_online:
            raise RuntimeError("Auth service is offline — cannot issue new tokens")

        # TODO: implement token issuance
        raise NotImplementedError("Implement AuthService.issue_token()")


class TokenVerifier:
    """
    Verifies tokens using only the auth service's PUBLIC key.
    Does NOT need to contact the auth service.
    Works offline.
    """

    def __init__(self, auth_public_key):
        self.auth_public_key = auth_public_key
        self._jti_store = NonceStore(window_seconds=3600)  # track used jti values

    def verify(self, token: str) -> dict:
        """
        Verify a token and return its claims if valid.
        Raises ValueError with a specific message if verification fails.

        IMPLEMENT ME, in this order:
        1. Split token into [header_b64, payload_b64, sig_b64]
           Raise ValueError("malformed token") if not exactly 3 parts.

        2. Verify the signature:
           - signing_input = f"{header_b64}.{payload_b64}".encode()
           - sig = b64url_decode(sig_b64)
           - Use shared.verify(self.auth_public_key, signing_input, sig)
           - Raise ValueError("invalid signature") if False

        3. Decode the payload: json_decode(b64url_decode(payload_b64))

        4. Check expiry: payload["exp"] < now() → raise ValueError("token expired")

        5. Consume jti to prevent token replay:
           self._jti_store.consume(payload["jti"], payload["iat"])
           Raise ValueError("token already used") if returns False

        6. Return the payload dict (the claims)

        IMPORTANT: verify signature BEFORE decoding payload.
        Why? An attacker could craft a payload that causes your JSON decoder
        to behave unexpectedly. Only trust the contents after the signature
        proves they haven't been modified.
        """
        # TODO: implement verification
        raise NotImplementedError("Implement TokenVerifier.verify()")


# --- Happy path ---
auth_service = AuthService(auth_private, token_ttl_seconds=300)
verifier = TokenVerifier(auth_public)

try:
    token = auth_service.issue_token(user_id="analyst_1", role="analyst")
    observe("token", token[:60] + "...")

    claims = verifier.verify(token)
    result("Token issued and verified successfully", True)
    observe("sub", claims.get("sub"))
    observe("role", claims.get("role"))
    observe("exp", claims.get("exp"))
except NotImplementedError as e:
    print(f"\n  ⚠  {e}\n")


# ===========================================================================
# PART B — Auth service goes offline
#
# The verifier holds a copy of the public key. Once a token is issued,
# the auth service is no longer needed for verification.
#
# Observation: which operations survive? Which fail?
# ===========================================================================

section("PART B — Auth service offline")

try:
    # Issue a token while online
    token_issued_online = auth_service.issue_token(user_id="analyst_1", role="analyst")
    result("Token issued while online", True)

    # Take the auth service offline
    auth_service.go_offline()

    # Can we verify the already-issued token?
    try:
        claims = verifier.verify(token_issued_online)
        result("Verify existing token while auth service offline", True)
        observe("→ insight", "verifier only needs the public key, not the auth service")
    except Exception as e:
        result("Verify existing token while auth service offline", False, str(e))

    # Can we issue a new token?
    try:
        new_token = auth_service.issue_token(user_id="analyst_2", role="analyst")
        result("Issue new token while offline", True, "UNEXPECTED — should have failed")
    except RuntimeError as e:
        result("Issue new token while offline (expected failure)", True)
        observe("→ insight", "issuance requires the auth service; verification does not")

    # Bring it back online
    auth_service._is_online = True

except NotImplementedError as e:
    print(f"\n  ⚠  {e}\n")


# ===========================================================================
# PART C — Token tampering attacks
#
# An attacker intercepts a token and tries to modify the payload.
# The signature should prevent this.
# ===========================================================================

section("PART C — Token tampering attacks")


def attack_role_escalation(token: str, verifier: TokenVerifier) -> bool:
    """
    Attempt to change role from "analyst" to "admin" in the payload.

    Expected: fails — the signature covers the original payload, not the modified one.

    IMPLEMENT ME:
    1. Split the token into [header_b64, payload_b64, sig_b64]
    2. Decode the payload
    3. Change payload["role"] to "admin"
    4. Re-encode the payload
    5. Reconstruct the token with the modified payload but ORIGINAL signature
    6. Present to verifier — it should fail
    """
    # TODO: implement the attack
    raise NotImplementedError("Implement attack_role_escalation()")


def attack_extend_expiry(token: str, verifier: TokenVerifier) -> bool:
    """
    Attempt to extend the token's expiry by modifying the exp field.

    Expected: fails — same reason as role escalation.
    """
    # TODO: implement the attack (same pattern as role escalation)
    raise NotImplementedError("Implement attack_extend_expiry()")


def attack_token_replay(token: str, verifier: TokenVerifier) -> bool:
    """
    Present the same token twice.

    Expected: second use fails because jti is consumed on first use.
    """
    # TODO: verify token twice, return whether second attempt succeeded
    raise NotImplementedError("Implement attack_token_replay()")


try:
    auth_service._is_online = True
    fresh_token = auth_service.issue_token(user_id="analyst_1", role="analyst")

    escalation_succeeded = attack_role_escalation(fresh_token, TokenVerifier(auth_public))
    result("Role escalation attack blocked", not escalation_succeeded)

    fresh_token2 = auth_service.issue_token(user_id="analyst_1", role="analyst")
    expiry_succeeded = attack_extend_expiry(fresh_token2, TokenVerifier(auth_public))
    result("Expiry extension attack blocked", not expiry_succeeded)

    fresh_token3 = auth_service.issue_token(user_id="analyst_1", role="analyst")
    replay_succeeded = attack_token_replay(fresh_token3, TokenVerifier(auth_public))
    result("Token replay attack blocked", not replay_succeeded)

except NotImplementedError as e:
    print(f"\n  ⚠  {e}\n")


# ===========================================================================
# PART D — The public key distribution problem
#
# Everything above works because the verifier has the correct public key.
# But how did the verifier get it? This is the hardest problem in the system.
#
# This part has no code to implement — it's a question to reason through.
# ===========================================================================

section("PART D — The public key distribution problem")

print("""
  The verifier needs the auth service's public key to verify tokens.
  How does it get it?

  Option 1: Hardcoded at deploy time.
    Pros: simple, no network dependency at runtime.
    Cons: key rotation requires redeploying all verifiers.
    Real-world use: CDDBS-Edge (pre-provision the public key at setup time).

  Option 2: JWKS endpoint (e.g., GET /.well-known/jwks.json).
    Pros: automatic rotation — verifiers fetch the current key set.
    Cons: verifier needs to reach the auth service at startup (or cache).
    Real-world use: OIDC providers, Auth0, Google.

  Option 3: Embedded in the token header (self-describing).
    Pros: zero configuration.
    Cons: trivially exploitable — attacker generates their own key pair,
          embeds the public key, signs the token. The verifier blindly trusts it.
          This is a real CVE class (CVE-2018-0114 pattern).

  Questions to answer before Experiment 3:
  1. Which option is appropriate for CDDBS cloud?
  2. Which option is appropriate for CDDBS-Edge?
  3. Why is Option 3 dangerous even though it seems convenient?
  4. What happens when the signing key is compromised?
     → Experiment 3.
""")


# ===========================================================================
# COMBINED FLOW — Proof → Assertion (Experiment 1 + 2)
#
# Full authentication sequence:
# 1. Client proves identity via challenge-response (Experiment 1)
# 2. Auth service issues a token (Experiment 2, Part A)
# 3. Client presents token on subsequent requests (Experiment 2, Part C)
# 4. Verifier checks token independently (no auth service needed)
# ===========================================================================

section("COMBINED FLOW — Proof → Assertion")

print("""
  Authentication sequence:
  ┌─ Client ─────────────────────────────────────────────────────────────┐
  │                                                                       │
  │  1. GET /auth/challenge  →  {nonce, service_id, iat, exp, intent}    │
  │  2. Sign challenge with private key  →  signature                    │
  │  3. POST /auth/prove {challenge, signature}                          │
  │     ← 200 {token}  (signed by auth service)                         │
  │  4. All subsequent requests: Cookie: session=<token>                 │
  │     ← 200 {data}   (verified by verifier, no auth service call)     │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘

  The auth service is only needed for steps 1 and 3.
  All other operations work with the public key alone.
  This is why CDDBS-Edge can work offline with a pre-issued token.
""")

try:
    from experiment_1_raw_proof import SecureServer, SecureClient

    # Setup
    client_private_e2, client_public_e2 = generate_keypair()
    auth_service_e2 = AuthService(auth_private, token_ttl_seconds=300)
    verifier_e2 = TokenVerifier(auth_public)
    proof_server = SecureServer(client_public_e2)
    proof_client = SecureClient(client_private_e2)

    # Step 1-3: Proof
    challenge = proof_server.issue_challenge(intent="authenticate")
    sig = proof_client.respond_to_challenge(challenge)
    proof_valid = proof_server.verify_proof(challenge, sig)
    result("Step 1-3: Proof established", proof_valid)

    # Step 4: Issue token (only if proof valid)
    if proof_valid:
        token = auth_service_e2.issue_token(user_id="analyst_1", role="analyst")
        result("Step 4: Token issued", True)

        # Step 5: Verify on subsequent request (no auth service needed)
        claims = verifier_e2.verify(token)
        result("Step 5: Token verified on request (auth service not called)", True)
        observe("identity asserted", f"sub={claims['sub']}, role={claims['role']}")

except (NotImplementedError, ImportError) as e:
    print(f"\n  ⚠  Complete Experiments 1 and 2 first: {e}\n")
