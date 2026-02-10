#!/usr/bin/env python3
"""快速测试URL导入功能"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试URL列表
TEST_URLS = [
    "https://github.com/python/cpython/blob/main/README.rst",
    # 可以添加更多你想测试的URL
]

def test_url_import():
    print("=" * 60)
    print("URL导入功能测试")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@admin.com", "password": "admin12345"}
    )
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    print("✅ 登录成功")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 测试URL导入
    for url in TEST_URLS:
        print(f"\n2. 从URL导入: {url}")
        response = requests.post(
            f"{BASE_URL}/import-adapters/import-url",
            headers=headers,
            params={
                "url": url,
                "category": "技术文档",
                "tags": ["测试", "导入"]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 导入成功!")
            print(f"   标题: {result['title']}")
            print(f"   知识ID: {result['knowledge_id']}")
            print(f"   字数: {result['metadata']['word_count']}")
            print(f"   阅读时间: {result['metadata']['reading_time']}分钟")
        else:
            print(f"❌ 导入失败: {response.status_code}")
            print(f"   错误: {response.text[:200]}")
    
    # 3. 查看导入的知识列表
    print(f"\n3. 查看知识列表...")
    response = requests.get(
        f"{BASE_URL}/knowledge",
        headers=headers,
        params={"limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 共有 {data['total']} 条知识")
        print(f"\n最近的5条:")
        for item in data['items'][:5]:
            print(f"   - {item['title']}")
            print(f"     来源: {item.get('source_platform', 'N/A')} | URL: {item.get('source_url', 'N/A')[:50]}...")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("1. 访问 http://localhost:3000 查看前端界面")
    print("2. 访问 http://localhost:8000/docs 查看API文档")
    print("3. 在前端可以直接测试URL导入功能")

if __name__ == "__main__":
    test_url_import()
