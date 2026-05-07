"""
Web crawler with FIFO queue for processing search result links
"""
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from bs4 import BeautifulSoup
from collections import deque
from motor.motor_asyncio import AsyncIOMotorDatabase


class WebCrawler:
    """FIFO queue-based web crawler"""
    
    def __init__(
        self,
        mongodb: AsyncIOMotorDatabase,
        project_id: Optional[str],
        search_execution_id: str,
        source_id: str,
        max_pages: int = 10,
        timeout: int = 10
    ):
        self.mongodb = mongodb
        self.project_id = project_id
        self.search_execution_id = search_execution_id
        self.source_id = source_id
        self.max_pages = max_pages
        self.timeout = timeout
        
        # FIFO queue for URLs to crawl
        self.url_queue = deque()
        
        # Track visited URLs to avoid duplicates
        self.visited_urls: Set[str] = set()
        
        # Results
        self.pages_crawled = 0
        self.pages_stored = 0
        self.mongodb_page_ids = []
        self.errors = []
    
    def add_urls(self, urls: List[str]):
        """Add URLs to the crawl queue"""
        for url in urls:
            if url not in self.visited_urls and url not in self.url_queue:
                self.url_queue.append(url)
    
    async def crawl(self) -> Dict[str, Any]:
        """
        Crawl all URLs in the queue (FIFO)
        
        Returns:
            {
                "pages_crawled": int,
                "pages_stored": int,
                "mongodb_page_ids": List[str],
                "errors": List[str]
            }
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            while self.url_queue and self.pages_crawled < self.max_pages:
                # FIFO: pop from left (first in, first out)
                url = self.url_queue.popleft()
                
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                
                try:
                    await self._crawl_page(session, url)
                    self.pages_crawled += 1
                    
                    # Small delay to be respectful
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    error_msg = f"Failed to crawl {url}: {str(e)}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
        
        return {
            "pages_crawled": self.pages_crawled,
            "pages_stored": self.pages_stored,
            "mongodb_page_ids": self.mongodb_page_ids,
            "errors": self.errors
        }
    
    async def _crawl_page(self, session: aiohttp.ClientSession, url: str):
        """Crawl a single page and store it"""
        print(f"🔍 Crawling: {url}")
        
        try:
            # Special handling for Reddit
            headers = {}
            if 'reddit.com' in url:
                # Use old.reddit.com for easier scraping (but don't double-convert)
                if not url.startswith('https://old.reddit.com'):
                    url = url.replace('www.reddit.com', 'old.reddit.com').replace('https://reddit.com', 'https://old.reddit.com')
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1"
                }
            
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                if response.status != 200:
                    self.errors.append(f"{url}: HTTP {response.status}")
                    return
                
                # Get content
                html_content = await response.text()
                
                # Check for Reddit verification page
                if 'reddit.com' in url and ('verification' in html_content.lower() or 'please wait' in html_content.lower()):
                    print(f"⚠️  Reddit verification page detected, skipping: {url}")
                    self.errors.append(f"{url}: Reddit verification required")
                    return
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove unwanted elements (header, footer, nav, ads, scripts, styles)
                for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                    element.decompose()
                
                # Remove common ad/tracking classes
                ad_classes = ['ad', 'advertisement', 'banner', 'popup', 'modal', 'cookie', 'gdpr', 'sidebar', 'related-posts']
                for ad_class in ad_classes:
                    for element in soup.find_all(class_=lambda x: x and ad_class in x.lower()):
                        element.decompose()
                
                # Try to find main content area
                main_content = None
                content_selectors = [
                    'article',
                    'main',
                    '[role="main"]',
                    '.content',
                    '.main-content',
                    '.post-content',
                    '.entry-content',
                    '#content',
                    '#main',
                    '.thing',  # Reddit specific
                    '.usertext-body'  # Reddit comments
                ]
                
                for selector in content_selectors:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break
                
                # If no main content found, use body
                if not main_content:
                    main_content = soup.body if soup.body else soup
                
                # Extract clean text content
                text_content = main_content.get_text(separator='\n', strip=True)
                
                # Remove excessive whitespace
                text_content = '\n'.join(line.strip() for line in text_content.split('\n') if line.strip())
                
                # Check if we got meaningful content
                if len(text_content) < 100:
                    print(f"⚠️  Too little content extracted from {url}, skipping")
                    self.errors.append(f"{url}: Insufficient content")
                    return
                
                # Extract title
                title = soup.title.string if soup.title else url
                
                # Extract meta description
                description = ""
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if not meta_desc:
                    meta_desc = soup.find('meta', attrs={'property': 'og:description'})
                if meta_desc:
                    description = meta_desc.get('content', '')
                
                # Extract links (only from main content)
                links = []
                for link in main_content.find_all('a', href=True, limit=50):
                    href = link['href']
                    if href.startswith('http'):
                        links.append({
                            "href": href,
                            "text": link.get_text(strip=True)[:100],
                            "type": "external"
                        })
                
                # Extract images (only from main content)
                media = []
                for img in main_content.find_all('img', src=True, limit=20):
                    media.append({
                        "type": "image",
                        "url": img['src'],
                        "alt_text": img.get('alt', '')
                    })
                
                # Store page in MongoDB
                page_id = await self._store_page({
                    "url": url,
                    "html_content": str(main_content),  # Store only main content HTML
                    "text_content": text_content,
                    "title": title,
                    "description": description,
                    "links": links,
                    "media": media,
                    "http_status": 200
                })
                
                if page_id:
                    self.pages_stored += 1
                    self.mongodb_page_ids.append(page_id)
                    print(f"✅ Stored: {title[:50]}... ({len(text_content)} chars)")
                
        except asyncio.TimeoutError:
            self.errors.append(f"{url}: Timeout")
        except Exception as e:
            self.errors.append(f"{url}: {str(e)}")
    
    async def _store_page(self, page_data: Dict[str, Any]) -> Optional[str]:
        """Store page in MongoDB"""
        import hashlib
        from datetime import timedelta
        from bson import ObjectId
        
        # Generate URL hash for deduplication
        url_hash = hashlib.sha256(page_data["url"].encode()).hexdigest()
        
        # Check if page already exists
        existing = await self.mongodb.raw_pages.find_one({"url_hash": url_hash})
        if existing:
            return str(existing["_id"])
        
        # Prepare document
        document = {
            "search_execution_id": self.search_execution_id,
            "source_id": self.source_id,
            "url": page_data["url"],
            "url_hash": url_hash,
            "canonical_url": page_data["url"],
            "html_content": page_data.get("html_content", ""),
            "text_content": page_data.get("text_content", ""),
            "title": page_data.get("title", ""),
            "description": page_data.get("description", ""),
            "links": page_data.get("links", []),
            "media": page_data.get("media", []),
            "http_status": page_data.get("http_status", 200),
            "headers": {},
            "processing_status": "completed",
            "posts_extracted_count": 0,
            "fetched_at": datetime.utcnow(),
            "processed_at": datetime.utcnow(),
            "retention_policy": "low_value",
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "created_at": datetime.utcnow()
        }
        
        # Add optional project_id
        if self.project_id:
            document["project_id"] = self.project_id
        
        result = await self.mongodb.raw_pages.insert_one(document)
        return str(result.inserted_id)
