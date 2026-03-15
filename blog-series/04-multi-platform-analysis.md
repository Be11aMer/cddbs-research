---
title: "Building CDDBS — Part 4: Multi-Platform Disinformation Detection"
published: false
description: "How we built platform adapters for Twitter and Telegram that normalize heterogeneous social media data into a common analysis format."
tags: ai, python, security, api
series: "Building CDDBS"
---

## Why Multiple Platforms Matter

Disinformation doesn't live on one platform. A narrative might originate on a Telegram channel, get amplified through Twitter retweet networks, and eventually surface in fringe news outlets that look legitimate enough to fool casual readers. If your detection system only watches one platform, you're seeing one act of a three-act play.

CDDBS was initially built around SerpAPI — a news search engine. That covers the news outlet angle: you give it "RT" and it finds recent RT articles to analyze. But analyzing the articles themselves doesn't tell you about the amplification network *around* those articles. For that, you need platform data.

Sprint 3 added platform adapter interfaces for Twitter and Telegram. Sprint 5 wired the Twitter adapter into the live pipeline with real API v2 calls. This post covers both: the adapter architecture and the Twitter integration.

## The Adapter Pattern

The core challenge is data heterogeneity. A Twitter API v2 response looks nothing like a Telegram Bot API response. Both look nothing like a SerpAPI news result. But the analysis pipeline doesn't care about platform-specific fields — it needs a common format to feed into the LLM prompt.

CDDBS solves this with platform adapters that normalize data into a `BriefingInput` dataclass:

```python
# src/cddbs/adapters.py
@dataclass
class PostData:
    id: str
    text: str
    timestamp: str
    engagement: dict       # likes, retweets, replies, etc.
    media_type: str        # text, image, video, poll
    urls: list
    mentions: list
    is_repost: bool        # retweet or forward
    original_source: str   # who it was reposted from
    raw_data: dict         # platform-specific fields preserved

@dataclass
class BriefingInput:
    profile: dict          # name, handle, followers, etc.
    posts: list            # list of PostData
    platform: str          # "twitter", "telegram"
    collection_period: dict
    data_source: str       # "api_v2", "bot_api", etc.
```

Every adapter implements a `normalize()` method that takes raw API data and returns a `BriefingInput`. The pipeline operates exclusively on `BriefingInput` objects — it never touches platform-specific data structures.

## The Twitter Adapter

Twitter API v2 returns rich user and tweet data. The adapter extracts what matters for disinformation analysis:

```python
class TwitterAdapter:
    def normalize(self, raw_data):
        profile = raw_data.get("profile", {})
        posts = raw_data.get("posts", [])

        normalized_profile = {
            "name": profile.get("name"),
            "handle": profile.get("username"),
            "followers": profile.get("public_metrics", {}).get("followers_count", 0),
            "following": profile.get("public_metrics", {}).get("following_count", 0),
            "tweet_count": profile.get("public_metrics", {}).get("tweet_count", 0),
            "verified": profile.get("verified", False),
            "created_at": profile.get("created_at"),
            "bio": profile.get("description", "")
        }

        normalized_posts = []
        for tweet in posts:
            is_repost = bool(tweet.get("referenced_tweets"))
            original_source = ""
            if is_repost:
                ref = tweet["referenced_tweets"][0]
                original_source = ref.get("author_username", ref.get("id", ""))

            normalized_posts.append(PostData(
                id=tweet.get("id", ""),
                text=tweet.get("text", ""),
                timestamp=tweet.get("created_at", ""),
                engagement={
                    "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                    "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                    "replies": tweet.get("public_metrics", {}).get("reply_count", 0),
                    "quotes": tweet.get("public_metrics", {}).get("quote_count", 0),
                    "impressions": tweet.get("public_metrics", {}).get("impression_count", 0)
                },
                media_type=detect_media_type(tweet),
                urls=extract_urls(tweet),
                mentions=extract_mentions(tweet),
                is_repost=is_repost,
                original_source=original_source,
                raw_data=tweet
            ))

        return BriefingInput(
            profile=normalized_profile,
            posts=normalized_posts,
            platform="twitter",
            collection_period=raw_data.get("collection_period", {}),
            data_source="api_v2"
        )
```

Three things the adapter specifically captures for disinformation analysis:

