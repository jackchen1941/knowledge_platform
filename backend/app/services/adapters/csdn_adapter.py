"""
CSDN Adapter

Adapter for importing articles from CSDN blog platform.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

from .base import BaseAdapter


class CSDNAdapter(BaseAdapter):
    """Adapter for CSDN blog platform."""
    
    async def validate_config(self) -> bool:
        """Validate CSDN configuration."""
        required_fields = ['username']
        return all(field in self.config for field in required_fields)
    
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch articles from CSDN blog.
        
        Note: This is a simplified implementation. In production, you would:
        1. Use CSDN's official API if available
        2. Handle pagination properly
        3. Add rate limiting
        4. Handle authentication if needed
        """
        username = self.config.get('username')
        blog_url = f"https://blog.csdn.net/{username}"
        
        articles = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch blog homepage
                async with session.get(blog_url) as response:
                    if response.status != 200:
                        return articles
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find article links (this is a simplified example)
                    # In reality, you'd need to parse CSDN's actual HTML structure
                    article_links = soup.find_all('a', class_='article-link')
                    
                    for link in article_links[:limit] if limit else article_links:
                        article_url = link.get('href')
                        if article_url:
                            article = await self._fetch_article(session, article_url)
                            if article:
                                articles.append(article)
        
        except Exception as e:
            print(f"Error fetching CSDN articles: {str(e)}")
        
        return articles
    
    async def _fetch_article(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch single article content."""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract article data (simplified)
                title_elem = soup.find('h1', class_='title-article')
                content_elem = soup.find('div', id='content_views')
                time_elem = soup.find('span', class_='time')
                tags_elem = soup.find_all('a', class_='tag-link')
                
                if not title_elem or not content_elem:
                    return None
                
                return {
                    'url': url,
                    'title': title_elem.text.strip(),
                    'content': content_elem.get_text(),
                    'html_content': str(content_elem),
                    'published_at': time_elem.text.strip() if time_elem else None,
                    'tags': [tag.text.strip() for tag in tags_elem],
                }
        
        except Exception as e:
            print(f"Error fetching article {url}: {str(e)}")
            return None
    
    async def transform_item(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CSDN article to standard format."""
        
        # Convert HTML to Markdown (simplified)
        content = self._html_to_markdown(raw_item.get('html_content', ''))
        
        # Parse published date
        published_at = None
        if raw_item.get('published_at'):
            try:
                published_at = datetime.strptime(
                    raw_item['published_at'],
                    '%Y-%m-%d %H:%M:%S'
                )
            except:
                pass
        
        return {
            'title': raw_item['title'],
            'content': content,
            'content_type': 'markdown',
            'summary': self._generate_summary(content),
            'tags': raw_item.get('tags', []),
            'category': 'CSDN导入',
            'source_platform': 'csdn',
            'source_url': raw_item['url'],
            'source_id': self._extract_article_id(raw_item['url']),
            'published_at': published_at,
            'meta_data': {
                'original_html': raw_item.get('html_content', ''),
                'import_date': datetime.utcnow().isoformat(),
            }
        }
    
    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown (simplified)."""
        if not html:
            return ''
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style tags
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n\n'.join(lines)
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate summary from content."""
        if len(content) <= max_length:
            return content
        return content[:max_length] + '...'
    
    def _extract_article_id(self, url: str) -> str:
        """Extract article ID from URL."""
        # Example: https://blog.csdn.net/username/article/details/123456
        match = re.search(r'/article/details/(\d+)', url)
        if match:
            return match.group(1)
        return url
