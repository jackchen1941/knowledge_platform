#!/usr/bin/env python3
"""
URL导入功能演示脚本

展示如何使用API导入不同类型的URL
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def main():
    print_header("URL导入功能演示")
    
    # 登录
    print_info("正在登录...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@admin.com", "password": "admin12345"}
    )
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    print_success("登录成功")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 演示URL列表
    demo_urls = [
        {
            "url": "https://github.com/python/cpython/blob/main/README.rst",
            "category": "开源项目",
            "tags": ["Python", "GitHub"],
            "description": "Python官方仓库README"
        },
        # 可以添加更多演示URL
    ]
    
    print_header("开始导入演示")
    
    for i, demo in enumerate(demo_urls, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(demo_urls)}] {demo['description']}{Colors.END}")
        print(f"URL: {demo['url']}")
        
        try:
            params = {
                "url": demo['url'],
                "category": demo['category'],
                "tags": demo['tags']
            }
            
            response = requests.post(
                f"{BASE_URL}/import-adapters/import-url",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success("导入成功!")
                print(f"  📝 标题: {result['title']}")
                print(f"  🆔 ID: {result['knowledge_id']}")
                print(f"  📊 字数: {result['metadata']['word_count']}")
                print(f"  ⏱️  阅读时间: {result['metadata']['reading_time']}分钟")
            else:
                print(f"❌ 导入失败: {response.status_code}")
                print(f"  错误: {response.text[:200]}")
        
        except requests.exceptions.Timeout:
            print("⚠️  请求超时（30秒）")
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        # 避免请求过快
        if i < len(demo_urls):
            time.sleep(2)
    
    print_header("演示完成")
    print_success("所有URL导入演示完成！")
    print(f"\n{Colors.BOLD}💡 下一步:{Colors.END}")
    print("  1. 访问前端查看导入的内容: http://localhost:3000")
    print("  2. 在'知识管理'页面查看所有文章")
    print("  3. 尝试导入你自己的URL")
    print(f"\n{Colors.BOLD}📚 使用指南:{Colors.END}")
    print("  - URL_IMPORT_GUIDE.md - 详细使用说明")
    print("  - MULTI_DEVICE_AND_IMPORT_GUIDE.md - 完整功能指南")

if __name__ == "__main__":
    main()
