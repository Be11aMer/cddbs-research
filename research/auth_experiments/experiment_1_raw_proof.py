"""
Experiment 1 — Raw Proof: Challenge-Response from Scratch
==========================================================

Goal: Implement the minimum viable challenge-response. Understand what a
      signature proves and what it doesn't.

Structure:
  Part A  — Naive implementation (intentionally incomplete)
  Part B  — Attack simulations that break Part A
  Part C  — Fixed implementation with proper payload binding
  Part D  — Verify all attacks are now closed

Run:  python experiment_1_raw_proof.py

The Parts run sequentially. Part B attacks will SUCCEED (break Part A) —
that is the expected and intended result. Part D verifies Part C closes them.

Record observations in research/auth_model_research.md as you run.
"""

from shared import (
    generate_keypair, sign, verify, new_nonce, now,
    json_encode, NonceStore, section, result, observe,
)


# ===========================================================================
# PART A — Naive challenge-response
#
# The server issues a challenge (just a nonce).
# The client signs it.
# The server verifies the signature.
#
# What does this prove? What doesn't it prove?
# ===========================================================================

section("PART A — Naive challenge-response")

# Setup: client has a key pair; server knows the client's public key.
client_private, client_public = generate_keypair()
observe("client public key", client_public.public_bytes(
    __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding.Raw,
    __import__("cryptography.hazmat.primitives.serialization", fromlist=["PublicFormat"]).PublicFormat.Raw,
).hex()[:16] + "...")


class NaiveServer:
    """A server that issues and verifies challenges naively."""

    def __init__(self, known_public_key):
        self.known_public_key = known_public_key
        self._pending_challenges: set[str] = set()

    def issue_challenge(self) -> bytes:
        """Issue a challenge: just a random nonce."""
        nonce = new_nonce()
        self._pending_challenges.add(nonce)
        # The challenge is just the raw nonce bytes.
        return nonce.encode()

    def verify_proof(self, challenge: bytes, signature: bytes) -> bool:
        """
        Verify that the signature covers the challenge and was produced
        by the known public key.

        IMPLEMENT ME:
        - Check the challenge was one we issued (is it in _pending_challenges?)
        - Verify the signature using shared.verify()
        - Remove the challenge from pending (prevent reuse... or does this help?)
        - Return True only if everything checks out

        Note what this does NOT check — you'll discover it in Part B.
        """
        # TODO: implement verification
        raise NotImplementedError("Implement NaiveServer.verify_proof()")


class NaiveClient:
    """A client that responds to challenges."""

    def __init__(self, private_key):
        self.private_key = private_key

    def respond_to_challenge(self, challenge: bytes) -> bytes:
        """
        Respond to a challenge by signing it.

        IMPLEMENT ME:
        - Sign the raw challenge bytes using shared.sign()
        - Return the signature
        """
        # TODO: implement signing
        raise NotImplementedError("Implement NaiveClient.respond_to_challenge()")


# --- Run the happy path ---
server_a = NaiveServer(client_public)
client = NaiveClient(client_private)

try:
    challenge = server_a.issue_challenge()
    signature = client.respond_to_challenge(challenge)
    ok = server_a.verify_proof(challenge, signature)
    result("Happy path: valid client authenticates", ok)
except NotImplementedError as e:
    print(f"\n  ⚠  {e}")
    print("  Implement the above before running attacks.\n")


# ===========================================================================
# PART B — Attack simulations
#
# These attacks SHOULD SUCCEED against the naive implementation.
# If they fail, either your implementation already has the fix (check Part C)
# or the attack is broken — debug before continuing.
# ===========================================================================

section("PART B — Attacks against naive implementation")

print("""
  These attacks are expected to SUCCEED here.
  If they fail on your naive implementation, investigate why before continuing.
""")


def attack_replay(server: NaiveServer, client: NaiveClient) -> bool:
    """
    Replay attack: capture a valid (challenge, signature) pair and present it again.

    Expected: succeeds on naive implementation (server doesn't track used signatures)
    Expected after fix: fails (nonce consumed on first use)
    """
    challenge = server.issue_challenge()
    signature = client.respond_to_challenge(challenge)

    # First presentation — should succeed
    first = server.verify_proof(challenge, signature)

    # Second presentation of the SAME (challenge, signature) — should this fail?
    # On the naive implementation, what happens?
    second = server.verify_proof(challenge, signature)

    observe("replay — first use", first)
    observe("replay — second use (attack)", second)
    attack_succeeded = second  # attack succeeds if the second use is accepted
    return attack_succeeded


