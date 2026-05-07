"""
Reddit JSON API - No authentication needed
Uses Reddit's public JSON endpoints
"""
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.search.base import BaseSearchEngine


class RedditJSONSearchEngine(BaseSearchEngine):
    """Reddit search using public JSON API"""
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        limit: int = 100,
        subreddit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search Reddit using public JSON API
        
        Args:
            query: Search query string
            keywords: List of keywords to search for
            limit: Maximum results to fetch
            subreddit: Specific subreddit to search (optional)
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
            # Use Reddit's search JSON API
            if subreddit:
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
            else:
                url = "https://www.reddit.com/search.json"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            params = {
                "q": query,
                "limit": min(limit, 100),
                "sort": "relevance",
                "t": "all",
                "restrict_sr": "on" if subreddit else "off"
            }
            
            print(f"🔍 Reddit JSON API searching: {query}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract posts from JSON
                        children = data.get('data', {}).get('children', [])
                        
                        print(f"📋 Reddit found {len(children)} posts")
                        
                        for item in children:
                            post_data = item.get('data', {})
                            
                            # Extract post content
                            content = post_data.get('selftext', '')
                            if not content:
                                content = post_data.get('title', '')
                            
                            # Fetch comments/replies for this post
                            permalink = post_data.get('permalink', '')
                            comments = []
                            if permalink:
                                comments = await self._fetch_comments(permalink, session, headers)
                            
                            # Store as raw post with comments
                            post = {
                                "source_post_id": f"reddit_{post_data.get('id')}",
                                "source_url": f"https://reddit.com{permalink}",
                                "content": f"{post_data.get('title', '')}\n\n{content}",
                                "author_username": post_data.get('author', 'unknown'),
                                "author_id": post_data.get('author', 'unknown'),
                                "likes": post_data.get('score', 0),
                                "shares": 0,
                                "comments": post_data.get('num_comments', 0),
                                "views": 0,
                                "posted_at": datetime.fromtimestamp(post_data.get('created_utc', 0)),
                                "language": "en",
                                "hashtags": [],
                                "mentions": [],
                                "replies": comments  # Add replies array
                            }
                            
                            post_id = await self.store_raw_post(post, None)
                            results["posts_extracted"] += 1
                            results["mongodb_post_ids"].append(post_id)
                            
                            print(f"  ✅ Post: {post_data.get('title', '')[:50]}... ({len(comments)} replies)")
                        
                        results["pages_found"] = 1
                        results["pages_stored"] = 1
                        
                    elif response.status == 429:
                        results["errors"].append("Reddit rate limit exceeded. Wait before trying again.")
                    else:
                        error_text = await response.text()
                        results["errors"].append(f"Reddit API error {response.status}: {error_text}")
            
        except Exception as e:
            results["errors"].append(f"Search error: {str(e)}")
        
        return results
    
    async def _fetch_comments(
        self,
        permalink: str,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        max_comments: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch comments/replies for a Reddit post"""
        comments = []
        
        try:
            # Convert permalink to JSON endpoint
            json_url = f"https://www.reddit.com{permalink}.json"
            
            async with session.get(json_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Reddit returns [post_data, comments_data]
                    if isinstance(data, list) and len(data) > 1:
                        comments_data = data[1].get('data', {}).get('children', [])
                        
                        for comment_item in comments_data[:max_comments]:
                            comment = comment_item.get('data', {})
                            
                            # Skip "more comments" placeholders
                            if comment.get('kind') == 'more':
                                continue
                            
                            body = comment.get('body', '')
                            if body and body != '[deleted]' and body != '[removed]':
                                comments.append({
                                    "comment_id": comment.get('id'),
                                    "author": comment.get('author', 'unknown'),
                                    "body": body,
                                    "score": comment.get('score', 0),
                                    "created_utc": comment.get('created_utc', 0),
                                    "permalink": f"https://reddit.com{comment.get('permalink', '')}"
                                })
        except Exception as e:
            print(f"  ⚠️  Failed to fetch comments: {e}")
        
        return comments
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a Reddit page as JSON"""
        try:
            # Convert Reddit URL to JSON endpoint
            json_url = url.rstrip('/') + '.json'
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(json_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "url": url,
                            "data": data,
                            "http_status": 200
                        }
        except:
            return None
    
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract posts from Reddit JSON"""
        posts = []
        data = page_data.get("data", {})
        
        if isinstance(data, list):
            # Post with comments
            for item in data:
                children = item.get('data', {}).get('children', [])
                for child in children:
                    post = child.get('data', {})
                    if post:
                        posts.append(self._format_reddit_post(post))
        else:
            # Search results
            children = data.get('children', [])
            for child in children:
                post = child.get('data', {})
                if post:
                    posts.append(self._format_reddit_post(post))
        
        return posts
    
    def _format_reddit_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Format Reddit post data"""
        content = post.get('selftext', '')
        if not content:
            content = post.get('body', '')  # For comments
        
        return {
            "source_post_id": f"reddit_{post.get('id')}",
            "source_url": f"https://reddit.com{post.get('permalink', '')}",
            "content": f"{post.get('title', '')}\n\n{content}" if post.get('title') else content,
            "author_username": post.get('author', 'unknown'),
            "author_id": post.get('author', 'unknown'),
            "likes": post.get('score', 0),
            "shares": 0,
            "comments": post.get('num_comments', 0),
            "views": 0,
            "posted_at": datetime.fromtimestamp(post.get('created_utc', 0)),
            "language": "en",
            "hashtags": [],
            "mentions": []
        }
