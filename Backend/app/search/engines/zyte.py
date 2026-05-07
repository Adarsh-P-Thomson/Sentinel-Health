"""
Zyte API for web scraping with automatic extraction
https://www.zyte.com/zyte-api/
"""
import aiohttp
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.search.base import BaseSearchEngine


class ZyteSearchEngine(BaseSearchEngine):
    """Zyte API for scraping search results"""
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        num_results: int = 10,
        search_engine: str = "google"
    ) -> Dict[str, Any]:
        """
        Use Zyte to scrape search results and extract content
        
        Args:
            query: Search query string
            keywords: List of keywords to search for
            num_results: Number of results to crawl
            search_engine: Which search engine to use (google, bing, duckduckgo)
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
            # Get API key from settings
            from app.core.config import settings
            api_key = settings.zyte_api_key
            
            if not api_key:
                results["errors"].append("Zyte API key not configured. Get key at https://www.zyte.com and add to .env as ZYTE_API_KEY")
                return results
            
            # First, get search results
            search_urls = await self._get_search_results(api_key, query, search_engine, num_results)
            
            if not search_urls:
                results["errors"].append("No search results found")
                return results
            
            print(f"📋 Found {len(search_urls)} URLs to scrape with Zyte")
            
            # Now scrape each URL using Zyte's extraction
            for url in search_urls[:num_results]:
                page_data = await self._scrape_with_zyte(api_key, url)
                if page_data:
                    page_id = await self.store_raw_page(page_data)
                    results["pages_found"] += 1
                    results["pages_stored"] += 1
                    results["mongodb_page_ids"].append(page_id)
                    print(f"✅ Scraped: {page_data.get('title', url)[:50]}...")
            
        except Exception as e:
            results["errors"].append(f"Zyte error: {str(e)}")
        
        return results
    
    async def _get_search_results(
        self,
        api_key: str,
        query: str,
        search_engine: str,
        num_results: int
    ) -> List[str]:
        """Get search result URLs"""
        import urllib.parse
        
        # Build search URL
        if search_engine == "google":
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"
        elif search_engine == "bing":
            search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={num_results}"
        else:  # duckduckgo
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        # Scrape search results page with Zyte
        url = "https://api.zyte.com/v1/extract"
        auth = base64.b64encode(f"{api_key}:".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": search_url,
            "httpResponseBody": True,
            "browserHtml": True
        }
        
        urls = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        html = data.get("browserHtml", "")
                        
                        # Parse HTML to extract links
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            if href.startswith('http') and search_engine not in href:
                                if href not in urls:
                                    urls.append(href)
        except Exception as e:
            print(f"❌ Zyte search error: {e}")
        
        return urls
    
    async def _scrape_with_zyte(self, api_key: str, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a URL using Zyte's automatic extraction"""
        zyte_url = "https://api.zyte.com/v1/extract"
        auth = base64.b64encode(f"{api_key}:".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "article": True,  # Extract article content
            "articleBodyHtml": True,
            "httpResponseBody": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(zyte_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        article = data.get("article", {})
                        
                        return {
                            "url": url,
                            "html_content": article.get("articleBodyHtml", ""),
                            "text_content": article.get("articleBody", ""),
                            "title": article.get("headline", url),
                            "description": article.get("description", ""),
                            "author": article.get("author", {}).get("name") if article.get("author") else None,
                            "published_date": article.get("datePublished"),
                            "links": [],
                            "media": [],
                            "http_status": 200
                        }
                    else:
                        print(f"❌ Zyte scrape failed for {url}: {response.status}")
        except Exception as e:
            print(f"❌ Zyte error for {url}: {e}")
        
        return None
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a page using Zyte"""
        from app.core.config import settings
        api_key = settings.zyte_api_key
        if api_key:
            return await self._scrape_with_zyte(api_key, url)
        return None
    
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract posts from page"""
        return []