def attack_redirect(
    server_a: NaiveServer,
    server_b: NaiveServer,
    client: NaiveClient,
) -> bool:
    """
    Redirect attack: a proof produced for server A is presented to server B.

    This is possible when the signed data contains no information about
    which service is the intended recipient.

    Expected: succeeds if both servers use the same public key and the
              signed payload contains no service binding.
    Expected after fix: fails (service_id in signed payload doesn't match server B)
    """
    # Client authenticates to server A legitimately
    challenge_a = server_a.issue_challenge()
    signature = client.respond_to_challenge(challenge_a)

    # Attacker presents the same (challenge, signature) to server B
    # Server B also knows the client's public key (it's the same user)
    # Does server B accept it?
    try:
        accepted_by_b = server_b.verify_proof(challenge_a, signature)
    except Exception:
        accepted_by_b = False

    observe("redirect — accepted by server B (attack)", accepted_by_b)
    return accepted_by_b


def attack_future_replay(server: NaiveServer, client: NaiveClient) -> bool:
    """
    Timestamp attack: a valid proof has no expiry — it could be saved and
    replayed later, even after the session has ended.

    Expected: succeeds on naive implementation (no timestamp in signed data)
    Expected after fix: fails (timestamp checked, proof expired)

    Note: this is harder to simulate without mocking time. For now, just
    observe whether the signed payload contains a timestamp at all.
    """
    challenge = server.issue_challenge()
    signature = client.respond_to_challenge(challenge)
    observe("signed payload contains timestamp", b"iat" in challenge or b"timestamp" in challenge)
    return False  # fill in after implementing the fix


# Run attacks
server_b = NaiveServer(client_public)  # a different service, same client key

try:
    replay_succeeded = attack_replay(server_a, client)
    result("Replay attack succeeded (expected)", replay_succeeded, "fix: consume nonce on first use")

    redirect_succeeded = attack_redirect(server_a, server_b, client)
    result("Redirect attack succeeded (expected)", redirect_succeeded, "fix: bind service_id into payload")

    attack_future_replay(server_a, client)
    result("Timestamp missing from payload (expected)", True, "fix: include iat + exp in signed data")
except NotImplementedError:
    print("  Complete Part A before running attacks.")


# ===========================================================================
# PART C — Fixed implementation with proper payload binding
#
# The signed payload must contain enough context to make the proof
# unambiguous: it is for this service, at this time, for this purpose,
# and can only be used once.
#
# Minimum viable payload:
#   {
#     "nonce":      "<random, single-use>",    -- closes replay
#     "service_id": "<who is asking>",         -- closes redirect
#     "iat":        <unix timestamp>,           -- closes future replay
#     "exp":        <unix timestamp + N>,       -- closes future replay
#     "intent":     "<what this proof is for>", -- closes scope confusion
#   }
#
# Compare this to WebAuthn's clientDataJSON when you're done.
# ===========================================================================

section("PART C — Fixed implementation")


class SecureServer:
    """
    A server that issues structured challenges and verifies bound proofs.

    The key difference from NaiveServer: the signed payload is a JSON structure,
    not a bare nonce. Every field in the payload closes a specific attack.
    """

    SERVICE_ID = "cddbs.auth.v1"  # unique identifier for this service

    def __init__(self, known_public_key):
        self.known_public_key = known_public_key
        self._nonce_store = NonceStore(window_seconds=60)

    def issue_challenge(self, intent: str = "authenticate") -> dict:
        """
        Issue a structured challenge.

        Returns a dict the client must include verbatim in the signed payload.
        The client cannot modify these fields — any modification breaks the signature.

        IMPLEMENT ME:
        - Generate a fresh nonce
        - Set iat (issued at, now()) and exp (now() + 60 seconds)
        - Include service_id and intent
        - Return the challenge dict
        """
        # TODO: return a dict with nonce, service_id, iat, exp, intent
        raise NotImplementedError("Implement SecureServer.issue_challenge()")

    def verify_proof(self, challenge: dict, signature: bytes) -> bool:
        """
        Verify a proof against the structured challenge.

        IMPLEMENT ME, checking in order:
        1. Reconstruct the signed bytes: json_encode(challenge)
        2. Verify the signature over those bytes
        3. Check challenge["service_id"] == self.SERVICE_ID
        4. Check challenge["exp"] > now()  (not expired)
        5. Consume the nonce via self._nonce_store.consume() — rejects replays
        6. Return True only if all checks pass

        Each check closes exactly one attack from Part B. Note which.
        """
        # TODO: implement all checks
        raise NotImplementedError("Implement SecureServer.verify_proof()")


