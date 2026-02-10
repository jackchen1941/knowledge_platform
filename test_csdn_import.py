#!/usr/bin/env python3
"""测试导入CSDN文章"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
CSDN_URL = "https://blog.csdn.net/m0_66011019/article/details/145370841"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
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

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def main():
    print_header("测试导入CSDN文章")
    
    # 登录
    print_info("正在登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@admin.com", "password": "admin12345"}
        )
        
        if response.status_code != 200:
            print_error(f"登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
        
        token = response.json()["access_token"]
        print_success("登录成功")
    except Exception as e:
        print_error(f"登录异常: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 导入CSDN文章
    print_info(f"正在导入CSDN文章...")
    print(f"URL: {CSDN_URL}")
    
    try:
        params = {
            "url": CSDN_URL,
            "category": "CSDN文章",
            "tags": ["测试", "CSDN", "导入"]
        }
        
        print_info("发送导入请求...")
        response = requests.post(
            f"{BASE_URL}/import-adapters/import-url",
            headers=headers,
            params=params,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print_success("导入成功!")
            print(f"\n{Colors.BOLD}文章信息:{Colors.END}")
            print(f"  📝 标题: {result['title']}")
            print(f"  🆔 知识ID: {result['knowledge_id']}")
            print(f"  📊 字数: {result['metadata']['word_count']}")
            print(f"  ⏱️  阅读时间: {result['metadata']['reading_time']}分钟")
            print(f"  🔗 来源: {result['metadata']['source_url']}")
            print(f"  📅 导入时间: {result['imported_at']}")
            
            # 获取文章详情
            print_info("\n获取文章详情...")
            detail_response = requests.get(
                f"{BASE_URL}/knowledge/{result['knowledge_id']}",
                headers=headers
            )
            
            if detail_response.status_code == 200:
                detail = detail_response.json()
                print_success("获取详情成功")
                print(f"\n{Colors.BOLD}内容预览（前500字符）:{Colors.END}")
                content = detail.get('content', '')
                print(content[:500] + "..." if len(content) > 500 else content)
            else:
                print_error(f"获取详情失败: {detail_response.status_code}")
        else:
            print_error(f"导入失败: {response.status_code}")
            print(f"\n错误详情:")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print(response.text[:500])
    
    except requests.exceptions.Timeout:
        print_error("请求超时（30秒）")
        print("提示: CSDN网站可能响应较慢，请稍后重试")
    except Exception as e:
        print_error(f"导入异常: {e}")
        import traceback
        traceback.print_exc()
    
    print_header("测试完成")
    print(f"\n{Colors.BOLD}💡 提示:{Colors.END}")
    print("  1. 访问前端查看导入的文章: http://localhost:3000")
    print("  2. 在'知识管理'页面可以看到导入的CSDN文章")
    print("  3. 可以继续编辑、添加笔记或导出")

if __name__ == "__main__":
    main()
