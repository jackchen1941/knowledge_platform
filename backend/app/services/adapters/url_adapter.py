"""
URL Adapter

Universal adapter for importing articles from any public URL.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

from .base import BaseAdapter


class URLAdapter(BaseAdapter):
    """Universal adapter for importing from any URL."""
    
    async def validate_config(self) -> bool:
        """Validate URL configuration."""
        return 'url' in self.config
    
    async def fetch_items(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch article from URL.
        
        Returns a single item list.
        """
        url = self.config.get('url')
        
        if not url:
            return []
        
        try:
            article = await self._fetch_article(url)
            if article:
                return [article]
        except Exception as e:
            print(f"Error fetching URL {url}: {str(e)}")
        
        return []
    
    async def _fetch_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch article content from URL."""
        try:
            # 更完整的请求头，模拟真实浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
            
            # 创建会话并设置超时
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.get(url, headers=headers, allow_redirects=True) as response:
                        # 检查响应状态
                        if response.status != 200:
                            print(f"HTTP {response.status} for URL {url}")
                            return None
                        
                        # 获取内容
                        html = await response.text()
                        
                        # 检查是否获取到内容
                        if not html or len(html) < 100:
                            print(f"Empty or too short content from {url}")
                            return None
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract article data
                        title = self._extract_title(soup, url)
                        content = self._extract_content(soup)
                        author = self._extract_author(soup)
                        published_at = self._extract_date(soup)
                        tags = self._extract_tags(soup)
                        
                        # 验证提取的内容
                        if not title:
                            print(f"Could not extract title from {url}")
                            title = "未命名文章"
                        
                        if not content or len(content) < 50:
                            print(f"Could not extract sufficient content from {url}")
                            return None
                        
                        return {
                            'url': url,
                            'title': title,
                            'content': content,
                            'author': author,
                            'published_at': published_at,
                            'tags': tags,
                        }
                
                except aiohttp.ClientError as e:
                    print(f"Client error fetching {url}: {str(e)}")
                    return None
                except asyncio.TimeoutError:
                    print(f"Timeout fetching {url}")
                    return None
        
        except Exception as e:
            print(f"Error fetching article {url}: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract article title."""
        # Try multiple methods to find title
        
        # Method 1: <title> tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text.strip()
            # Clean up common suffixes
            title = re.sub(r'\s*[-_|]\s*.*$', '', title)
            if title:
                return title
        
        # Method 2: <h1> tag
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.text.strip()
        
        # Method 3: meta og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Method 4: meta twitter:title
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()
        
        # Fallback: use URL
        return url.split('/')[-1].replace('-', ' ').replace('_', ' ')
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content."""
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
            tag.decompose()
        
        # Try to find article content using common patterns
        content_selectors = [
            'article',
            '[class*="article"]',
            '[class*="content"]',
            '[class*="post"]',
            '[id*="article"]',
            '[id*="content"]',
            '[id*="post"]',
            'main',
            '.markdown-body',  # GitHub
            '#content_views',  # CSDN
            '.article-content',  # Common
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        # If no specific content area found, use body
        if not content_elem:
            content_elem = soup.find('body')
        
        if not content_elem:
            return ''
        
        # Convert to markdown
        return self._html_to_markdown(str(content_elem))
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author."""
        # Try meta tags
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            return author_meta['content'].strip()
        
        # Try og:author
        og_author = soup.find('meta', property='og:author')
        if og_author and og_author.get('content'):
            return og_author['content'].strip()
        
        # Try common class names
        author_selectors = [
            '.author',
            '.author-name',
            '[class*="author"]',
            '[rel="author"]',
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                return author_elem.text.strip()
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date."""
        # Try meta tags
        date_meta = soup.find('meta', property='article:published_time')
        if date_meta and date_meta.get('content'):
            try:
                return datetime.fromisoformat(date_meta['content'].replace('Z', '+00:00'))
            except:
                pass
        
        # Try time tag
        time_tag = soup.find('time')
        if time_tag:
            datetime_attr = time_tag.get('datetime')
            if datetime_attr:
                try:
                    return datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                except:
                    pass
        
        return None
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract article tags."""
        tags = []
        
        # Try meta keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta and keywords_meta.get('content'):
            keywords = keywords_meta['content'].split(',')
            tags.extend([k.strip() for k in keywords if k.strip()])
        
        # Try article:tag meta
        tag_metas = soup.find_all('meta', property='article:tag')
        for tag_meta in tag_metas:
            if tag_meta.get('content'):
                tags.append(tag_meta['content'].strip())
        
        # Try common tag elements
        tag_selectors = [
            '.tag',
            '.tags a',
            '[class*="tag"] a',
            '[rel="tag"]',
        ]
        
        for selector in tag_selectors:
            tag_elems = soup.select(selector)
            for elem in tag_elems:
                tag_text = elem.text.strip()
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
        
        return tags[:10]  # Limit to 10 tags
    
    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown with better formatting."""
        if not html:
            return ''
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Build markdown recursively
        def process_element(elem, depth=0) -> str:
            if isinstance(elem, str):
                text = elem.strip()
                return text if text else ''
            
            if not hasattr(elem, 'name'):
                return ''
            
            result = []
            
            if elem.name == 'h1':
                return f"\n# {elem.get_text().strip()}\n\n"
            elif elem.name == 'h2':
                return f"\n## {elem.get_text().strip()}\n\n"
            elif elem.name == 'h3':
                return f"\n### {elem.get_text().strip()}\n\n"
            elif elem.name == 'h4':
                return f"\n#### {elem.get_text().strip()}\n\n"
            elif elem.name == 'h5':
                return f"\n##### {elem.get_text().strip()}\n\n"
            elif elem.name == 'h6':
                return f"\n###### {elem.get_text().strip()}\n\n"
            elif elem.name == 'p':
                text = ''.join(process_element(child, depth) for child in elem.children)
                return f"\n{text.strip()}\n\n" if text.strip() else ''
            elif elem.name == 'br':
                return "\n"
            elif elem.name == 'strong' or elem.name == 'b':
                return f"**{elem.get_text().strip()}**"
            elif elem.name == 'em' or elem.name == 'i':
                return f"*{elem.get_text().strip()}*"
            elif elem.name == 'code':
                return f"`{elem.get_text().strip()}`"
            elif elem.name == 'pre':
                code = elem.find('code')
                if code:
                    lang = ''
                    if code.get('class'):
                        classes = code.get('class')
                        for cls in classes:
                            if cls.startswith('language-'):
                                lang = cls.replace('language-', '')
                                break
                    return f"\n```{lang}\n{code.get_text()}\n```\n\n"
                else:
                    return f"\n```\n{elem.get_text()}\n```\n\n"
            elif elem.name == 'a':
                href = elem.get('href', '')
                text = elem.get_text().strip()
                if href and text:
                    return f"[{text}]({href})"
                return text
            elif elem.name == 'img':
                src = elem.get('src', '')
                alt = elem.get('alt', 'image')
                if src:
                    return f"\n![{alt}]({src})\n\n"
                return ''
            elif elem.name == 'ul':
                items = []
                for li in elem.find_all('li', recursive=False):
                    text = ''.join(process_element(child, depth+1) for child in li.children)
                    items.append(f"- {text.strip()}")
                return '\n' + '\n'.join(items) + '\n\n' if items else ''
            elif elem.name == 'ol':
                items = []
                for i, li in enumerate(elem.find_all('li', recursive=False), 1):
                    text = ''.join(process_element(child, depth+1) for child in li.children)
                    items.append(f"{i}. {text.strip()}")
                return '\n' + '\n'.join(items) + '\n\n' if items else ''
            elif elem.name == 'li':
                # Already handled in ul/ol
                return ''.join(process_element(child, depth) for child in elem.children)
            elif elem.name == 'blockquote':
                lines = elem.get_text().strip().split('\n')
                quoted = '\n'.join(f"> {line.strip()}" for line in lines if line.strip())
                return f"\n{quoted}\n\n"
            elif elem.name == 'hr':
                return "\n---\n\n"
            elif elem.name == 'table':
                # Simple table support
                rows = elem.find_all('tr')
                if not rows:
                    return ''
                
                table_md = []
                for i, row in enumerate(rows):
                    cells = row.find_all(['th', 'td'])
                    row_text = ' | '.join(cell.get_text().strip() for cell in cells)
                    table_md.append(f"| {row_text} |")
                    
                    # Add separator after header
                    if i == 0:
                        separator = ' | '.join(['---'] * len(cells))
                        table_md.append(f"| {separator} |")
                
                return '\n' + '\n'.join(table_md) + '\n\n' if table_md else ''
            else:
                # Process children for other elements
                return ''.join(process_element(child, depth) for child in elem.children)
        
        markdown = process_element(soup)
        
        # Clean up excessive whitespace
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        markdown = re.sub(r' {2,}', ' ', markdown)
        
        return markdown.strip()
    
    async def transform_item(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform URL article to standard format."""
        
        # Generate summary from content
        content = raw_item.get('content', '')
        summary = self._generate_summary(content)
        
        return {
            'title': raw_item['title'],
            'content': content,
            'content_type': 'markdown',
            'summary': summary,
            'tags': raw_item.get('tags', []),
            'category': '网页导入',
            'source_platform': 'url',
            'source_url': raw_item['url'],
            'source_id': raw_item['url'],
            'published_at': raw_item.get('published_at'),
            'meta_data': {
                'author': raw_item.get('author'),
                'import_date': datetime.utcnow().isoformat(),
                'original_url': raw_item['url'],
            }
        }
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate summary from content."""
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]()]', '', content)
        text = re.sub(r'\n+', ' ', text)
        text = text.strip()
        
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence boundary
        summary = text[:max_length]
        last_period = summary.rfind('。')
        if last_period > max_length * 0.7:
            summary = summary[:last_period + 1]
        else:
            last_period = summary.rfind('.')
            if last_period > max_length * 0.7:
                summary = summary[:last_period + 1]
            else:
                summary = summary + '...'
        
        return summary
