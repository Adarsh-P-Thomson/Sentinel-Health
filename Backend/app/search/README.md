# Search Engine Module

Multi-source search implementation for Sentinel Health.

See full documentation in `/DOCS/SEARCH_ENGINE.md`

## Quick Start

```python
# Execute search
POST /api/v1/search
{
  "project_id": "uuid",
  "source_ids": ["reddit", "twitter"],
  "query": "Drug-Y side effects",
  "keywords": ["Drug-Y", "headache"]
}
```

## Available Sources

- Reddit (OAuth2)
- Twitter/X (twitterapi.io)
- Google Custom Search
- More coming soon...

## Configuration

Add API keys to `.env`:
```env
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
TWITTER_API_KEY=...
GOOGLE_API_KEY=...
```
