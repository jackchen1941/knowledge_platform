#!/usr/bin/env python3
"""详细测试URL导入功能 - 支持多种URL类型"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def login():
    """登录获取token"""
    print_info("正在登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@admin.com", "password": "admin12345"}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success("登录成功")
            return token
        else:
            print_error(f"登录失败: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"登录异常: {e}")
        return None

def test_single_url_import(token, url, category="技术文档", tags=None):
    """测试单个URL导入"""
    if tags is None:
        tags = ["测试", "导入"]
    
    print(f"\n{Colors.BOLD}测试URL:{Colors.END} {url}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/import-adapters/import-url",
            headers=headers,
            params={
                "url": url,
                "category": category,
                "tags": tags
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("导入成功!")
            print(f"  📝 标题: {result['title']}")
            print(f"  🆔 知识ID: {result['knowledge_id']}")
            print(f"  📊 字数: {result['metadata']['word_count']}")
            print(f"  ⏱️  阅读时间: {result['metadata']['reading_time']}分钟")
            print(f"  🔗 来源: {result['metadata']['source_url']}")
            return True
        else:
            print_error(f"导入失败: {response.status_code}")
            print(f"  错误详情: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print_error("请求超时（30秒）")
        return False
    except Exception as e:
        print_error(f"导入异常: {e}")
        return False

def test_batch_import(token, urls, category="批量导入", tags=None):
    """测试批量URL导入"""
    if tags is None:
        tags = ["批量", "测试"]
    
    print_header("批量URL导入测试")
    print_info(f"准备导入 {len(urls)} 个URL...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/import-adapters/import-urls",
            headers=headers,
            json={
                "urls": urls,
                "category": category,
                "tags": tags
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"批量导入完成!")
            print(f"  总数: {result['total']}")
            print(f"  成功: {result['successful']}")
            print(f"  失败: {result['failed']}")
            
            print(f"\n  详细结果:")
            for r in result['results']:
                if r['success']:
                    print(f"    ✅ {r['url'][:60]}...")
                    print(f"       标题: {r['title']}")
                else:
                    print(f"    ❌ {r['url'][:60]}...")
                    print(f"       错误: {r['error']}")
            return True
        else:
            print_error(f"批量导入失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"批量导入异常: {e}")
        return False

def view_knowledge_list(token, limit=10):
    """查看知识列表"""
    print_header("知识库列表")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/knowledge",
            headers=headers,
            params={"limit": limit, "offset": 0}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"知识库共有 {data['total']} 条记录")
            print(f"\n最近的 {min(limit, len(data['items']))} 条:")
            
            for i, item in enumerate(data['items'][:limit], 1):
                print(f"\n  {i}. {item['title']}")
                print(f"     🆔 ID: {item['id']}")
                print(f"     📁 分类: {item.get('category', 'N/A')}")
                print(f"     🏷️  标签: {', '.join(item.get('tags', [])) if item.get('tags') else 'N/A'}")
                source_platform = item.get('source_platform', 'N/A')
                source_url = item.get('source_url', 'N/A')
                if source_url != 'N/A':
                    print(f"     🔗 来源: {source_platform} | {source_url[:50]}...")
            return True
        else:
            print_error(f"获取列表失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"获取列表异常: {e}")
        return False

def main():
    print_header("URL导入功能详细测试")
    
    # 登录
    token = login()
    if not token:
        print_error("无法继续测试，请检查服务是否正常运行")
        sys.exit(1)
    
    # 测试用例
    test_cases = [
        {
            "name": "GitHub README",
            "url": "https://github.com/python/cpython/blob/main/README.rst",
            "category": "开源项目",
            "tags": ["Python", "GitHub"]
        },
        # 可以添加更多测试URL
        # {
        #     "name": "技术博客",
        #     "url": "https://blog.example.com/article",
        #     "category": "技术文章",
        #     "tags": ["教程", "编程"]
        # },
    ]
    
    # 单个URL导入测试
    print_header("单个URL导入测试")
    success_count = 0
    for test_case in test_cases:
        print_info(f"测试场景: {test_case['name']}")
        if test_single_url_import(
            token,
            test_case['url'],
            test_case['category'],
            test_case['tags']
        ):
            success_count += 1
    
    print(f"\n{Colors.BOLD}单个导入测试结果: {success_count}/{len(test_cases)} 成功{Colors.END}")
    
    # 批量导入测试（可选）
    # batch_urls = [tc['url'] for tc in test_cases]
    # if len(batch_urls) > 1:
    #     test_batch_import(token, batch_urls, "批量测试", ["批量", "测试"])
    
    # 查看知识列表
    view_knowledge_list(token, limit=5)
    
    # 总结
    print_header("测试完成")
    print_success("URL导入功能测试完成！")
    print(f"\n{Colors.BOLD}💡 下一步:{Colors.END}")
    print("  1. 访问前端界面测试: http://localhost:3000")
    print("  2. 查看API文档: http://localhost:8000/docs")
    print("  3. 在前端的'导入管理'页面可以直接输入URL导入")
    print("  4. 支持的URL类型: GitHub、CSDN、知乎、掘金、简书、Medium等")
    print(f"\n{Colors.BOLD}📚 详细文档:{Colors.END}")
    print("  - MULTI_DEVICE_AND_IMPORT_GUIDE.md")
    print("  - FEATURES_SUMMARY.md")

if __name__ == "__main__":
    main()
