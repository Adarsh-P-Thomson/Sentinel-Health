from abc import ABC, abstractmethod
from typing import Optional

class MCPScout(ABC):
    """
    Base class for all Model Context Protocol (MCP) Scouts.
    These scouts standardise the way raw data is fetched from external APIs,
    translating it into a format the LangGraph Brain can understand.
    """
    
    @abstractmethod
    async def fetch_data(self, keyword: str, limit: int = 10) -> Optional[str]:
        """
        Fetches data related to a specific keyword.
        
        Args:
            keyword (str): The keyword to search for (e.g., 'Drug-Y')
            limit (int): Number of posts to fetch
            
        Returns:
            str: Combined raw text from the fetched posts, or None if failed.
        """
        pass
