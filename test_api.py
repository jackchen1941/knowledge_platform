#!/usr/bin/env python3
"""测试API功能"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录"""
    print("🔐 测试登录...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@admin.com", "password": "admin12345"}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ 登录成功")
        return data["access_token"]
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def test_create_knowledge(token):
    """测试创建知识"""
    print("\n📝 测试创建知识...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "title": "测试知识条目",
        "content": "这是一个测试内容，用于验证知识创建功能。\n\n包含多行文本。",
        "summary": "测试摘要",
        "is_published": True
    }
    
    response = requests.post(
        f"{BASE_URL}/knowledge",
        headers=headers,
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:500]}")
    
    if response.status_code in [200, 201]:
        print("✅ 创建知识成功")
        return response.json()
    else:
        print(f"❌ 创建知识失败")
        return None

def test_list_knowledge(token):
    """测试列表知识"""
    print("\n📋 测试列表知识...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/knowledge",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取知识列表成功，共 {data.get('total', 0)} 条")
        return data
    else:
        print(f"❌ 获取知识列表失败: {response.text}")
        return None

def test_analytics(token):
    """测试统计"""
    print("\n📊 测试统计...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/analytics/overview",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取统计成功")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    else:
        print(f"❌ 获取统计失败: {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("API 功能测试")
    print("=" * 60)
    
    # 登录
    token = test_login()
    if not token:
        print("\n❌ 无法继续测试，登录失败")
        exit(1)
    
    # 测试创建知识
    knowledge = test_create_knowledge(token)
    
    # 测试列表知识
    test_list_knowledge(token)
    
    # 测试统计
    test_analytics(token)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
