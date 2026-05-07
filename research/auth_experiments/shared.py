"""
Shared cryptographic primitives for auth experiments.

All three experiments use Ed25519 asymmetric keys:
- Private key: held by the client (proves identity) or auth service (signs tokens)
- Public key: held by the verifier (checks proofs and tokens)

The `cryptography` library wraps OpenSSL. We use it at a low level here
so you see exactly what is being signed and verified.
"""

import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
)
from cryptography.exceptions import InvalidSignature


# ---------------------------------------------------------------------------
# Key utilities
# ---------------------------------------------------------------------------

def generate_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a fresh Ed25519 key pair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def public_key_bytes(public_key: Ed25519PublicKey) -> bytes:
    """Serialize a public key to raw 32-byte format."""
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)


def public_key_hex(public_key: Ed25519PublicKey) -> str:
    return public_key_bytes(public_key).hex()


# ---------------------------------------------------------------------------
# Signing and verification (raw — no token format yet)
# ---------------------------------------------------------------------------

def sign(private_key: Ed25519PrivateKey, data: bytes) -> bytes:
    """Sign raw bytes. Returns 64-byte Ed25519 signature."""
    return private_key.sign(data)


def verify(public_key: Ed25519PublicKey, data: bytes, signature: bytes) -> bool:
    """Verify a signature. Returns True if valid, False if not."""
    try:
        public_key.verify(signature, data)
        return True
    except InvalidSignature:
        return False


# ---------------------------------------------------------------------------
# Encoding helpers (used in Experiment 2 token format)
# ---------------------------------------------------------------------------

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def json_encode(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()


def json_decode(data: bytes) -> dict:
    return json.loads(data)


# ---------------------------------------------------------------------------
# Nonce generation
# ---------------------------------------------------------------------------

def new_nonce() -> str:
    """Generate a cryptographically random nonce (hex string)."""
    return os.urandom(16).hex()


def now() -> int:
    """Current Unix timestamp (integer seconds)."""
    return int(time.time())


# ---------------------------------------------------------------------------
# Simple in-memory nonce store (replay prevention)
# ---------------------------------------------------------------------------

class NonceStore:
    """
    Tracks seen nonces within a time window.
    A nonce can only be used once — presenting the same nonce twice is a replay.

    In production this would be Redis or a DB table. Here it's just a set.
    Note: this store loses memory on process restart — acceptable for experiments.
    """

    def __init__(self, window_seconds: int = 300):
        self._seen: dict[str, int] = {}  # nonce -> timestamp when first seen
        self._window = window_seconds

    def consume(self, nonce: str, timestamp: int) -> bool:
        """
        Returns True if the nonce is fresh and unseen.
        Returns False if it's been seen before or is outside the time window.
        Marks it as consumed if accepted.
        """
        self._evict_expired(timestamp)

        if nonce in self._seen:
            return False  # replay detected

        if abs(timestamp - now()) > self._window:
            return False  # too old or too far in the future

        self._seen[nonce] = timestamp
        return True

    def _evict_expired(self, current_time: int):
        expired = [n for n, t in self._seen.items() if current_time - t > self._window]
        for n in expired:
            del self._seen[n]


# ---------------------------------------------------------------------------
# Print helpers for experiment output
# ---------------------------------------------------------------------------

def section(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def result(label: str, passed: bool, detail: str = ""):
    icon = "✓" if passed else "✗"
    line = f"  {icon}  {label}"
    if detail:
        line += f"  →  {detail}"
    print(line)


def observe(label: str, value: Any):
    print(f"  obs  {label}: {value}")
