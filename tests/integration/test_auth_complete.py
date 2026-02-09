#!/usr/bin/env python3
"""
Complete Authentication System Test

Test user registration, login, and token management.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_authentication_system():
    """Test complete authentication flow."""
    
    print("🔐 测试完整认证系统")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: User Registration
        print("\n1️⃣ 测试用户注册")
        register_data = {
            "username": f"test{int(datetime.now().timestamp())}",
            "email": f"test{int(datetime.now().timestamp())}@test.com",
            "password": "test12345",
            "full_name": "Test User"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 用户注册成功: {result['username']} ({result['email']})")
                    user_id = result['id']
                else:
                    error = await response.text()
                    print(f"❌ 用户注册失败: {response.status} - {error}")
                    return
        except Exception as e:
            print(f"❌ 注册请求失败: {e}")
            return
        
        # Test 2: User Login
        print("\n2️⃣ 测试用户登录")
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 用户登录成功: {result['user']['username']}")
                    access_token = result['access_token']
                    print(f"🔑 获得访问令牌: {access_token[:20]}...")
                else:
                    error = await response.text()
                    print(f"❌ 用户登录失败: {response.status} - {error}")
                    return
        except Exception as e:
            print(f"❌ 登录请求失败: {e}")
            return
        
        # Test 3: Access Protected Endpoint
        print("\n3️⃣ 测试受保护端点访问")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.get(
                f"{BASE_URL}/api/v1/me",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 成功访问用户信息: {result}")
                else:
                    error = await response.text()
                    print(f"❌ 访问用户信息失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 用户信息请求失败: {e}")
        
        # Test 4: Test Invalid Login
        print("\n4️⃣ 测试无效登录")
        invalid_login = {
            "email": register_data["email"],
            "password": "WrongPassword"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=invalid_login,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 401:
                    print("✅ 无效密码正确被拒绝")
                else:
                    print(f"❌ 无效密码未被正确处理: {response.status}")
        except Exception as e:
            print(f"❌ 无效登录测试失败: {e}")
        
        # Test 5: Test Duplicate Registration
        print("\n5️⃣ 测试重复注册")
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 400:
                    print("✅ 重复注册正确被拒绝")
                else:
                    print(f"❌ 重复注册未被正确处理: {response.status}")
        except Exception as e:
            print(f"❌ 重复注册测试失败: {e}")
        
        # Test 6: Test Sync Service with Authentication
        print("\n6️⃣ 测试同步服务认证")
        device_data = {
            "device_name": "Test Device",
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
                    print(f"✅ 设备注册成功: {result['device_name']}")
                else:
                    error = await response.text()
                    print(f"❌ 设备注册失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 设备注册请求失败: {e}")
        
        # Test 7: Test Notification with Authentication
        print("\n7️⃣ 测试通知服务认证")
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/notifications/demo",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 演示通知创建成功: {result['title']}")
                else:
                    error = await response.text()
                    print(f"❌ 演示通知创建失败: {response.status} - {error}")
        except Exception as e:
            print(f"❌ 通知创建请求失败: {e}")

    print("\n" + "=" * 50)
    print("🎉 认证系统测试完成!")

if __name__ == "__main__":
    asyncio.run(test_authentication_system())