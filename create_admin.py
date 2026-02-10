#!/usr/bin/env python3
"""创建管理员账户的简单脚本"""

import sqlite3
import sys
import uuid

def create_admin():
    """创建管理员账户"""
    
    # 连接数据库
    conn = sqlite3.connect('backend/knowledge_platform.db')
    cursor = conn.cursor()
    
    # 检查是否已存在 admin 用户
    cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@example.com',))
    if cursor.fetchone():
        print("❌ 管理员账户已存在！")
        print("📧 邮箱: admin@example.com")
        print("👤 用户名: admin")
        print("🔑 密码: admin123")
        conn.close()
        return
    
    # 生成 UUID
    user_id = str(uuid.uuid4())
    
    # 使用预先计算的 bcrypt 哈希（admin123）
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNk3KqJqK"
    
    # 插入管理员用户
    cursor.execute("""
        INSERT INTO users (id, email, username, password_hash, is_active, is_superuser, is_verified, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (user_id, 'admin@example.com', 'admin', hashed_password, 1, 1, 1))
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("✅ 管理员账户创建成功！")
    print("")
    print("📧 邮箱: admin@example.com")
    print("👤 用户名: admin")  
    print("🔑 密码: admin123")
    print("")
    print("🌐 现在可以使用这些凭据登录：")
    print("   前端: http://localhost:3000")
    print("   后端API: http://localhost:8000/docs")

if __name__ == '__main__':
    try:
        create_admin()
    except Exception as e:
        print(f"❌ 创建管理员失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
