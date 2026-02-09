#!/usr/bin/env python3
"""
Complete Knowledge Management System Test

Test knowledge item CRUD operations.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_knowledge_system():
    """Test complete knowledge management flow."""
    
    print("📚 测试完整知识管理系统")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Register and login to get token
        print("\n1️⃣ 用户认证")
        register_data = {
            "username": f"knowledge_test_{int(datetime.now().timestamp())}",
            "email": f"knowledge_test_{int(datetime.now().timestamp())}@test.com",
            "password": "test12345",
            "full_name": "Knowledge Test User"
        }
        
        # Register user
        async with session.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ 用户注册成功: {result['username']}")
            else:
                print(f"❌ 用户注册失败: {response.status}")
                return
        
        # Login user
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
                print(f"✅ 用户登录成功，获得令牌")
            else:
                print(f"❌ 用户登录失败: {response.status}")
                return
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Step 2: Create Knowledge Item
        print("\n2️⃣ 创建知识条目")
        knowledge_data = {
            "title": "测试知识条目",
            "content": "# 这是一个测试知识条目\n\n这里是内容部分，包含一些**重要信息**。\n\n## 子标题\n\n- 列表项1\n- 列表项2\n- 列表项3",
            "content_type": "markdown",
            "summary": "这是一个用于测试的知识条目摘要",
            "is_published": True,
            "visibility": "public",
            "meta_data": {
                "tags": ["测试", "知识管理"],
                "difficulty": "初级"
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
                    print(f"✅ 知识条目创建成功: {result['title']}")
                    print(f"   ID: {knowledge_id}")
                    print(f"   字数: {result['word_count']}")
                    print(f"   阅读时间: {result['reading_time']}分钟")
                else:
                    error = await response.text()
                    print(f"❌ 知识条目创建失败: {response.status} - {error}")
                    return
        except Exception as e:
            print(f"❌ 创建知识条目请求失败: {e}")
            return
        
        # Step 3: Get Knowledge Item
        print("\n3️⃣ 获取知识条目")
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/knowledge/{knowledge_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 成功获取知识条目: {result['title']}")
                    print(f"   内容长度: {len(result['content'])} 字符")
                    print(f"   发布状态: {'已发布' if result['is_published'] else '草稿'}")
                else:
                    error = await response.text()
                    print(f"❌ 获取知识条目失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 获取知识条目请求失败: {e}")
        
        # Step 4: Update Knowledge Item
        print("\n4️⃣ 更新知识条目")
        update_data = {
            "title": "更新后的测试知识条目",
            "content": knowledge_data["content"] + "\n\n## 更新内容\n\n这是更新后添加的内容。",
            "summary": "这是更新后的摘要",
            "meta_data": {
                "tags": ["测试", "知识管理", "更新"],
                "difficulty": "中级",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        try:
            async with session.put(
                f"{BASE_URL}/api/v1/knowledge/{knowledge_id}",
                json=update_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 知识条目更新成功: {result['title']}")
                    print(f"   更新时间: {result['updated_at']}")
                else:
                    error = await response.text()
                    print(f"❌ 知识条目更新失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 更新知识条目请求失败: {e}")
        
        # Step 5: List Knowledge Items
        print("\n5️⃣ 列出知识条目")
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/knowledge/?limit=10&offset=0",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 成功获取知识条目列表: {result['total']} 个条目")
                    for item in result['items']:
                        print(f"   - {item['title']} ({item['word_count']} 字)")
                else:
                    error = await response.text()
                    print(f"❌ 获取知识条目列表失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 获取知识条目列表请求失败: {e}")
        
        # Step 6: Search Knowledge Items
        print("\n6️⃣ 搜索知识条目")
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/knowledge/?search=测试&limit=5",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 搜索结果: {result['total']} 个匹配条目")
                    for item in result['items']:
                        print(f"   - {item['title']}")
                else:
                    error = await response.text()
                    print(f"❌ 搜索知识条目失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 搜索知识条目请求失败: {e}")
        
        # Step 7: Create Another Knowledge Item
        print("\n7️⃣ 创建第二个知识条目")
        knowledge_data2 = {
            "title": "第二个测试知识条目",
            "content": "这是第二个知识条目的内容。\n\n包含不同的信息和结构。",
            "content_type": "markdown",
            "summary": "第二个知识条目的摘要",
            "is_published": False,  # 草稿状态
            "visibility": "private",
            "meta_data": {
                "category": "测试分类",
                "priority": "低"
            }
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/knowledge/",
                json=knowledge_data2,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    knowledge_id2 = result['id']
                    print(f"✅ 第二个知识条目创建成功: {result['title']}")
                    print(f"   状态: {'已发布' if result['is_published'] else '草稿'}")
                else:
                    error = await response.text()
                    print(f"❌ 第二个知识条目创建失败: {response.status} - {error}")
                    knowledge_id2 = None
        except Exception as e:
            print(f"❌ 创建第二个知识条目请求失败: {e}")
            knowledge_id2 = None
        
        # Step 8: Filter by Published Status
        print("\n8️⃣ 按发布状态过滤")
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/knowledge/?is_published=true",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 已发布的知识条目: {result['total']} 个")
                    for item in result['items']:
                        print(f"   - {item['title']} (已发布)")
                else:
                    error = await response.text()
                    print(f"❌ 过滤已发布条目失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 过滤已发布条目请求失败: {e}")
        
        # Step 9: Delete Knowledge Item
        print("\n9️⃣ 删除知识条目")
        if knowledge_id2:
            try:
                async with session.delete(
                    f"{BASE_URL}/api/v1/knowledge/{knowledge_id2}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ 知识条目删除成功: {result['message']}")
                    else:
                        error = await response.text()
                        print(f"❌ 知识条目删除失败: {response.status} - {error}")
            except Exception as e:
                print(f"❌ 删除知识条目请求失败: {e}")
        
        # Step 10: Verify Deletion
        print("\n🔟 验证删除")
        if knowledge_id2:
            try:
                async with session.get(
                    f"{BASE_URL}/api/v1/knowledge/{knowledge_id2}",
                    headers=headers
                ) as response:
                    if response.status == 404:
                        print("✅ 确认知识条目已被删除")
                    else:
                        print(f"❌ 知识条目删除验证失败: {response.status}")
            except Exception as e:
                print(f"❌ 验证删除请求失败: {e}")

    print("\n" + "=" * 50)
    print("🎉 知识管理系统测试完成!")

if __name__ == "__main__":
    asyncio.run(test_knowledge_system())