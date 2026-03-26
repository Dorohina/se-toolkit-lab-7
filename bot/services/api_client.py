"""LMS API client service."""

import httpx
from typing import Any


class LMSClient:
    """Client for interacting with the LMS backend API.
    
    Attributes:
        base_url: Base URL of the LMS API.
        api_key: API key for authentication.
    """
    
    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.
        
        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002).
            api_key: API key for Bearer authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}
    
    def get_items(self) -> list[dict[str, Any]]:
        """Fetch all items (labs and tasks) from the backend.
        
        Returns:
            List of items with lab and task information.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        url = f"{self.base_url}/items/"
        with httpx.Client() as client:
            response = client.get(url, headers=self._headers)
            response.raise_for_status()
            return response.json()
    
    def get_pass_rates(self, lab: str) -> dict[str, Any]:
        """Fetch pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., 'lab-01').
            
        Returns:
            Dictionary with pass rate data per task.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        url = f"{self.base_url}/analytics/pass-rates"
        params = {"lab": lab}
        with httpx.Client() as client:
            response = client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()
    
    def check_health(self) -> dict[str, Any]:
        """Check if the backend is healthy.
        
        Returns:
            Dictionary with health status and item count.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        items = self.get_items()
        return {"healthy": True, "item_count": len(items)}