1. **Retweet detection.** The `referenced_tweets` field tells us if a tweet is original content or amplification. A high retweet ratio (e.g., 80%+ of an account's activity is retweets) is a behavioral indicator of coordinated amplification.

2. **Engagement ratios.** Impressions vs. likes vs. retweets creates a profile. Accounts with high impressions but very low engagement may be boosted algorithmically or part of a botnet.

3. **Account metadata.** Creation date, follower/following ratio, bio content, and verification status are all indicators. An unverified account created last month with 50K followers and a bio full of political keywords has a different risk profile than a 10-year-old verified journalist account.

## The Telegram Adapter

Telegram presents fundamentally different challenges:

```python
class TelegramAdapter:
    def normalize(self, raw_data):
        channel = raw_data.get("channel", {})

        normalized_profile = {
            "name": channel.get("title"),
            "handle": channel.get("username"),
            "subscribers": channel.get("participants_count", 0),
            "channel_type": channel.get("type", "channel"),
            "created_at": channel.get("date"),
            "description": channel.get("about", ""),
            "is_verified": channel.get("verified", False),
            "is_scam": channel.get("scam", False)
        }

        normalized_posts = []
        for message in raw_data.get("messages", []):
            is_forward = "fwd_from" in message
            original_source = ""
            if is_forward:
                fwd = message["fwd_from"]
                original_source = (
                    fwd.get("from_name") or
                    fwd.get("channel_post", {}).get("title", "") or
                    str(fwd.get("from_id", ""))
                )

            normalized_posts.append(PostData(
                id=str(message.get("id", "")),
                text=message.get("message", ""),
                timestamp=message.get("date", ""),
                engagement={
                    "views": message.get("views", 0),
                    "forwards": message.get("forwards", 0),
                    "replies": message.get("replies", {}).get("replies", 0)
                },
                media_type=detect_telegram_media(message),
                urls=extract_telegram_urls(message),
                mentions=extract_telegram_mentions(message),
                is_repost=is_forward,
                original_source=original_source,
                raw_data=message
            ))

        return BriefingInput(
            profile=normalized_profile,
            posts=normalized_posts,
            platform="telegram",
            collection_period=raw_data.get("collection_period", {}),
            data_source="bot_api"
        )
```

### Twitter vs. Telegram: Key Differences for Analysis

| Signal | Twitter | Telegram |
|--------|---------|----------|
| Amplification | Retweets (source hidden from casual view) | Forwards (source channel preserved) |
| Reach metric | Impressions + followers | Views + subscriber count |
| Attribution | Account is always visible | Channel admins can be anonymous |
| Bot detection | Follower/following ratio, creation date | View-to-subscriber ratio, posting frequency |
| Content persistence | Tweets can be deleted retroactively | Messages can be edited/deleted silently |
| Network visibility | Follow graph is partially public | Subscriber lists are private |

Telegram is actually *better* for attribution in one specific way: forwarded messages preserve the source channel. On Twitter, a retweet chain can obscure the original source. On Telegram, you can trace a forwarding chain back to the originating channel — which is why our threat model includes a "forwarding chain laundering" narrative (`tg_amp_001`).

## The Twitter API v2 Client

Sprint 5 added a dedicated Twitter client that calls the API v2 endpoints:

```python
# src/cddbs/pipeline/twitter_client.py
def fetch_twitter_data(handle, num_posts=10, bearer_token=None):
    token = _get_bearer_token(bearer_token)
    if not token:
        return None

    # Step 1: Resolve handle to user ID
    user_data = lookup_user(handle, token)
    if not user_data:
        return None

    # Step 2: Fetch recent tweets
    tweets = fetch_user_tweets(user_data["id"], num_posts, token)

    # Step 3: Normalize via adapter
    adapter = TwitterAdapter()
    return adapter.normalize({
        "profile": user_data,
        "posts": tweets,
        "collection_period": {
            "start": datetime.now(UTC).isoformat(),
            "method": "api_v2_recent"
        }
    })
```

### Rate Limiting

Twitter API v2 has aggressive rate limits, especially on the Basic tier (10K tweets/month read). The client implements exponential backoff:

```python
def _make_request(url, headers, params=None, max_retries=3):
    for attempt in range(max_retries + 1):
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:  # Rate limited
            reset_time = int(response.headers.get("x-rate-limit-reset", 0))
            wait = max(reset_time - time.time(), 2 ** attempt)
            time.sleep(min(wait, 60))  # cap at 60 seconds
            continue

        if response.status_code >= 500:  # Server error, retry
            time.sleep(2 ** attempt)
            continue

        return None  # Client error, don't retry

    return None
```

The key detail: the `x-rate-limit-reset` header tells you exactly when the rate limit window resets. We use that when available, falling back to exponential backoff (`2^attempt` seconds) when it's not. The 60-second cap prevents absurdly long waits.

### Bridging to the Pipeline

The pipeline expects a list of article-like dicts (with `title`, `link`, `snippet` fields). The Twitter client bridges this gap:

```python
def briefing_input_to_articles(briefing_input):
    articles = []
    for post in briefing_input.posts:
        articles.append({
            "title": f"Tweet by @{briefing_input.profile.get('handle', 'unknown')}",
            "link": f"https://twitter.com/{briefing_input.profile.get('handle')}/status/{post.id}",
            "snippet": post.text[:200],
            "full_text": post.text,
            "date": post.timestamp,
            "meta": {
                "platform": "twitter",
                "engagement": post.engagement,
                "is_repost": post.is_repost,
                "original_source": post.original_source
            }
        })
    return articles
```

This is an impedance mismatch adapter. The pipeline was originally built for news articles with titles, links, and snippets. Tweets don't have titles. The bridge creates synthetic titles (`"Tweet by @handle"`), constructs URLs from the tweet ID, and truncates the text to a snippet while preserving the full text.

The `meta` field carries platform-specific data (engagement, repost status) through to the LLM prompt, where the system prompt knows how to interpret Twitter-specific indicators.

## Platform Routing in the Pipeline

The orchestrator routes data fetch based on the `platform` parameter:

```python
def _fetch_for_platform(platform, outlet, country, num_articles,
                        url, serpapi_key, twitter_bearer_token,
                        date_filter):
    if platform == "twitter":
        try:
            briefing_input = fetch_twitter_data(
                handle=outlet,
                num_posts=num_articles or 10,
                bearer_token=twitter_bearer_token
            )
            if briefing_input and briefing_input.posts:
                return briefing_input_to_articles(briefing_input)
        except Exception:
            pass  # Fall through to SerpAPI

    return fetch_articles(outlet, country,
                          num_articles=num_articles,
                          url=url, api_key=serpapi_key,
                          time_period=date_filter)
```

The fallback is silent. If the Twitter API returns nothing — bad token, rate limited, account doesn't exist — the pipeline falls back to SerpAPI news search for the same outlet name. This means an analyst who types `@rt_com` with a bad Twitter token still gets an analysis, just from news articles instead of tweets.

## Use Cases This Enables

With multi-platform support, CDDBS can address several analysis patterns:

**Single-outlet deep dive.** Analyze RT's Twitter presence and their news output separately, then compare narrative alignment. Do their tweets push harder on certain narratives than their articles?

**Cross-platform correlation.** If the same narrative appears in a Telegram channel and a Twitter account within a short time window, that's a signal of coordinated messaging — especially if the Telegram channel is the earlier source.

**Amplification network mapping.** By analyzing multiple accounts that share content from the same sources, you can identify amplification networks. A batch analysis of 5 Twitter accounts that all retweet the same state media content is more informative than analyzing each one in isolation.

**Narrative velocity tracking.** How quickly does a narrative move from Telegram (where it might originate) to Twitter (where it gets amplified) to news outlets (where it gains legitimacy)? Multi-platform data makes this measurable.

## What's Not Built Yet

Transparency about limitations:

**Telegram live integration shipped in Sprint 6.** What started as an interface-only adapter is now wired into the live pipeline via `POST /analysis-runs/telegram`. The endpoint accepts a Telegram channel handle and routes it through `TelegramAdapter` in the orchestrator using the Telegram Bot API. The adapter tests (22 tests) cover normalization and forwarding chain attribution; the live endpoint handles channel lookups and message retrieval.

**Cross-platform identity linking is manual.** The research framework defines 8 signals for linking accounts across platforms (shared URLs, similar bios, posting timing, content overlap, etc.), but automated correlation isn't implemented. An analyst has to manually run analyses on suspected linked accounts and compare the results.

**No real-time streaming.** Both Twitter and Telegram offer streaming APIs for real-time data. CDDBS currently operates in batch mode — you request an analysis, it fetches recent data, and gives you a report. The Sprint 6 RSS/GDELT ingestion pipeline runs on a schedule (every 3–5 minutes), which is the closest thing to near-real-time monitoring available today. Full streaming is a future capability.

## The Adapter Test Suite

Platform adapters have 22 tests — the second-highest coverage area after quality scoring:

```python
def test_twitter_retweet_detection():
    """Retweets should be detected from referenced_tweets field."""
    tweet = {"referenced_tweets": [{"type": "retweeted", "id": "123"}]}
    adapter = TwitterAdapter()
    result = adapter.normalize({"profile": {}, "posts": [tweet]})
    assert result.posts[0].is_repost is True

def test_telegram_forward_attribution():
    """Forwarded messages should preserve source channel."""
    message = {
        "fwd_from": {"from_name": "StateMediaChannel"},
        "message": "Breaking news..."
    }
    adapter = TelegramAdapter()
    result = adapter.normalize({"channel": {}, "messages": [message]})
    assert result.posts[0].original_source == "StateMediaChannel"

def test_cross_platform_normalization():
    """Both adapters should produce compatible BriefingInput objects."""
    twitter_input = TwitterAdapter().normalize(TWITTER_FIXTURE)
    telegram_input = TelegramAdapter().normalize(TELEGRAM_FIXTURE)

    # Both should have the same interface
    assert hasattr(twitter_input, "profile")
    assert hasattr(telegram_input, "profile")
    assert isinstance(twitter_input.posts[0], PostData)
    assert isinstance(telegram_input.posts[0], PostData)
```

The cross-platform normalization test is particularly important: it verifies that downstream code (the pipeline, the quality scorer, the narrative matcher) can process data from any platform without knowing which platform it came from.

## Next Up

This post covered the data ingestion layer — how CDDBS gets data from different platforms into a common format for analysis. The final post in this series covers operational maturity: batch analysis, export formats, metrics, and the engineering work that turns a working prototype into a production system.

---

*Platform adapters: [adapters.py](https://github.com/Be11aMer/cddbs-prod/blob/main/src/cddbs/adapters.py). Twitter client: [twitter_client.py](https://github.com/Be11aMer/cddbs-prod/blob/main/src/cddbs/pipeline/twitter_client.py).*
