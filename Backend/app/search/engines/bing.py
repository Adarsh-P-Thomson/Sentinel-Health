"""
Bing search engine - no API key needed
Crawls actual result pages
"""
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

from app.search.base import BaseSearchEngine
from app.search.crawler import WebCrawler


class BingSearchEngine(BaseSearchEngine):
    """Bing search without API requirements"""
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        num_results: int = 20
    ) -> Dict[str, Any]:
        """
        Scrape Bing search results (no API key needed)
        
        Args:
            query: Search query string
            keywords: List of keywords to search for
            num_results: Number of results to fetch
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
            # Bing search URL
            search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={num_results}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract search result URLs - get all links
                        search_result_urls = []
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            if href.startswith('http') and 'bing.com' not in href:
                                if href not in search_result_urls:
                                    search_result_urls.append(href)
                        
                        print(f"📋 Bing found {len(search_result_urls)} result URLs")
                        if search_result_urls:
                            print(f"   Sample URLs: {search_result_urls[:3]}")
                        
                        # Crawl result pages
                        if search_result_urls:
                            crawler = WebCrawler(
                                mongodb=self.mongodb,
                                project_id=self.project_id,
                                search_execution_id=self.search_execution_id,
                                source_id=self.source_id,
                                max_pages=min(num_results, len(search_result_urls))
                            )
                            
                            crawler.add_urls(search_result_urls)
                            crawl_results = await crawler.crawl()
                            
                            results["pages_found"] = crawl_results["pages_crawled"]
                            results["pages_stored"] = crawl_results["pages_stored"]
                            results["mongodb_page_ids"] = crawl_results["mongodb_page_ids"]
                            results["errors"].extend(crawl_results["errors"])
                        else:
                            results["errors"].append("No search result URLs found")
                    else:
                        error = f"Bing search failed: HTTP {response.status}"
                        results["errors"].append(error)
            
            await self.respect_rate_limit()
            
        except Exception as e:
            results["errors"].append(f"Search error: {str(e)}")
        
        return results
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a web page"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
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
        """Extract posts from page"""
        return []
