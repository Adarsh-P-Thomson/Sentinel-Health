"""
Twitter/X search engine implementation using twitterapi.io
"""
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.search.base import BaseSearchEngine


class TwitterSearchEngine(BaseSearchEngine):
    """Twitter/X search implementation"""
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        count: int = 100,
        result_type: str = "recent"
    ) -> Dict[str, Any]:
        """
        Search Twitter/X for tweets
        
        Args:
            query: Search query string
            keywords: List of keywords to search for
            count: Maximum results to fetch
            result_type: Type of results (recent, popular, mixed)
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
            config = self.source_config.get("config", {})
            api_key = config.get("api_key", "").replace("${TWITTER_API_KEY}", "")
            
            if not api_key:
                raise ValueError("Twitter API key not configured")
            
            url = "https://api.twitterapi.io/v1/search"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "query": query,
                "count": count,
                "result_type": result_type
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Store the search results page
                        page_data = {
                            "url": str(response.url),
                            "title": f"Twitter Search: {query}",
                            "text_content": query,
                            "http_status": 200
                        }
                        page_id = await self.store_raw_page(page_data)
                        results["pages_found"] = 1
                        results["pages_stored"] = 1
                        results["mongodb_page_ids"].append(page_id)
                        
                        # Extract tweets
                        tweets = await self.extract_tweets_from_response(data, page_id)
                        results["posts_extracted"] = len(tweets)
                        results["mongodb_post_ids"].extend(tweets)
                        
                        # Update page with post count
                        await self.mongodb.raw_pages.update_one(
                            {"_id": page_id},
                            {
                                "$set": {
                                    "processing_status": "completed",
                                    "posts_extracted_count": len(tweets),
                                    "processed_at": datetime.utcnow()
                                }
                            }
                        )
                    else:
                        error = f"Twitter API error: {response.status}"
                        results["errors"].append(error)
            
            await self.respect_rate_limit()
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a Twitter page (not typically used)"""
        return None
    
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tweets from API response"""
        posts = []
        tweets = page_data.get("data", [])
        
        for tweet in tweets:
            posts.append(self._format_tweet(tweet))
        
        return posts
    
    async def extract_tweets_from_response(
        self,
        response_data: Dict[str, Any],
        page_id: str
    ) -> List[str]:
        """Extract and store tweets from API response"""
        post_ids = []
        tweets = response_data.get("data", [])
        
        for tweet in tweets:
            formatted_tweet = {
                "source_post_id": f"twitter_{tweet.get('id_str', tweet.get('id'))}",
                "source_url": f"https://twitter.com/user/status/{tweet.get('id_str', tweet.get('id'))}",
                "content": tweet.get('text', ''),
                "author_username": tweet.get('user', {}).get('screen_name'),
                "author_id": tweet.get('user', {}).get('id_str'),
                "likes": tweet.get('favorite_count', 0),
                "shares": tweet.get('retweet_count', 0),
                "comments": tweet.get('reply_count', 0),
                "views": 0,  # Twitter API v1 doesn't provide view count
                "posted_at": self._parse_twitter_date(tweet.get('created_at')),
                "hashtags": [tag['text'] for tag in tweet.get('entities', {}).get('hashtags', [])],
                "mentions": [mention['screen_name'] for mention in tweet.get('entities', {}).get('user_mentions', [])]
            }
            
            post_id = await self.store_raw_post(formatted_tweet, page_id)
            post_ids.append(post_id)
        
        return post_ids
    
    def _format_tweet(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """Format tweet data"""
        return {
            "source_post_id": f"twitter_{tweet.get('id_str', tweet.get('id'))}",
            "source_url": f"https://twitter.com/user/status/{tweet.get('id_str', tweet.get('id'))}",
            "content": tweet.get('text', ''),
            "author_username": tweet.get('user', {}).get('screen_name'),
            "author_id": tweet.get('user', {}).get('id_str'),
            "likes": tweet.get('favorite_count', 0),
            "shares": tweet.get('retweet_count', 0),
            "comments": tweet.get('reply_count', 0),
            "views": 0,
            "posted_at": self._parse_twitter_date(tweet.get('created_at')),
            "language": tweet.get('lang', 'en'),
            "hashtags": [tag['text'] for tag in tweet.get('entities', {}).get('hashtags', [])],
            "mentions": [mention['screen_name'] for mention in tweet.get('entities', {}).get('user_mentions', [])]
        }
    
    def _parse_twitter_date(self, date_str: str) -> datetime:
        """Parse Twitter date format"""
        if not date_str:
            return datetime.utcnow()
        try:
            return datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
        except:
            return datetime.utcnow()
