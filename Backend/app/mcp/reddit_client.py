import httpx
from typing import Optional
from app.mcp.base import MCPScout

class RedditScout(MCPScout):
    """
    MCP Scout for Reddit.
    Fetches recent posts containing the medical keyword.
    """
    
    def __init__(self):
        self.base_url = "https://www.reddit.com/search.json"
        
    async def fetch_data(self, keyword: str, limit: int = 5) -> Optional[str]:
        """Fetches Reddit posts containing the keyword."""
        try:
            # We use an async HTTP client to avoid blocking the FastAPI event loop
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={"q": keyword, "limit": limit, "sort": "new"},
                    headers={"User-Agent": "SentinelHealth/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    
                    if not posts:
                        return f"No Reddit discussions found for {keyword}."
                    
                    # Combine the titles and selftexts of the posts into a single raw text payload
                    combined_text = "\n\n".join(
                        f"Title: {post['data'].get('title', '')}\nContent: {post['data'].get('selftext', '')}"
                        for post in posts
                    )
                    return combined_text
                else:
                    return f"Error fetching from Reddit: {response.status_code}"
                    
        except Exception as e:
            return f"Failed to connect to Reddit: {str(e)}"
