"""
Base Adapter

Abstract base class for all import adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ImportResult:
    """Result of importing a single item."""
    success: bool
    item_id: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None
    imported_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAdapter(ABC):
    """Base class for import adapters."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize adapter with configuration.
        
        Args:
            config: Adapter-specific configuration
        """
        self.config = config or {}
        self.logger = self._get_logger()
    
    def _get_logger(self):
        """Get logger for this adapter."""
        import logging
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """
        Validate adapter configuration.
        
        Returns:
            True if configuration is valid
        """
        pass
    
    @abstractmethod
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch items from external platform.
        
        Args:
            since: Only fetch items updated after this date
            limit: Maximum number of items to fetch
            
        Returns:
            List of raw items from platform
        """
        pass
    
    @abstractmethod
    async def transform_item(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw item to standard format.
        
        Args:
            raw_item: Raw item from platform
            
        Returns:
            Transformed item in standard format:
            {
                "title": str,
                "content": str,
                "content_type": str,
                "summary": Optional[str],
                "tags": List[str],
                "category": Optional[str],
                "source_platform": str,
                "source_url": Optional[str],
                "source_id": str,
                "published_at": Optional[datetime],
                "meta_data": Dict[str, Any]
            }
        """
        pass
    
    async def import_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Import items from platform.
        
        Args:
            since: Only import items updated after this date
            limit: Maximum number of items to import
            
        Returns:
            List of transformed items ready for import
        """
        # Fetch raw items
        raw_items = await self.fetch_items(since, limit)
        
        # Transform each item
        transformed_items = []
        for raw_item in raw_items:
            try:
                transformed = await self.transform_item(raw_item)
                transformed_items.append(transformed)
            except Exception as e:
                # Log error but continue with other items
                print(f"Error transforming item: {str(e)}")
                continue
        
        return transformed_items
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return self.__class__.__name__.replace('Adapter', '').lower()
