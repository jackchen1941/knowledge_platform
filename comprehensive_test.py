#!/usr/bin/env python3
"""全面测试所有API功能"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

class APITester:
    def __init__(self):
        self.token = None
        self.test_data = {}
        self.passed = 0
        self.failed = 0
        
    def login(self):
        """登录获取token"""
        print_info("测试登录...")
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": "admin@admin.com", "password": "admin12345"}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                print_success("登录成功")
                self.passed += 1
                return True
            else:
                print_error(f"登录失败: {response.status_code}")
                self.failed += 1
                return False
        except Exception as e:
            print_error(f"登录异常: {e}")
            self.failed += 1
            return False
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_categories(self):
        """测试分类CRUD"""
        print("\n" + "="*60)
        print("测试分类管理")
        print("="*60)
        
        # 创建分类
        print_info("创建分类...")
        try:
            response = requests.post(
                f"{BASE_URL}/categories",
                headers=self.get_headers(),
                json={
                    "name": "测试分类",
                    "description": "这是一个测试分类",
                    "color": "#3498db",
                    "icon": "📁"
                }
            )
            if response.status_code in [200, 201]:
                category = response.json()
                self.test_data['category_id'] = category['id']
                print_success(f"创建分类成功: {category['name']}")
                self.passed += 1
            else:
                print_error(f"创建分类失败: {response.status_code} - {response.text[:200]}")
                self.failed += 1
                return
        except Exception as e:
            print_error(f"创建分类异常: {e}")
            self.failed += 1
            return
        
        # 列表分类
        print_info("获取分类列表...")
        try:
            response = requests.get(
                f"{BASE_URL}/categories",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"获取分类列表成功，共 {len(data.get('categories', []))} 个")
                self.passed += 1
            else:
                print_error(f"获取分类列表失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"获取分类列表异常: {e}")
            self.failed += 1
        
        # 更新分类
        if 'category_id' in self.test_data:
            print_info("更新分类...")
            try:
                response = requests.put(
                    f"{BASE_URL}/categories/{self.test_data['category_id']}",
                    headers=self.get_headers(),
                    json={"name": "测试分类（已更新）"}
                )
                if response.status_code == 200:
                    print_success("更新分类成功")
                    self.passed += 1
                else:
                    print_error(f"更新分类失败: {response.status_code}")
                    self.failed += 1
            except Exception as e:
                print_error(f"更新分类异常: {e}")
                self.failed += 1
    
    def test_tags(self):
        """测试标签CRUD"""
        print("\n" + "="*60)
        print("测试标签管理")
        print("="*60)
        
        # 创建标签
        print_info("创建标签...")
        try:
            response = requests.post(
                f"{BASE_URL}/tags",
                headers=self.get_headers(),
                json={
                    "name": "测试标签",
                    "description": "这是一个测试标签",
                    "color": "#e74c3c"
                }
            )
            if response.status_code in [200, 201]:
                tag = response.json()
                self.test_data['tag_id'] = tag['id']
                print_success(f"创建标签成功: {tag['name']}")
                self.passed += 1
            else:
                print_error(f"创建标签失败: {response.status_code} - {response.text[:200]}")
                self.failed += 1
                return
        except Exception as e:
            print_error(f"创建标签异常: {e}")
            self.failed += 1
            return
        
        # 列表标签
        print_info("获取标签列表...")
        try:
            response = requests.get(
                f"{BASE_URL}/tags",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"获取标签列表成功，共 {len(data.get('tags', []))} 个")
                self.passed += 1
            else:
                print_error(f"获取标签列表失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"获取标签列表异常: {e}")
            self.failed += 1
        
        # 更新标签
        if 'tag_id' in self.test_data:
            print_info("更新标签...")
            try:
                response = requests.put(
                    f"{BASE_URL}/tags/{self.test_data['tag_id']}",
                    headers=self.get_headers(),
                    json={"name": "测试标签（已更新）"}
                )
                if response.status_code == 200:
                    print_success("更新标签成功")
                    self.passed += 1
                else:
                    print_error(f"更新标签失败: {response.status_code}")
                    self.failed += 1
            except Exception as e:
                print_error(f"更新标签异常: {e}")
                self.failed += 1
    
    def test_knowledge(self):
        """测试知识CRUD"""
        print("\n" + "="*60)
        print("测试知识管理")
        print("="*60)
        
        # 创建知识
        print_info("创建知识...")
        try:
            knowledge_data = {
                "title": "测试知识条目",
                "content": "这是一个测试知识内容\n\n包含多行文本和详细信息。",
                "summary": "测试摘要",
                "is_published": True
            }
            
            if 'category_id' in self.test_data:
                knowledge_data['category_id'] = self.test_data['category_id']
            
            if 'tag_id' in self.test_data:
                knowledge_data['tag_ids'] = [self.test_data['tag_id']]
            
            response = requests.post(
                f"{BASE_URL}/knowledge",
                headers=self.get_headers(),
                json=knowledge_data
            )
            
            if response.status_code in [200, 201]:
                knowledge = response.json()
                self.test_data['knowledge_id'] = knowledge['id']
                print_success(f"创建知识成功: {knowledge['title']}")
                self.passed += 1
            else:
                print_error(f"创建知识失败: {response.status_code} - {response.text[:200]}")
                self.failed += 1
                return
        except Exception as e:
            print_error(f"创建知识异常: {e}")
            self.failed += 1
            return
        
        # 列表知识
        print_info("获取知识列表...")
        try:
            response = requests.get(
                f"{BASE_URL}/knowledge",
                headers=self.get_headers(),
                params={"page": 1, "page_size": 10}
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"获取知识列表成功，共 {data.get('total', 0)} 条")
                self.passed += 1
            else:
                print_error(f"获取知识列表失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"获取知识列表异常: {e}")
            self.failed += 1
        
        # 获取单个知识
        if 'knowledge_id' in self.test_data:
            print_info("获取知识详情...")
            try:
                response = requests.get(
                    f"{BASE_URL}/knowledge/{self.test_data['knowledge_id']}",
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    print_success("获取知识详情成功")
                    self.passed += 1
                else:
                    print_error(f"获取知识详情失败: {response.status_code}")
                    self.failed += 1
            except Exception as e:
                print_error(f"获取知识详情异常: {e}")
                self.failed += 1
            
            # 更新知识
            print_info("更新知识...")
            try:
                response = requests.put(
                    f"{BASE_URL}/knowledge/{self.test_data['knowledge_id']}",
                    headers=self.get_headers(),
                    json={"title": "测试知识条目（已更新）"}
                )
                if response.status_code == 200:
                    print_success("更新知识成功")
                    self.passed += 1
                else:
                    print_error(f"更新知识失败: {response.status_code}")
                    self.failed += 1
            except Exception as e:
                print_error(f"更新知识异常: {e}")
                self.failed += 1
    
    def test_search(self):
        """测试搜索功能"""
        print("\n" + "="*60)
        print("测试搜索功能")
        print("="*60)
        
        print_info("搜索知识...")
        try:
            response = requests.get(
                f"{BASE_URL}/search",
                headers=self.get_headers(),
                params={"q": "测试"}
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"搜索成功，找到 {data.get('total', 0)} 条结果")
                self.passed += 1
            else:
                print_error(f"搜索失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"搜索异常: {e}")
            self.failed += 1
    
    def test_analytics(self):
        """测试统计功能"""
        print("\n" + "="*60)
        print("测试统计功能")
        print("="*60)
        
        print_info("获取概览统计...")
        try:
            response = requests.get(
                f"{BASE_URL}/analytics/overview",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"获取统计成功")
                print(f"  - 总条目: {data.get('total_items', 0)}")
                print(f"  - 已发布: {data.get('published_items', 0)}")
                print(f"  - 总字数: {data.get('total_words', 0)}")
                self.passed += 1
            else:
                print_error(f"获取统计失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"获取统计异常: {e}")
            self.failed += 1
    
    def cleanup(self):
        """清理测试数据"""
        print("\n" + "="*60)
        print("清理测试数据")
        print("="*60)
        
        # 删除知识
        if 'knowledge_id' in self.test_data:
            print_info("删除测试知识...")
            try:
                response = requests.delete(
                    f"{BASE_URL}/knowledge/{self.test_data['knowledge_id']}",
                    headers=self.get_headers()
                )
                if response.status_code in [200, 204]:
                    print_success("删除知识成功")
                else:
                    print_warning(f"删除知识失败: {response.status_code}")
            except Exception as e:
                print_warning(f"删除知识异常: {e}")
        
        # 删除标签
        if 'tag_id' in self.test_data:
            print_info("删除测试标签...")
            try:
                response = requests.delete(
                    f"{BASE_URL}/tags/{self.test_data['tag_id']}",
                    headers=self.get_headers()
                )
                if response.status_code in [200, 204]:
                    print_success("删除标签成功")
                else:
                    print_warning(f"删除标签失败: {response.status_code}")
            except Exception as e:
                print_warning(f"删除标签异常: {e}")
        
        # 删除分类
        if 'category_id' in self.test_data:
            print_info("删除测试分类...")
            try:
                response = requests.delete(
                    f"{BASE_URL}/categories/{self.test_data['category_id']}",
                    headers=self.get_headers(),
                    params={"force": True}
                )
                if response.status_code in [200, 204]:
                    print_success("删除分类成功")
                else:
                    print_warning(f"删除分类失败: {response.status_code}")
            except Exception as e:
                print_warning(f"删除分类异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("知识管理平台 - 全面功能测试")
        print("="*60)
        
        # 登录
        if not self.login():
            print_error("登录失败，无法继续测试")
            return
        
        # 运行各项测试
        self.test_categories()
        self.test_tags()
        self.test_knowledge()
        self.test_search()
        self.test_analytics()
        
        # 清理
        self.cleanup()
        
        # 总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"总测试数: {total}")
        print_success(f"通过: {self.passed}")
        if self.failed > 0:
            print_error(f"失败: {self.failed}")
        print(f"成功率: {success_rate:.1f}%")
        
        if self.failed == 0:
            print_success("\n🎉 所有测试通过！")
        else:
            print_error(f"\n⚠️  有 {self.failed} 个测试失败，请检查")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
