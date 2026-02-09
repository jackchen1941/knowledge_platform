"""
Notion Adapter

Adapter for importing pages from Notion workspace.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp

from .base import BaseAdapter


class NotionAdapter(BaseAdapter):
    """Adapter for Notion workspace."""
    
    async def validate_config(self) -> bool:
        """Validate Notion configuration."""
        required_fields = ['api_key']
        return all(field in self.config for field in required_fields)
    
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch pages from Notion workspace.
        
        Requires Notion Integration API key.
        See: https://developers.notion.com/
        """
        api_key = self.config.get('api_key')
        database_id = self.config.get('database_id')  # Optional: specific database
        
        pages = []
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                if database_id:
                    # Query specific database
                    pages = await self._query_database(session, database_id, limit)
                else:
                    # Search all pages
                    pages = await self._search_pages(session, limit)
        
        except Exception as e:
            print(f"Error fetching Notion pages: {str(e)}")
        
        return pages
    
    async def _query_database(
        self,
        session: aiohttp.ClientSession,
        database_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query pages from a specific Notion database."""
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        
        data = {
            'page_size': limit or 100
        }
        
        pages = []
        
        try:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    results = result.get('results', [])
                    
                    for page in results:
                        # Fetch full page content
                        page_content = await self._fetch_page_content(
                            session,
                            page['id']
                        )
                        if page_content:
                            page['content'] = page_content
                            pages.append(page)
        
        except Exception as e:
            print(f"Error querying database: {str(e)}")
        
        return pages
    
    async def _search_pages(
        self,
        session: aiohttp.ClientSession,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search all accessible pages."""
        url = "https://api.notion.com/v1/search"
        
        data = {
            'filter': {
                'property': 'object',
                'value': 'page'
            },
            'page_size': limit or 100
        }
        
        pages = []
        
        try:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    results = result.get('results', [])
                    
                    for page in results:
                        # Fetch full page content
                        page_content = await self._fetch_page_content(
                            session,
                            page['id']
                        )
                        if page_content:
                            page['content'] = page_content
                            pages.append(page)
        
        except Exception as e:
            print(f"Error searching pages: {str(e)}")
        
        return pages
    
    async def _fetch_page_content(
        self,
        session: aiohttp.ClientSession,
        page_id: str
    ) -> Optional[str]:
        """Fetch page content blocks."""
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    blocks = result.get('results', [])
                    
                    # Convert blocks to markdown
                    return self._blocks_to_markdown(blocks)
        
        except Exception as e:
            print(f"Error fetching page content: {str(e)}")
        
        return None
    
    def _blocks_to_markdown(self, blocks: List[Dict[str, Any]]) -> str:
        """Convert Notion blocks to Markdown."""
        markdown_lines = []
        
        for block in blocks:
            block_type = block.get('type')
            
            if block_type == 'paragraph':
                text = self._extract_rich_text(block['paragraph'].get('rich_text', []))
                markdown_lines.append(text)
                markdown_lines.append('')
            
            elif block_type == 'heading_1':
                text = self._extract_rich_text(block['heading_1'].get('rich_text', []))
                markdown_lines.append(f'# {text}')
                markdown_lines.append('')
            
            elif block_type == 'heading_2':
                text = self._extract_rich_text(block['heading_2'].get('rich_text', []))
                markdown_lines.append(f'## {text}')
                markdown_lines.append('')
            
            elif block_type == 'heading_3':
                text = self._extract_rich_text(block['heading_3'].get('rich_text', []))
                markdown_lines.append(f'### {text}')
                markdown_lines.append('')
            
            elif block_type == 'bulleted_list_item':
                text = self._extract_rich_text(block['bulleted_list_item'].get('rich_text', []))
                markdown_lines.append(f'- {text}')
            
            elif block_type == 'numbered_list_item':
                text = self._extract_rich_text(block['numbered_list_item'].get('rich_text', []))
                markdown_lines.append(f'1. {text}')
            
            elif block_type == 'code':
                code = self._extract_rich_text(block['code'].get('rich_text', []))
                language = block['code'].get('language', '')
                markdown_lines.append(f'```{language}')
                markdown_lines.append(code)
                markdown_lines.append('```')
                markdown_lines.append('')
        
        return '\n'.join(markdown_lines)
    
    def _extract_rich_text(self, rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text from Notion rich text."""
        return ''.join([item.get('plain_text', '') for item in rich_text])
    
    async def transform_item(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Notion page to standard format."""
        
        # Extract title
        title = ''
        properties = raw_item.get('properties', {})
        
        # Try to find title property
        for prop_name, prop_value in properties.items():
            if prop_value.get('type') == 'title':
                title_array = prop_value.get('title', [])
                if title_array:
                    title = title_array[0].get('plain_text', '')
                break
        
        # Extract tags
        tags = []
        for prop_name, prop_value in properties.items():
            if prop_value.get('type') == 'multi_select':
                tags = [item['name'] for item in prop_value.get('multi_select', [])]
                break
        
        # Parse dates
        created_time = raw_item.get('created_time')
        published_at = None
        if created_time:
            try:
                published_at = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
            except:
                pass
        
        return {
            'title': title or 'Untitled',
            'content': raw_item.get('content', ''),
            'content_type': 'markdown',
            'summary': self._generate_summary(raw_item.get('content', '')),
            'tags': tags or ['Notion'],
            'category': 'Notion导入',
            'source_platform': 'notion',
            'source_url': raw_item.get('url', ''),
            'source_id': raw_item.get('id', ''),
            'published_at': published_at,
            'meta_data': {
                'notion_id': raw_item.get('id', ''),
                'parent': raw_item.get('parent', {}),
                'import_date': datetime.utcnow().isoformat(),
            }
        }
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate summary from content."""
        if len(content) <= max_length:
            return content
        return content[:max_length] + '...'
