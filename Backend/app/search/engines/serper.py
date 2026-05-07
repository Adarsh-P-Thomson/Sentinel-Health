"""
Serper.dev Google Search API - Free tier available
https://serper.dev - 2,500 free searches/month
"""
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.search.base import BaseSearchEngine
from app.search.crawler import WebCrawler


class SerperSearchEngine(BaseSearchEngine):
    """Serper.dev Google Search API"""
    
    async def search(
        self,
        query: str,
        keywords: List[str],
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search using Serper.dev API
        
        Get free API key from: https://serper.dev
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
            # Get API key from config
            config = self.source_config.get("config", {})
            api_key = config.get("api_key", "").replace("${SERPER_API_KEY}", "")
            
            if not api_key:
                results["errors"].append("Serper API key not configured. Get free key at https://serper.dev")
                return results
            
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": num_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract result URLs
                        search_result_urls = []
                        for result in data.get('organic', []):
                            link = result.get('link')
                            if link:
                                search_result_urls.append(link)
                        
                        print(f"📋 Serper found {len(search_result_urls)} result URLs")
                        
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
                        error_text = await response.text()
                        results["errors"].append(f"Serper API error {response.status}: {error_text}")
            
        except Exception as e:
            results["errors"].append(f"Search error: {str(e)}")
        
        return results
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a web page"""
        return None
    
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract posts from page"""
        return []