class SecureClient:
    """A client that signs structured challenge payloads."""

    def __init__(self, private_key):
        self.private_key = private_key

    def respond_to_challenge(self, challenge: dict) -> bytes:
        """
        Sign the challenge.

        IMPLEMENT ME:
        - Encode the challenge to bytes: json_encode(challenge)
        - Sign the bytes: sign(self.private_key, payload_bytes)
        - Return the signature

        Important: the client signs the challenge exactly as received.
        It cannot modify any field — doing so would break the signature.
        Why does this matter for security? Think about what would happen
        if the client could swap out the service_id.
        """
        # TODO: implement signing
        raise NotImplementedError("Implement SecureClient.respond_to_challenge()")


# --- Run the happy path ---
secure_server_a = SecureServer(client_public)
secure_server_b = SecureServer(client_public)
secure_client = SecureClient(client_private)

try:
    challenge = secure_server_a.issue_challenge()
    signature = secure_client.respond_to_challenge(challenge)
    ok = secure_server_a.verify_proof(challenge, signature)
    result("Happy path: valid client authenticates", ok)
except NotImplementedError as e:
    print(f"\n  ⚠  {e}")


# ===========================================================================
# PART D — Verify attacks are closed
#
# Run the same attacks from Part B against the secure implementation.
# They should now all FAIL.
# ===========================================================================

section("PART D — Attacks against fixed implementation")

print("""
  These attacks should now FAIL.
  If any still succeed, your fix is incomplete — go back to Part C.
""")


def attack_replay_secure(server: SecureServer, client: SecureClient) -> bool:
    """Replay the same (challenge, signature) pair twice."""
    challenge = server.issue_challenge()
    sig = client.respond_to_challenge(challenge)

    first = server.verify_proof(challenge, sig)
    try:
        second = server.verify_proof(challenge, sig)
    except Exception:
        second = False

    observe("replay — first use", first)
    observe("replay — second use (attack)", second)
    return second  # attack succeeded if second=True


def attack_redirect_secure(
    server_a: SecureServer,
    server_b: SecureServer,
    client: SecureClient,
) -> bool:
    """Present server A's challenge to server B."""
    challenge_a = server_a.issue_challenge()
    sig = client.respond_to_challenge(challenge_a)

    try:
        accepted = server_b.verify_proof(challenge_a, sig)
    except Exception:
        accepted = False

    observe("redirect — accepted by server B (attack)", accepted)
    return accepted


try:
    replay_succeeded = attack_replay_secure(secure_server_a, secure_client)
    result("Replay attack blocked", not replay_succeeded)

    redirect_succeeded = attack_redirect_secure(secure_server_a, secure_server_b, secure_client)
    result("Redirect attack blocked", not redirect_succeeded)
except NotImplementedError as e:
    print(f"\n  ⚠  {e}")


# ===========================================================================
# REFLECTION
#
# Before moving to Experiment 2, answer these questions:
#
# 1. What is the minimum set of fields that must appear in the signed payload?
#    Why is each one necessary?
#
# 2. The client signs the challenge "exactly as received". What would happen
#    if the client could modify the service_id before signing?
#
# 3. Look up WebAuthn's clientDataJSON:
#    https://www.w3.org/TR/webauthn-3/#dictdef-collectedclientdata
#    How does it compare to the payload you derived?
#
# 4. The proof is valid for 60 seconds. After verification, the server has
#    established that the client holds the private key. But it has not yet
#    issued anything the client can use for subsequent requests. What needs
#    to happen next? → That is Experiment 2.
# ===========================================================================

section("REFLECTION — Questions before Experiment 2")
print("""
  1. What is the minimum payload that closes replay, redirect, and expiry?
  2. What would happen if the client could modify service_id before signing?
  3. Compare your payload to WebAuthn clientDataJSON — what matches?
  4. After a valid proof: what does the client use for the next request?
     → Answer: Experiment 2.
""")
