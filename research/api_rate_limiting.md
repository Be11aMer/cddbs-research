# API Rate Limiting Design

**Sprint**: 3 — Multi-Platform Support
**Status**: Research complete
**Purpose**: Design rate limiting and error handling strategy for multi-platform data collection

---

## Platform API Overview

### Twitter/X API v2

| Tier | Rate Limits | Monthly Cost | Data Access |
|------|------------|--------------|-------------|
| Free | 1,500 tweets/month read, 50 requests/15min | $0 | Tweet lookup, user lookup (limited) |
| Basic | 10,000 tweets/month read, 100 requests/15min | $100 | Tweet lookup, user lookup, search (7 days) |
| Pro | 1,000,000 tweets/month read, 300 requests/15min | $5,000 | Full-archive search, filtered stream |
| Academic Research | 10,000,000 tweets/month | Application-based | Full-archive search, conversation threads |

**Key endpoints for CDDBS**:
- `GET /2/users/:id/tweets` — User timeline (per-user rate: 1,500 tweets/request, 900 requests/15min at Pro)
- `GET /2/tweets/search/recent` — Recent search (450 requests/15min at Pro)
- `GET /2/users/:id/followers` — Follower list (15 requests/15min)
- `GET /2/users/:id/following` — Following list (15 requests/15min)

**Rate limit headers**:
- `x-rate-limit-limit` — Max requests in window
- `x-rate-limit-remaining` — Requests remaining
- `x-rate-limit-reset` — Unix timestamp when window resets

### Telegram Bot API

| Constraint | Limit |
|-----------|-------|
| Messages per second (to same chat) | 1 |
| Messages per second (overall) | 30 |
| Bulk messages per second | 30 |
| getUpdates long polling | No hard rate limit |
| File download | 20 MB max |

**Key methods for CDDBS**:
- `getChat` — Channel/group metadata (no documented rate limit, but throttled at ~30/sec)
- `getChatMemberCount` — Subscriber count
- `getChatHistory` (MTProto only) — Message history retrieval
- `forwardMessage` — N/A for analysis, but forwarding metadata visible in messages

**Important**: The Bot API has limited access to channel history. For comprehensive analysis, MTProto (Telethon/Pyrogram) is needed:
- `client.get_messages(channel, limit=N)` — Retrieve message history
- `client.get_participants(channel)` — Member list (admin permissions required)
- `client.iter_messages(channel, search=query)` — Search within channel

**MTProto rate limits**:
- FloodWait errors: Variable, typically 5-60 seconds, can be hours for aggressive scraping
- Concurrent requests: ~20-30 before throttling
- Account-based: Limits are per-account, not per-IP

---

## Rate Limiting Strategy

### 1. Token Bucket Algorithm

Use token bucket for each API endpoint:

```python
@dataclass
class TokenBucket:
    capacity: int          # Max tokens (requests)
    refill_rate: float     # Tokens per second
    tokens: float          # Current tokens
    last_refill: float     # Timestamp of last refill

    def consume(self, tokens: int = 1) -> float:
        """Try to consume tokens. Returns wait time (0 if available)."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return 0.0
        wait = (tokens - self.tokens) / self.refill_rate
        return wait
```

### 2. Per-Platform Configuration

```python
RATE_LIMITS = {
    "twitter": {
        "user_timeline": TokenBucket(capacity=900, refill_rate=1.0, window=900),   # 900/15min
        "search_recent": TokenBucket(capacity=450, refill_rate=0.5, window=900),   # 450/15min
        "followers":     TokenBucket(capacity=15,  refill_rate=0.017, window=900), # 15/15min
    },
    "telegram": {
        "get_messages":  TokenBucket(capacity=30, refill_rate=30.0, window=1),     # 30/sec
        "get_chat":      TokenBucket(capacity=30, refill_rate=30.0, window=1),     # 30/sec
    }
}
```

### 3. Exponential Backoff with Jitter

For transient errors (429, 500, network):

```python
def retry_with_backoff(func, max_retries=4):
    for attempt in range(max_retries + 1):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries:
                raise
            # Use server-provided wait time if available
            wait = e.retry_after or (2 ** attempt)
            jitter = random.uniform(0, wait * 0.1)
            time.sleep(wait + jitter)
        except TransientError:
            if attempt == max_retries:
                raise
            wait = 2 ** attempt
            jitter = random.uniform(0, wait * 0.1)
            time.sleep(wait + jitter)
```

### 4. Request Queue Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Analysis     │────▶│ Request      │────▶│ Platform        │
│ Pipeline     │     │ Queue        │     │ Rate Limiter    │
└─────────────┘     └──────────────┘     └────────┬────────┘
                         ▲                         │
                         │    ┌─────────────────┐  │
                         └────│ Retry Queue     │◀─┘
                              │ (failed/429s)   │
                              └─────────────────┘
```

**Queue priorities**:
1. **Critical**: Metadata lookups (fast, low-cost)
2. **Standard**: Timeline/history retrieval
3. **Bulk**: Follower/network enumeration (slow, high-cost)

---

## Error Handling Matrix

| Error | Platform | Action | Max Retries |
|-------|----------|--------|-------------|
| 429 Too Many Requests | Twitter | Wait `retry-after` header seconds | 4 |
| FloodWait | Telegram | Wait `seconds` from error | 3 |
| 401 Unauthorized | Both | Refresh token / re-authenticate | 1 |
| 403 Forbidden | Both | Skip resource, log warning | 0 |
| 500/502/503 | Both | Exponential backoff | 4 |
| Network timeout | Both | Exponential backoff (2, 4, 8, 16s) | 4 |
| 404 Not Found | Both | Skip (account deleted/suspended) | 0 |

---

## Cost Analysis

### Scenario: Analyze 50 accounts/month

| Platform | Tier | Monthly Tweets/Messages | Estimated Cost |
|----------|------|------------------------|----------------|
| Twitter | Basic | ~60,000 (50 accounts × 1,200 posts avg) | $100/month |
| Twitter | Pro | ~60,000 | $5,000/month |
| Telegram | MTProto | ~100,000 (50 channels × 2,000 msgs avg) | $0 (API is free) |

**Recommendation**: Twitter Basic tier ($100/month) is sufficient for CDDBS research phase. Telegram MTProto is free but requires a user account (phone number).

### Cost Optimization Strategies

1. **Cache aggressively**: Store retrieved posts/messages locally; never re-fetch
2. **Incremental collection**: Only fetch new posts since last analysis
3. **Prioritize targets**: Use metadata-only requests first to triage; full timeline for flagged accounts only
4. **Batch where possible**: Twitter v2 supports batch user/tweet lookups (up to 100 IDs)
5. **Off-peak collection**: Run bulk collection during low-traffic hours to reduce FloodWait risk on Telegram

---

## Implementation Phases

### Phase 1 (Sprint 3 — Research)
- Document rate limits and design patterns (this document)
- No production code yet

### Phase 2 (Sprint 4+  — Production)
- Implement token bucket rate limiter in cddbs-prod
- Add request queue with priority levels
- Implement retry logic with exponential backoff
- Add monitoring/alerting for rate limit approaching

### Phase 3 (Sprint 5+ — Scale)
- Multi-account rotation for Telegram (distribute load)
- Proxy rotation for IP-based limits
- Request deduplication across analysis pipelines
- Cost dashboard and budget alerts

---

## Key References

- Twitter API v2 Rate Limits: https://developer.twitter.com/en/docs/twitter-api/rate-limits
- Telegram Bot API: https://core.telegram.org/bots/api
- Telegram MTProto: https://core.telegram.org/api
- Telethon documentation: https://docs.telethon.dev/
