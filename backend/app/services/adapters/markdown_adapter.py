"""
Markdown Adapter

Adapter for importing Markdown files and content.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .base import BaseAdapter, ImportResult


class MarkdownAdapter(BaseAdapter):
    """Adapter for importing Markdown files."""
    
    platform_name = "markdown"
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.md', '.markdown', '.mdown', '.mkd']
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Markdown import configuration."""
        required_fields = ['source_path']
        
        for field in required_fields:
            if field not in config:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Check if source path exists
        source_path = config['source_path']
        if not os.path.exists(source_path):
            self.logger.error(f"Source path does not exist: {source_path}")
            return False
        
        return True
    
    async def test_connection(self, config: Dict[str, Any]) -> bool:
        """Test connection to Markdown source."""
        try:
            source_path = config['source_path']
            
            # Check if path is accessible
            if os.path.isfile(source_path):
                # Single file
                return source_path.lower().endswith(tuple(self.supported_extensions))
            elif os.path.isdir(source_path):
                # Directory - check if it contains markdown files
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        if file.lower().endswith(tuple(self.supported_extensions)):
                            return True
                return False
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_items(self, config: Dict[str, Any], since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get Markdown items from source."""
        items = []
        source_path = config['source_path']
        
        try:
            if os.path.isfile(source_path):
                # Single file
                item = await self._process_file(source_path, config, since)
                if item:
                    items.append(item)
            elif os.path.isdir(source_path):
                # Directory
                items = await self._process_directory(source_path, config, since)
            
            self.logger.info(f"Found {len(items)} Markdown items")
            return items
            
        except Exception as e:
            self.logger.error(f"Failed to get items: {e}")
            return []
    
    async def _process_file(self, file_path: str, config: Dict[str, Any], since: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Process a single Markdown file."""
        try:
            # Check file extension
            if not file_path.lower().endswith(tuple(self.supported_extensions)):
                return None
            
            # Check modification time if since is provided
            if since:
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime <= since:
                    return None
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata and content
            metadata, body = self._parse_markdown(content)
            
            # Get file info
            file_stat = os.stat(file_path)
            file_name = os.path.basename(file_path)
            
            # Create item
            item = {
                'id': self._generate_id(file_path),
                'title': metadata.get('title', os.path.splitext(file_name)[0]),
                'content': body,
                'content_type': 'markdown',
                'source_url': f"file://{file_path}",
                'created_at': datetime.fromtimestamp(file_stat.st_ctime),
                'updated_at': datetime.fromtimestamp(file_stat.st_mtime),
                'metadata': {
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_size': file_stat.st_size,
                    **metadata
                },
                'tags': metadata.get('tags', []),
                'category': metadata.get('category'),
            }
            
            return item
            
        except Exception as e:
            self.logger.error(f"Failed to process file {file_path}: {e}")
            return None
    
    async def _process_directory(self, dir_path: str, config: Dict[str, Any], since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Process all Markdown files in a directory."""
        items = []
        
        # Get recursive option
        recursive = config.get('recursive', True)
        
        if recursive:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    item = await self._process_file(file_path, config, since)
                    if item:
                        items.append(item)
        else:
            # Only process files in the current directory
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    item = await self._process_file(file_path, config, since)
                    if item:
                        items.append(item)
        
        return items
    
    def _parse_markdown(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse Markdown content and extract frontmatter."""
        metadata = {}
        body = content
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    metadata = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                except ImportError:
                    # YAML not available, try simple parsing
                    metadata = self._parse_simple_frontmatter(parts[1])
                    body = parts[2].strip()
                except Exception as e:
                    self.logger.warning(f"Failed to parse YAML frontmatter: {e}")
        
        # Extract title from first heading if not in metadata
        if 'title' not in metadata:
            title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
        
        # Extract tags from content if not in metadata
        if 'tags' not in metadata:
            tag_matches = re.findall(r'#(\w+)', body)
            if tag_matches:
                metadata['tags'] = list(set(tag_matches))
        
        return metadata, body
    
    def _parse_simple_frontmatter(self, frontmatter: str) -> Dict[str, Any]:
        """Parse simple key-value frontmatter."""
        metadata = {}
        
        for line in frontmatter.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle lists
                if value.startswith('[') and value.endswith(']'):
                    value = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                # Handle booleans
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                # Handle numbers
                elif value.isdigit():
                    value = int(value)
                
                metadata[key] = value
        
        return metadata
    
    def _generate_id(self, file_path: str) -> str:
        """Generate a unique ID for a file."""
        import hashlib
        return hashlib.md5(file_path.encode()).hexdigest()
    
    async def import_item(self, item: Dict[str, Any], user_id: str) -> ImportResult:
        """Import a single Markdown item."""
        try:
            # The actual import logic would be handled by the ImportEngine
            # This method just validates and prepares the item
            
            # Validate required fields
            required_fields = ['title', 'content']
            for field in required_fields:
                if not item.get(field):
                    return ImportResult(
                        success=False,
                        item_id=item.get('id'),
                        error=f"Missing required field: {field}"
                    )
            
            # Clean and validate content
            content = item['content'].strip()
            if len(content) < 10:  # Minimum content length
                return ImportResult(
                    success=False,
                    item_id=item.get('id'),
                    error="Content too short"
                )
            
            return ImportResult(
                success=True,
                item_id=item.get('id'),
                title=item['title'],
                imported_at=datetime.utcnow()
            )
            
        except Exception as e:
            return ImportResult(
                success=False,
                item_id=item.get('id'),
                error=str(e)
            )
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information."""
        return {
            'name': 'Markdown',
            'description': 'Import Markdown files from local filesystem',
            'version': '1.0.0',
            'supported_formats': self.supported_extensions,
            'config_schema': {
                'source_path': {
                    'type': 'string',
                    'required': True,
                    'description': 'Path to Markdown file or directory'
                },
                'recursive': {
                    'type': 'boolean',
                    'required': False,
                    'default': True,
                    'description': 'Process subdirectories recursively'
                }
            }
        }