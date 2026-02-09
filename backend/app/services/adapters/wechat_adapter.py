"""
WeChat Adapter

Adapter for importing articles from WeChat Official Account.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp

from .base import BaseAdapter


class WeChatAdapter(BaseAdapter):
    """Adapter for WeChat Official Account platform."""
    
    async def validate_config(self) -> bool:
        """Validate WeChat configuration."""
        required_fields = ['app_id', 'app_secret']
        return all(field in self.config for field in required_fields)
    
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch articles from WeChat Official Account.
        
        Note: This requires WeChat Official Account API access.
        You need to:
        1. Register as a WeChat Official Account developer
        2. Get app_id and app_secret
        3. Implement OAuth authentication
        """
        app_id = self.config.get('app_id')
        app_secret = self.config.get('app_secret')
        
        articles = []
        
        try:
            # Get access token
            access_token = await self._get_access_token(app_id, app_secret)
            
            if not access_token:
                return articles
            
            # Fetch article list
            articles = await self._fetch_article_list(access_token, limit)
        
        except Exception as e:
            print(f"Error fetching WeChat articles: {str(e)}")
        
        return articles
    
    async def _get_access_token(
        self,
        app_id: str,
        app_secret: str
    ) -> Optional[str]:
        """Get WeChat API access token."""
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': app_id,
            'secret': app_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('access_token')
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
        
        return None
    
    async def _fetch_article_list(
        self,
        access_token: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch article list from WeChat API."""
        url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material"
        
        articles = []
        offset = 0
        count = limit or 20
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'type': 'news',
                    'offset': offset,
                    'count': count
                }
                
                async with session.post(
                    f"{url}?access_token={access_token}",
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        items = result.get('item', [])
                        
                        for item in items:
                            content = item.get('content', {})
                            news_items = content.get('news_item', [])
                            
                            for news in news_items:
                                articles.append({
                                    'title': news.get('title'),
                                    'author': news.get('author'),
                                    'digest': news.get('digest'),
                                    'content': news.get('content'),
                                    'content_source_url': news.get('content_source_url'),
                                    'thumb_url': news.get('thumb_url'),
                                    'url': news.get('url'),
                                    'update_time': item.get('update_time'),
                                })
        
        except Exception as e:
            print(f"Error fetching article list: {str(e)}")
        
        return articles
    
    async def transform_item(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform WeChat article to standard format."""
        
        # Convert HTML content to Markdown
        content = self._html_to_markdown(raw_item.get('content', ''))
        
        # Parse update time
        published_at = None
        if raw_item.get('update_time'):
            try:
                published_at = datetime.fromtimestamp(raw_item['update_time'])
            except:
                pass
        
        return {
            'title': raw_item.get('title', ''),
            'content': content,
            'content_type': 'markdown',
            'summary': raw_item.get('digest', ''),
            'tags': ['微信公众号'],
            'category': '微信公众号导入',
            'source_platform': 'wechat',
            'source_url': raw_item.get('url', ''),
            'source_id': raw_item.get('url', '').split('/')[-1] if raw_item.get('url') else '',
            'published_at': published_at,
            'meta_data': {
                'author': raw_item.get('author', ''),
                'thumb_url': raw_item.get('thumb_url', ''),
                'content_source_url': raw_item.get('content_source_url', ''),
                'import_date': datetime.utcnow().isoformat(),
            }
        }
    
    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown (simplified)."""
        if not html:
            return ''
        
        # This is a simplified conversion
        # In production, use a proper HTML to Markdown converter
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style tags
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n\n'.join(lines)
