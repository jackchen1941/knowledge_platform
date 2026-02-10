#!/usr/bin/env python3
"""测试URL导入和多设备同步功能"""

import requests
import json

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

class FeatureTester:
    def __init__(self):
        self.token = None
        
    def login(self):
        """登录获取token"""
        print_info("登录...")
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": "admin@admin.com", "password": "admin12345"}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                print_success("登录成功")
                return True
            else:
                print_error(f"登录失败: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"登录异常: {e}")
            return False
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_url_import(self):
        """测试URL导入功能"""
        print("\n" + "="*60)
        print("测试URL导入功能")
        print("="*60)
        
        # 测试URL列表（使用一些公开的技术文章）
        test_urls = [
            "https://github.com/python/cpython/blob/main/README.rst",
            # 可以添加更多测试URL
        ]
        
        for url in test_urls:
            print_info(f"从URL导入: {url}")
            try:
                response = requests.post(
                    f"{BASE_URL}/import-adapters/import-url",
                    headers=self.get_headers(),
                    params={
                        "url": url,
                        "category": "技术文章",
                        "tags": ["测试", "导入"]  # 作为query参数传递
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print_success(f"导入成功: {result['title']}")
                    print_info(f"  - 知识ID: {result['knowledge_id']}")
                    print_info(f"  - 字数: {result['metadata']['word_count']}")
                    print_info(f"  - 阅读时间: {result['metadata']['reading_time']}分钟")
                else:
                    print_error(f"导入失败: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                print_error(f"导入异常: {e}")
    
    def test_device_sync(self):
        """测试多设备同步功能"""
        print("\n" + "="*60)
        print("测试多设备同步功能")
        print("="*60)
        
        # 1. 注册设备
        print_info("注册设备...")
        try:
            response = requests.post(
                f"{BASE_URL}/sync/devices/register",
                headers=self.get_headers(),
                json={
                    "device_name": "测试设备",
                    "device_type": "desktop",
                    "device_id": "test-device-123"
                }
            )
            
            if response.status_code in [200, 201]:
                device = response.json()
                print_success(f"设备注册成功: {device['device_name']}")
                device_id = device['id']
                
                # 2. 查看设备列表
                print_info("查看设备列表...")
                response = requests.get(
                    f"{BASE_URL}/sync/devices",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    devices = response.json()
                    print_success(f"获取设备列表成功，共 {len(devices)} 个设备")
                    for dev in devices:
                        print(f"  - {dev['device_name']} ({dev['device_type']})")
                
                # 3. 测试同步拉取
                print_info("测试同步拉取...")
                response = requests.post(
                    f"{BASE_URL}/sync/pull",
                    headers=self.get_headers(),
                    json={
                        "device_id": device_id
                    }
                )
                
                if response.status_code == 200:
                    sync_result = response.json()
                    print_success("同步拉取成功")
                    print_info(f"  - 知识更新: {len(sync_result['changes']['knowledge'])} 条")
                    print_info(f"  - 分类更新: {len(sync_result['changes']['categories'])} 条")
                    print_info(f"  - 标签更新: {len(sync_result['changes']['tags'])} 条")
                else:
                    print_error(f"同步拉取失败: {response.status_code}")
                
                # 4. 查看同步统计
                print_info("查看同步统计...")
                response = requests.get(
                    f"{BASE_URL}/sync/stats",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    print_success("获取统计成功")
                    print_info(f"  - 总设备数: {stats['total_devices']}")
                    print_info(f"  - 活跃设备: {stats['active_devices']}")
                    print_info(f"  - 未解决冲突: {stats['unresolved_conflicts']}")
                
            else:
                print_error(f"设备注册失败: {response.status_code}")
        except Exception as e:
            print_error(f"设备同步测试异常: {e}")
    
    def test_platform_list(self):
        """测试查看支持的平台"""
        print("\n" + "="*60)
        print("查看支持的导入平台")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/import-adapters/platforms",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                platforms = response.json()
                print_success(f"支持 {len(platforms)} 个导入平台:")
                for platform in platforms:
                    print(f"\n  📱 {platform['name']} ({platform['platform']})")
                    print(f"     {platform['description']}")
                    print(f"     必需配置: {', '.join(platform['required_config'])}")
                    if platform['optional_config']:
                        print(f"     可选配置: {', '.join(platform['optional_config'])}")
            else:
                print_error(f"获取平台列表失败: {response.status_code}")
        except Exception as e:
            print_error(f"获取平台列表异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("多设备同步和URL导入功能测试")
        print("="*60)
        
        # 登录
        if not self.login():
            print_error("登录失败，无法继续测试")
            return
        
        # 运行测试
        self.test_platform_list()
        self.test_device_sync()
        self.test_url_import()
        
        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
        print_info("更多功能请查看: MULTI_DEVICE_AND_IMPORT_GUIDE.md")

if __name__ == "__main__":
    tester = FeatureTester()
    tester.run_all_tests()
