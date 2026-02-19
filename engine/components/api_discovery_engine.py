import requests
from typing import List, Dict, Any
import logging
from urllib.parse import urlparse

class APIDiscoveryEngine:
    """
    A class to discover and parse APIs from various sources.
    
    Attributes:
        api_endpoints (List[str]): URLs of API documentation endpoints.
        session (requests.Session): Session for making HTTP requests.
    """
    
    def __init__(self):
        self.api_endpoints = [
            "https://api.swaggerhub.com/v1/apis",
            "https://rapidapihub.com/api/endpoints"
        ]
        self.session = requests.Session()
        
    def discover_apis(self) -> List[Dict[str, Any]]:
        """
        Discovers APIs from configured endpoints and parses them.
        
        Returns:
            List of API information dictionaries. Each dictionary contains
            'name', 'endpoint', 'documentation_url', and 'specs'.
            
        Raises:
            requests.exceptions.RequestException: If discovery fails.
        """
        discoveredApis = []
        
        for endpoint in self.api_endpoints:
            try:
                response = self.session.get(endpoint)
                response.raise_for_status()
                
                data = response.json()
                if "apis" in data:
                    for api_data in data["apis"]:
                        api_info = {
                            "name": api_data.get("name", ""),
                            "endpoint": api_data.get("endpoint", ""),
                            "documentation_url": api_data.get("docUrl", ""),
                            "specs": self._parse_api_specs(api_data)
                        }
                        discoveredApis.append(api_info)
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to discover APIs from {endpoint}: {str(e)}")
                
        return discoveredApis
    
    def _parse_api_specs(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses API specifications from the given data.
        
        Args:
            api_data: Dictionary containing API information.
            
        Returns:
            Parsed API specifications.
        """
        specs = {}
        
        # Example: Extracting Swagger/OpenAPI specs
        if "openapi" in api_data.get("tags", []):
            specs["type"] = "openapi"
            specs["url"] = api_data.get("specUrl", "")
        elif "swagger" in api_data.get("tags", []):
            specs["type"] = "swagger"
            specs["url"] = api_data.get("specUrl", "")
        
        # Extracting other relevant info
        specs["authentication"] = api_data.get("authType", "none")
        specs["rate_limits"] = api_data.get("limits", {})
        
        return specs
    
    def get_api_endpoint(self, domain: str) -> str:
        """
        Determines the API endpoint URL from the domain.
        
        Args:
            domain: Domain name of the service.
            
        Returns:
            Base URL of the API endpoint.
        """
        try:
            response = self.session.get(f"https://{domain}/api")
            response.raise_for_status()
            
            # Example: Parse response headers for location
            location = response.headers.get("Location", "")
            return urlparse(location).path + "?format=openapi"
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get API endpoint for {domain}: {str(e)}")
            raise