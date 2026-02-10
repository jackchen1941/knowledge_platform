#!/usr/bin/env python3
"""
知识图谱功能测试脚本
Test script for knowledge graph features
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试账户
EMAIL = "admin@admin.com"
PASSWORD = "admin12345"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def create_test_knowledge(token, title, content):
    """创建测试知识"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/knowledge",
        headers=headers,
        json={
            "title": title,
            "content": content,
            "content_type": "markdown",
            "is_published": True
        }
    )
    if response.status_code == 201:
        knowledge_id = response.json()["id"]
        print(f"✅ 创建知识成功: {title} (ID: {knowledge_id})")
        return knowledge_id
    else:
        print(f"❌ 创建知识失败: {response.text}")
        return None

def create_link(token, source_id, target_id, link_type="related", description=None):
    """创建知识链接"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "target_id": target_id,
        "link_type": link_type
    }
    if description:
        data["description"] = description
    
    response = requests.post(
        f"{BASE_URL}/knowledge/{source_id}/links",
        headers=headers,
        json=data
    )
    if response.status_code == 201:
        link_id = response.json()["id"]
        print(f"✅ 创建链接成功: {source_id} -> {target_id} ({link_type})")
        return link_id
    else:
        print(f"❌ 创建链接失败: {response.text}")
        return None

def get_links(token, knowledge_id, direction="both"):
    """获取知识链接"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/knowledge/{knowledge_id}/links?direction={direction}",
        headers=headers
    )
    if response.status_code == 200:
        links = response.json()
        print(f"✅ 获取链接成功: {len(links)} 个链接")
        return links
    else:
        print(f"❌ 获取链接失败: {response.text}")
        return []

def get_related_suggestions(token, knowledge_id):
    """获取相关知识推荐"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/knowledge/{knowledge_id}/related?limit=5",
        headers=headers
    )
    if response.status_code == 200:
        suggestions = response.json()["suggestions"]
        print(f"✅ 获取推荐成功: {len(suggestions)} 个推荐")
        return suggestions
    else:
        print(f"❌ 获取推荐失败: {response.text}")
        return []

def get_graph_stats(token):
    """获取图谱统计"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/graph/stats",
        headers=headers
    )
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 获取统计成功:")
        print(f"   总知识数: {stats['total_items']}")
        print(f"   总链接数: {stats['total_links']}")
        print(f"   孤立节点: {stats['isolated_items']}")
        print(f"   平均链接数: {stats['average_links_per_item']}")
        return stats
    else:
        print(f"❌ 获取统计失败: {response.text}")
        return None

def delete_link(token, link_id):
    """删除链接"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/links/{link_id}",
        headers=headers
    )
    if response.status_code == 204:
        print(f"✅ 删除链接成功: {link_id}")
        return True
    else:
        print(f"❌ 删除链接失败: {response.text}")
        return False

def main():
    print("=" * 60)
    print("知识图谱功能测试")
    print("=" * 60)
    print()
    
    # 1. 登录
    print("1. 登录测试")
    print("-" * 60)
    token = login()
    if not token:
        return
    print()
    
    # 2. 创建测试知识
    print("2. 创建测试知识")
    print("-" * 60)
    knowledge1 = create_test_knowledge(
        token,
        "Python基础教程",
        "这是Python基础教程的内容..."
    )
    knowledge2 = create_test_knowledge(
        token,
        "Python高级特性",
        "这是Python高级特性的内容..."
    )
    knowledge3 = create_test_knowledge(
        token,
        "Python异步编程",
        "这是Python异步编程的内容..."
    )
    print()
    
    if not all([knowledge1, knowledge2, knowledge3]):
        print("❌ 创建测试知识失败，退出测试")
        return
    
    # 3. 创建链接
    print("3. 创建知识链接")
    print("-" * 60)
    link1 = create_link(token, knowledge1, knowledge2, "prerequisite", "基础是高级的前置知识")
    link2 = create_link(token, knowledge2, knowledge3, "related", "高级特性与异步编程相关")
    print()
    
    # 4. 获取链接
    print("4. 获取知识链接")
    print("-" * 60)
    print(f"获取 {knowledge1} 的outgoing链接:")
    outgoing = get_links(token, knowledge1, "outgoing")
    for link in outgoing:
        print(f"   -> {link['target_title']} ({link['link_type']})")
    
    print(f"\n获取 {knowledge2} 的incoming链接:")
    incoming = get_links(token, knowledge2, "incoming")
    for link in incoming:
        print(f"   <- {link['source_title']} ({link['link_type']})")
    
    print(f"\n获取 {knowledge2} 的所有链接:")
    all_links = get_links(token, knowledge2, "both")
    for link in all_links:
        if link['source_id'] == knowledge2:
            print(f"   -> {link['target_title']} ({link['link_type']})")
        else:
            print(f"   <- {link['source_title']} ({link['link_type']})")
    print()
    
    # 5. 获取推荐
    print("5. 获取相关知识推荐")
    print("-" * 60)
    suggestions = get_related_suggestions(token, knowledge1)
    for item in suggestions:
        print(f"   {item['title']} (相似度: {item['score']}, 原因: {', '.join(item['reasons'])})")
    print()
    
    # 6. 获取统计
    print("6. 获取图谱统计")
    print("-" * 60)
    stats = get_graph_stats(token)
    print()
    
    # 7. 删除链接测试
    print("7. 删除链接测试")
    print("-" * 60)
    if link1:
        delete_link(token, link1)
        print("验证删除后的链接:")
        remaining = get_links(token, knowledge1, "outgoing")
        print(f"   剩余链接数: {len(remaining)}")
    print()
    
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print()
    print("📝 测试总结:")
    print(f"   - 创建了 3 个测试知识")
    print(f"   - 创建了 2 个知识链接")
    print(f"   - 测试了链接查询（outgoing/incoming/both）")
    print(f"   - 测试了相关知识推荐")
    print(f"   - 测试了图谱统计")
    print(f"   - 测试了链接删除")
    print()
    print("🌐 前端测试:")
    print(f"   访问: http://localhost:3000/knowledge/{knowledge1}")
    print("   在页面底部查看\"关联知识\"区域")
    print()

if __name__ == "__main__":
    main()
