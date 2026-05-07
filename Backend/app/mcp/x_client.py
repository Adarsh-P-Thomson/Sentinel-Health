import os
import httpx
from typing import Optional
from app.mcp.base import MCPScout

class XScout(MCPScout):
    """
    MCP Scout for X (Twitter).
    Utilizes twitterapi.io as specified in the hackathon Idea.md.
    """
    
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY", "")
        self.base_url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
        
    async def fetch_data(self, keyword: str, limit: int = 5) -> Optional[str]:
        """Fetches X posts containing the keyword."""
        if not self.api_key:
            print("⚠️ TWITTER_API_KEY not found in environment. Using simulated X data.")
            return f"Simulated X Data for {keyword}: Just took {keyword} and my heart is racing. Is this normal? #sideeffects"
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={"query": keyword, "queryType": "Latest"},
                    headers={"X-API-Key": self.api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get("tweets", [])[:limit]
                    
                    if not tweets:
                        return f"No X posts found for {keyword}."
                    
                    combined_text = "\n\n".join(
                        f"Tweet: {tweet.get('text', '')}" for tweet in tweets
                    )
                    return combined_text
                else:
                    return f"Error fetching from X: {response.status_code}"
                    
        except Exception as e:
            return f"Failed to connect to X API: {str(e)}"
