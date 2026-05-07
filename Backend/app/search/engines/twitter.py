"""
Twitter/X search engine implementation using Twitter API v2
"""
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.search.base import BaseSearchEngine
from app.search.crawler import WebCrawler


class TwitterSearchEngine(BaseSearchEngine):
    """Twitter/X search implementation using API v2"""
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search Twitter/X for tweets using API v2
        
        Args:
            query: Search query string
            keywords: List of keywords to search for
            max_results: Maximum results to fetch (10-100)
        """
        results = {
            "pages_found": 0,
            "pages_stored": 0,
            "posts_extracted": 0,
            "mongodb_page_ids": [],
            "mongodb_post_ids": [],
            "errors": []
        }
        
        try:
            # Get Bearer Token from settings
            from app.core.config import settings
            bearer_token = settings.twitter_bearer_token
            
            if not bearer_token:
                results["errors"].append("Twitter Bearer Token not configured. Add to .env as TWITTER_BEARER_TOKEN")
                return results
            
            # Twitter API v2 recent search endpoint
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {
                "Authorization": f"Bearer {bearer_token}"
            }
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,public_metrics,author_id,lang",
                "expansions": "author_id",
                "user.fields": "username"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract tweets and store them
                        tweets = data.get("data", [])
                        users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}
                        
                        print(f"📋 Twitter found {len(tweets)} tweets")
                        
                        for tweet in tweets:
                            author_id = tweet.get("author_id")
                            author = users.get(author_id, {})
                            metrics = tweet.get("public_metrics", {})
                            
                            post_data = {
                                "source_post_id": f"twitter_{tweet['id']}",
                                "source_url": f"https://twitter.com/user/status/{tweet['id']}",
                                "content": tweet.get("text", ""),
                                "author_username": author.get("username", "unknown"),
                                "author_id": author_id,
                                "likes": metrics.get("like_count", 0),
                                "shares": metrics.get("retweet_count", 0),
                                "comments": metrics.get("reply_count", 0),
                                "views": metrics.get("impression_count", 0),
                                "posted_at": datetime.fromisoformat(tweet.get("created_at", "").replace("Z", "+00:00")) if tweet.get("created_at") else datetime.utcnow(),
                                "language": tweet.get("lang", "en"),
                                "hashtags": [],
                                "mentions": []
                            }
                            
                            post_id = await self.store_raw_post(post_data, None)
                            results["posts_extracted"] += 1
                            results["mongodb_post_ids"].append(post_id)
                        
                        results["pages_found"] = 1
                        results["pages_stored"] = 1
                        
                    elif response.status == 429:
                        results["errors"].append("Twitter API rate limit exceeded. Wait before trying again.")
                    else:
                        error_text = await response.text()
                        results["errors"].append(f"Twitter API error {response.status}: {error_text}")
            
            await self.respect_rate_limit()
            
        except Exception as e:
            results["errors"].append(f"Search error: {str(e)}")
        
        return results
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a Twitter page (not typically used)"""
        return None
    
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tweets from API response"""
        return []
