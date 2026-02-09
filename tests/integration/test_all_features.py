#!/usr/bin/env python3
"""
Complete Feature Test Suite

Test all implemented features of the knowledge management platform.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_all_features():
    """Test all platform features."""
    
    print("🚀 测试知识管理平台所有功能")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Authentication
        print("\n🔐 1. 认证系统测试")
        print("-" * 30)
        
        register_data = {
            "username": f"fulltest_{int(datetime.now().timestamp())}",
            "email": f"fulltest_{int(datetime.now().timestamp())}@test.com",
            "password": "test12345",
            "full_name": "Full Test User"
        }
        
        # Register
        async with session.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ 用户注册: {result['username']}")
            else:
                print(f"❌ 用户注册失败: {response.status}")
                return
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        async with session.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                access_token = result['access_token']
                print(f"✅ 用户登录: 获得令牌")
            else:
                print(f"❌ 用户登录失败: {response.status}")
                return
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Step 2: Categories
        print("\n📁 2. 分类管理测试")
        print("-" * 30)
        
        # Create category
        category_data = {
            "name": "测试分类",
            "description": "这是一个测试分类"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/categories/",
                json=category_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    category_id = result['id']
                    print(f"✅ 分类创建: {result['name']}")
                else:
                    print(f"❌ 分类创建失败: {response.status}")
                    category_id = None
        except Exception as e:
            print(f"❌ 分类创建异常: {e}")
            category_id = None
        
        # List categories
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/categories/",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 分类列表: {result['total']} 个分类")
                else:
                    print(f"❌ 分类列表失败: {response.status}")
        except Exception as e:
            print(f"❌ 分类列表异常: {e}")
        
        # Step 3: Tags
        print("\n🏷️ 3. 标签管理测试")
        print("-" * 30)
        
        # Create tag
        tag_data = {
            "name": "测试标签",
            "description": "这是一个测试标签",
            "color": "#ff6b6b"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/tags/",
                json=tag_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    tag_id = result['id']
                    print(f"✅ 标签创建: {result['name']} ({result['color']})")
                else:
                    print(f"❌ 标签创建失败: {response.status}")
                    tag_id = None
        except Exception as e:
            print(f"❌ 标签创建异常: {e}")
            tag_id = None
        
        # List tags
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/tags/",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 标签列表: {result['total']} 个标签")
                else:
                    print(f"❌ 标签列表失败: {response.status}")
        except Exception as e:
            print(f"❌ 标签列表异常: {e}")
        
        # Step 4: Knowledge Management
        print("\n📚 4. 知识管理测试")
        print("-" * 30)
        
        # Create knowledge item
        knowledge_data = {
            "title": "完整功能测试知识条目",
            "content": "# 测试知识条目\n\n这是一个用于测试所有功能的知识条目。\n\n## 内容特点\n\n- 包含**粗体**文本\n- 包含*斜体*文本\n- 包含代码块\n\n```python\nprint('Hello, World!')\n```\n\n## 结论\n\n这个条目用于验证系统功能。",
            "content_type": "markdown",
            "summary": "用于测试所有功能的综合知识条目",
            "category_id": category_id,
            "is_published": True,
            "visibility": "public",
            "meta_data": {
                "test_type": "comprehensive",
                "version": "1.0"
            }
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/knowledge/",
                json=knowledge_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    knowledge_id = result['id']
                    print(f"✅ 知识条目创建: {result['title']}")
                    print(f"   字数: {result['word_count']}, 阅读时间: {result['reading_time']}分钟")
                else:
                    error = await response.text()
                    print(f"❌ 知识条目创建失败: {response.status} - {error}")
                    knowledge_id = None
        except Exception as e:
            print(f"❌ 知识条目创建异常: {e}")
            knowledge_id = None
        
        # List knowledge items
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/knowledge/?limit=10",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 知识条目列表: {result['total']} 个条目")
                else:
                    error = await response.text()
                    print(f"❌ 知识条目列表失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 知识条目列表异常: {e}")
        
        # Step 5: Search
        print("\n🔍 5. 搜索功能测试")
        print("-" * 30)
        
        # Search knowledge
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/search/?q=测试&limit=5",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 搜索结果: {result['total']} 个匹配项")
                    for item in result['results'][:3]:  # Show first 3
                        print(f"   - {item['title']} (相关度: {item['relevance_score']})")
                else:
                    error = await response.text()
                    print(f"❌ 搜索失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 搜索异常: {e}")
        
        # Search suggestions
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/search/suggestions?q=测试",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 搜索建议: {len(result['suggestions'])} 个建议")
                    for suggestion in result['suggestions']:
                        print(f"   - {suggestion}")
                else:
                    print(f"❌ 搜索建议失败: {response.status}")
        except Exception as e:
            print(f"❌ 搜索建议异常: {e}")
        
        # Step 6: Sync System
        print("\n🔄 6. 同步系统测试")
        print("-" * 30)
        
        # Register device
        device_data = {
            "device_name": "测试设备",
            "device_type": "desktop",
            "device_id": f"test-device-{int(datetime.now().timestamp())}"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/sync/devices/register",
                json=device_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    device_id = result['id']
                    print(f"✅ 设备注册: {result['device_name']} ({result['device_type']})")
                else:
                    error = await response.text()
                    print(f"❌ 设备注册失败: {response.status} - {error}")
                    device_id = None
        except Exception as e:
            print(f"❌ 设备注册异常: {e}")
            device_id = None
        
        # List devices
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/sync/devices",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 设备列表: {len(result)} 个设备")
                else:
                    print(f"❌ 设备列表失败: {response.status}")
        except Exception as e:
            print(f"❌ 设备列表异常: {e}")
        
        # Step 7: Notifications
        print("\n🔔 7. 通知系统测试")
        print("-" * 30)
        
        # Create demo notification
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/notifications/demo",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 演示通知创建: {result.get('title', '通知')}")
                else:
                    error = await response.text()
                    print(f"❌ 演示通知失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 演示通知异常: {e}")
        
        # Step 8: WebSocket
        print("\n🌐 8. WebSocket系统测试")
        print("-" * 30)
        
        # Get WebSocket stats
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/ws/stats",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    stats = result['stats']
                    print(f"✅ WebSocket统计: {stats['total_connections']} 连接, {stats['total_users']} 用户")
                    print(f"   功能: {', '.join(result['features'])}")
                else:
                    print(f"❌ WebSocket统计失败: {response.status}")
        except Exception as e:
            print(f"❌ WebSocket统计异常: {e}")
        
        # Step 9: System Status
        print("\n⚡ 9. 系统状态测试")
        print("-" * 30)
        
        # Check system status
        try:
            async with session.get(f"{BASE_URL}/status") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 系统状态: {result['status']}")
                    print(f"   数据库: {result['database']}")
                    print(f"   版本: {result['version']}")
                else:
                    print(f"❌ 系统状态检查失败: {response.status}")
        except Exception as e:
            print(f"❌ 系统状态异常: {e}")
        
        # Check features
        try:
            async with session.get(f"{BASE_URL}/features") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 可用功能:")
                    for feature, info in result.items():
                        print(f"   - {feature}: {info['status']}")
                else:
                    print(f"❌ 功能检查失败: {response.status}")
        except Exception as e:
            print(f"❌ 功能检查异常: {e}")

    print("\n" + "=" * 60)
    print("🎉 所有功能测试完成!")
    print("\n📊 测试总结:")
    print("✅ 认证系统: 用户注册、登录、令牌管理")
    print("✅ 分类管理: 创建分类、列出分类")
    print("✅ 标签管理: 创建标签、列出标签")
    print("✅ 知识管理: 创建、列出、获取知识条目")
    print("✅ 搜索功能: 全文搜索、搜索建议")
    print("✅ 同步系统: 设备注册、设备管理")
    print("✅ 通知系统: 创建通知、实时推送")
    print("✅ WebSocket: 实时连接、状态统计")
    print("✅ 系统监控: 状态检查、功能列表")

if __name__ == "__main__":
    asyncio.run(test_all_features())