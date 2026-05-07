"""
Reddit search engine implementation
"""
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from app.search.base import BaseSearchEngine


class RedditSearchEngine(BaseSearchEngine):
    """Reddit search implementation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None
        
    async def authenticate(self):
        """Get OAuth2 access token"""
        config = self.source_config.get("config", {})
        client_id = config.get("client_id", "").replace("${REDDIT_CLIENT_ID}", "")
        client_secret = config.get("client_secret", "").replace("${REDDIT_CLIENT_SECRET}", "")
        user_agent = config.get("user_agent", "").replace("${REDDIT_USER_AGENT}", "SentinelHealth/1.0")
        
        if not client_id or not client_secret:
            raise ValueError("Reddit credentials not configured")
        
        auth = aiohttp.BasicAuth(client_id, client_secret)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": user_agent}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get("access_token")
                else:
                    raise Exception(f"Reddit auth failed: {response.status}")
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        subreddit: Optional[str] = None,
        sort: str = "relevance",
        time_filter: str = "week",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search Reddit for posts
        
        Args:
            query: Search query string
            keywords: List of keywords to search for
            subreddit: Specific subreddit to search (optional)
            sort: Sort method (relevance, new, hot, top)
            time_filter: Time filter (all, year, month, week, day, hour)
            limit: Maximum results to fetch
        """
        if not self.access_token:
            await self.authenticate()
        
        results = {
            "pages_found": 0,
            "pages_stored": 0,
            "posts_extracted": 0,
            "mongodb_page_ids": [],
            "mongodb_post_ids": [],
            "errors": []
        }
        
        try:
            # Build search URL
            if subreddit:
                url = f"https://oauth.reddit.com/r/{subreddit}/search"
            else:
                url = "https://oauth.reddit.com/search"
            
            params = {
                "q": query,
                "sort": sort,
                "t": time_filter,
                "limit": limit,
                "raw_json": 1
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": "SentinelHealth/1.0"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Store the search results page
                        page_data = {
                            "url": str(response.url),
                            "title": f"Reddit Search: {query}",
                            "text_content": query,
                            "http_status": 200
                        }
                        page_id = await self.store_raw_page(page_data)
                        results["pages_found"] = 1
                        results["pages_stored"] = 1
                        results["mongodb_page_ids"].append(page_id)
                        
                        # Extract posts
                        posts = await self.extract_posts_from_response(data, page_id)
                        results["posts_extracted"] = len(posts)
                        results["mongodb_post_ids"].extend(posts)
                        
                        # Update page with post count
                        await self.mongodb.raw_pages.update_one(
                            {"_id": page_id},
                            {
                                "$set": {
                                    "processing_status": "completed",
                                    "posts_extracted_count": len(posts),
                                    "processed_at": datetime.utcnow()
                                }
                            }
                        )
                    else:
                        error = f"Reddit API error: {response.status}"
                        results["errors"].append(error)
            
            await self.respect_rate_limit()
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a Reddit page"""
        if not self.access_token:
            await self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "SentinelHealth/1.0"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "url": str(response.url),
                        "data": data,
                        "http_status": 200
                    }
        return None
    
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract posts from Reddit API response"""
        posts = []
        data = page_data.get("data", {})
        
        if "data" in data and "children" in data["data"]:
            for child in data["data"]["children"]:
                post = child.get("data", {})
                posts.append(self._format_reddit_post(post))
        
        return posts
    
    async def extract_posts_from_response(
        self,
        response_data: Dict[str, Any],
        page_id: str
    ) -> List[str]:
        """Extract and store posts from Reddit API response"""
        post_ids = []
        
        if "data" in response_data and "children" in response_data["data"]:
            for child in response_data["data"]["children"]:
                post_data = child.get("data", {})
                
                formatted_post = {
                    "source_post_id": f"reddit_{post_data.get('id')}",
                    "source_url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "content": f"{post_data.get('title', '')}\\n\\n{post_data.get('selftext', '')}",
                    "author_username": post_data.get('author'),
                    "author_id": post_data.get('author'),
                    "likes": post_data.get('score', 0),
                    "comments": post_data.get('num_comments', 0),
                    "posted_at": datetime.fromtimestamp(post_data.get('created_utc', 0)),
                    "hashtags": [],
                    "mentions": []
                }
                
                post_id = await self.store_raw_post(formatted_post, page_id)
                post_ids.append(post_id)
        
        return post_ids
    
    def _format_reddit_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Format Reddit post data"""
        return {
            "source_post_id": f"reddit_{post.get('id')}",
            "source_url": f"https://reddit.com{post.get('permalink', '')}",
            "content": f"{post.get('title', '')}\\n\\n{post.get('selftext', '')}",
            "author_username": post.get('author'),
            "author_id": post.get('author'),
            "likes": post.get('score', 0),
            "comments": post.get('num_comments', 0),
            "views": 0,  # Reddit doesn't provide view count
            "posted_at": datetime.fromtimestamp(post.get('created_utc', 0)),
            "language": "en",
            "hashtags": [],
            "mentions": []
        }
