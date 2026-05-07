from app.mcp.base import MCPScout
from app.mcp.reddit_client import RedditScout
from app.mcp.x_client import XScout

class MCPFactory:
    """
    Factory pattern to return the correct MCP Scout based on the source name.
    """
    @staticmethod
    def get_scout(source: str) -> MCPScout:
        source_lower = source.lower()
        if source_lower == "reddit":
            return RedditScout()
        elif source_lower in ["x", "twitter"]:
            return XScout()
        else:
            raise ValueError(f"Unknown data source: {source}")
