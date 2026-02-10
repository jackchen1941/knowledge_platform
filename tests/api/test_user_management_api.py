#!/usr/bin/env python3
"""
用户管理功能测试脚本
Test script for user management features
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

def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def list_users(token):
    """获取用户列表"""
    print("\n" + "="*60)
    print("测试: 获取用户列表")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/users",
        headers=get_headers(token),
        params={"page": 1, "page_size": 10}
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        users = response.json().get("users", [])
        print(f"✅ 获取用户列表成功: {len(users)} 个用户")
        return users
    else:
        print(f"❌ 获取用户列表失败")
        return []

def get_user_stats(token):
    """获取用户统计"""
    print("\n" + "="*60)
    print("测试: 获取用户统计")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/users/stats/overview",
        headers=get_headers(token)
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print(f"✅ 获取统计成功")
        return response.json()
    else:
        print(f"❌ 获取统计失败")
        return None

def create_user(token, email, username, password):
    """创建用户"""
    print("\n" + "="*60)
    print(f"测试: 创建用户 {email}")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/users",
        headers=get_headers(token),
        json={
            "email": email,
            "username": username,
            "password": password,
            "is_active": True,
            "is_superuser": False
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        user_id = response.json()["id"]
        print(f"✅ 创建用户成功: {user_id}")
        return user_id
    else:
        print(f"❌ 创建用户失败")
        return None

def get_user(token, user_id):
    """获取用户详情"""
    print("\n" + "="*60)
    print(f"测试: 获取用户详情 {user_id}")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/users/{user_id}",
        headers=get_headers(token)
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print(f"✅ 获取用户详情成功")
        return response.json()
    else:
        print(f"❌ 获取用户详情失败")
        return None

def update_user(token, user_id, **updates):
    """更新用户"""
    print("\n" + "="*60)
    print(f"测试: 更新用户 {user_id}")
    print(f"更新内容: {updates}")
    print("="*60)
    
    response = requests.put(
        f"{BASE_URL}/users/{user_id}",
        headers=get_headers(token),
        json=updates
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print(f"✅ 更新用户成功")
        return response.json()
    else:
        print(f"❌ 更新用户失败")
        return None

def delete_user(token, user_id):
    """删除用户"""
    print("\n" + "="*60)
    print(f"测试: 删除用户 {user_id}")
    print("="*60)
    
    response = requests.delete(
        f"{BASE_URL}/users/{user_id}",
        headers=get_headers(token)
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 204:
        print(f"✅ 删除用户成功")
        return True
    else:
        print(f"❌ 删除用户失败: {response.text}")
        return False

def main():
    print("="*60)
    print("用户管理功能测试")
    print("="*60)
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 获取用户列表
    users = list_users(token)
    
    # 3. 获取统计
    stats = get_user_stats(token)
    
    # 4. 创建测试用户
    test_email = f"test_user_{int(__import__('time').time())}@example.com"
    test_username = f"testuser_{int(__import__('time').time())}"
    user_id = create_user(token, test_email, test_username, "test123456")
    
    if user_id:
        # 5. 获取用户详情
        user = get_user(token, user_id)
        
        # 6. 更新用户
        updated = update_user(token, user_id, 
                            username=f"{test_username}_updated",
                            is_active=False)
        
        # 7. 再次获取确认更新
        if updated:
            get_user(token, user_id)
        
        # 8. 删除用户
        delete_user(token, user_id)
        
        # 9. 确认删除
        print("\n" + "="*60)
        print("验证: 确认用户已删除")
        print("="*60)
        get_user(token, user_id)
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    print("\n📝 测试总结:")
    print("   - 登录认证")
    print("   - 获取用户列表")
    print("   - 获取用户统计")
    print("   - 创建用户")
    print("   - 获取用户详情")
    print("   - 更新用户")
    print("   - 删除用户")
    print()

if __name__ == "__main__":
    main()
