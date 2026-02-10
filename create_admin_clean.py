#!/usr/bin/env python3
"""清理并创建全新的管理员账户"""

import sqlite3
import sys
import requests

def clean_and_create_admin():
    """清理旧账户并创建新管理员"""
    
    # 1. 删除所有旧的管理员账户
    print("🧹 清理旧的管理员账户...")
    conn = sqlite3.connect('backend/knowledge_platform.db')
    cursor = conn.cursor()
    
    # 删除 admin 相关的账户
    cursor.execute("DELETE FROM users WHERE email IN ('admin@example.com', 'admin@admin.com') OR username = 'admin'")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ 已删除 {deleted} 个旧账户")
    print()
    
    # 2. 通过 API 注册新的管理员账户
    print("📝 注册新的管理员账户...")
    
    admin_data = {
        "email": "admin@admin.com",
        "username": "admin",
        "password": "admin12345",
        "full_name": "System Administrator"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            user_data = response.json()
            user_id = user_data['id']
            print(f"✅ 管理员账户注册成功！用户ID: {user_id}")
            print()
            
            # 3. 更新为超级用户
            print("🔧 设置为超级用户...")
            conn = sqlite3.connect('backend/knowledge_platform.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET is_superuser = 1, is_verified = 1 
                WHERE id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            print("✅ 已设置为超级用户")
            print()
            print("=" * 60)
            print("🎉 管理员账户创建成功！")
            print("=" * 60)
            print()
            print("📧 邮箱：admin@admin.com")
            print("👤 用户名：admin")
            print("🔑 密码：admin12345")
            print("🔐 权限：超级管理员")
            print()
            print("🌐 登录地址：http://localhost:3000")
            print()
            
        else:
            print(f"❌ 注册失败：{response.status_code}")
            print(f"错误信息：{response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 创建管理员失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    clean_and_create_admin()
