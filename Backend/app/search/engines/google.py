"""
Google Custom Search engine implementation
"""
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from app.search.base import BaseSearchEngine


class GoogleSearchEngine(BaseSearchEngine):
    """Google Custom Search implementation"""
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        num_results: int = 10,
        start: int = 1
    ) -> Dict[str, Any]:
        """
        Search Google for web pages
        
        Args:
            query: Search query string
            keywords: List of keywords to search for
            num_results: Number of results per page (max 10)
            start: Starting index for results
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
            api_key = config.get("api_key", "").replace("${GOOGLE_API_KEY}", "")
            cx = config.get("cx", "").replace("${GOOGLE_SEARCH_ENGINE_ID}", "")
            
            if not api_key or not cx:
                raise ValueError("Google API credentials not configured")
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cx,
                "q": query,
                "num": min(num_results, 10),
                "start": start
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process each search result
                        items = data.get('items', [])
                        for item in items:
                            # Fetch and store the actual page
                            page_id = await self.fetch_and_store_page(item)
                            if page_id:
                                results["pages_found"] += 1
                                results["pages_stored"] += 1
                                results["mongodb_page_ids"].append(page_id)
                        
                    else:
                        error = f"Google API error: {response.status}"
                        results["errors"].append(error)
            
            await self.respect_rate_limit()
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    async def fetch_and_store_page(self, search_result: Dict[str, Any]) -> Optional[str]:
        """Fetch a page from Google search result and store it"""
        try:
            url = search_result.get('link')
            if not url:
                return None
            
            # Fetch the actual page
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Parse HTML
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract text content
                        text_content = soup.get_text(separator='\\n', strip=True)
                        
                        # Extract links
                        links = []
                        for link in soup.find_all('a', href=True):
                            links.append({
                                "href": link['href'],
                                "text": link.get_text(strip=True),
                                "type": "internal" if url in link['href'] else "external"
                            })
                        
                        # Extract media
                        media = []
                        for img in soup.find_all('img', src=True):
                            media.append({
                                "type": "image",
                                "url": img['src'],
                                "alt_text": img.get('alt', '')
                            })
                        
                        # Store page
                        page_data = {
                            "url": url,
                            "html_content": html_content,
                            "text_content": text_content,
                            "title": search_result.get('title', soup.title.string if soup.title else ''),
                            "description": search_result.get('snippet', ''),
                            "links": links[:50],  # Limit to 50 links
                            "media": media[:20],  # Limit to 20 media items
                            "http_status": 200
                        }
                        
                        page_id = await self.store_raw_page(page_data)
                        
                        # Mark as completed (no post extraction for web pages)
                        await self.mongodb.raw_pages.update_one(
                            {"_id": page_id},
                            {
                                "$set": {
                                    "processing_status": "completed",
                                    "processed_at": datetime.utcnow()
                                }
                            }
                        )
                        
                        return page_id
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a web page"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        return {
                            "url": str(response.url),
                            "html_content": html_content,
                            "http_status": 200
                        }
        except:
            return None
    
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Google search doesn't extract posts - returns full pages"""
        return []
