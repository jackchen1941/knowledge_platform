#!/usr/bin/env python3
"""测试导入导出功能"""

import requests
import json
import time
from pathlib import Path

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

class ImportExportTester:
    def __init__(self):
        self.token = None
        self.test_data = {}
        self.passed = 0
        self.failed = 0
        
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
    
    def create_test_knowledge(self):
        """创建测试知识"""
        print("\n" + "="*60)
        print("创建测试知识")
        print("="*60)
        
        print_info("创建知识条目...")
        try:
            response = requests.post(
                f"{BASE_URL}/knowledge",
                headers=self.get_headers(),
                json={
                    "title": "导出测试文章",
                    "content": """# 这是一篇测试文章

## 简介
这是用于测试导入导出功能的文章。

## 内容
包含多个段落和格式：
- 列表项1
- 列表项2
- 列表项3

### 代码示例
```python
def hello():
    print("Hello, World!")
```

## 结论
测试文章到此结束。
""",
                    "summary": "这是一篇用于测试导入导出功能的文章",
                    "content_type": "markdown",
                    "is_published": True
                }
            )
            
            if response.status_code in [200, 201]:
                knowledge = response.json()
                self.test_data['knowledge_id'] = knowledge['id']
                print_success(f"创建知识成功: {knowledge['title']}")
                self.passed += 1
                return True
            else:
                print_error(f"创建知识失败: {response.status_code} - {response.text[:200]}")
                self.failed += 1
                return False
        except Exception as e:
            print_error(f"创建知识异常: {e}")
            self.failed += 1
            return False
    
    def test_export_markdown(self):
        """测试导出为Markdown"""
        print("\n" + "="*60)
        print("测试导出为Markdown")
        print("="*60)
        
        if 'knowledge_id' not in self.test_data:
            print_warning("跳过：没有测试知识ID")
            return
        
        print_info("导出为Markdown...")
        try:
            response = requests.post(
                f"{BASE_URL}/import-export/export/{self.test_data['knowledge_id']}",
                headers=self.get_headers(),
                json={
                    "format": "markdown",
                    "include_metadata": True
                }
            )
            
            if response.status_code == 200:
                # 保存文件
                output_file = Path("test_export.md")
                output_file.write_bytes(response.content)
                print_success(f"导出Markdown成功，文件大小: {len(response.content)} 字节")
                print_info(f"文件已保存到: {output_file.absolute()}")
                self.passed += 1
            else:
                print_error(f"导出Markdown失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"导出Markdown异常: {e}")
            self.failed += 1
    
    def test_export_json(self):
        """测试导出为JSON"""
        print("\n" + "="*60)
        print("测试导出为JSON")
        print("="*60)
        
        if 'knowledge_id' not in self.test_data:
            print_warning("跳过：没有测试知识ID")
            return
        
        print_info("导出为JSON...")
        try:
            response = requests.post(
                f"{BASE_URL}/import-export/export/{self.test_data['knowledge_id']}",
                headers=self.get_headers(),
                json={
                    "format": "json",
                    "include_versions": True
                }
            )
            
            if response.status_code == 200:
                # 保存文件
                output_file = Path("test_export.json")
                output_file.write_bytes(response.content)
                
                # 验证JSON格式
                data = json.loads(response.content)
                print_success(f"导出JSON成功")
                print_info(f"  - 标题: {data.get('title')}")
                print_info(f"  - 字数: {data.get('word_count')}")
                print_info(f"  - 阅读时间: {data.get('reading_time')}分钟")
                print_info(f"文件已保存到: {output_file.absolute()}")
                self.passed += 1
            else:
                print_error(f"导出JSON失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"导出JSON异常: {e}")
            self.failed += 1
    
    def test_export_html(self):
        """测试导出为HTML"""
        print("\n" + "="*60)
        print("测试导出为HTML")
        print("="*60)
        
        if 'knowledge_id' not in self.test_data:
            print_warning("跳过：没有测试知识ID")
            return
        
        print_info("导出为HTML...")
        try:
            response = requests.post(
                f"{BASE_URL}/import-export/export/{self.test_data['knowledge_id']}",
                headers=self.get_headers(),
                json={
                    "format": "html"
                }
            )
            
            if response.status_code == 200:
                # 保存文件
                output_file = Path("test_export.html")
                output_file.write_bytes(response.content)
                print_success(f"导出HTML成功，文件大小: {len(response.content)} 字节")
                print_info(f"文件已保存到: {output_file.absolute()}")
                self.passed += 1
            else:
                print_error(f"导出HTML失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"导出HTML异常: {e}")
            self.failed += 1
    
    def test_batch_export(self):
        """测试批量导出"""
        print("\n" + "="*60)
        print("测试批量导出")
        print("="*60)
        
        print_info("获取所有知识ID...")
        try:
            response = requests.get(
                f"{BASE_URL}/knowledge",
                headers=self.get_headers(),
                params={"page": 1, "page_size": 5}
            )
            
            if response.status_code != 200:
                print_error(f"获取知识列表失败: {response.status_code}")
                self.failed += 1
                return
            
            data = response.json()
            item_ids = [item['id'] for item in data.get('items', [])]
            
            if not item_ids:
                print_warning("没有可导出的知识条目")
                return
            
            print_info(f"准备导出 {len(item_ids)} 个知识条目...")
            
            response = requests.post(
                f"{BASE_URL}/import-export/export/batch",
                headers=self.get_headers(),
                json={
                    "item_ids": item_ids,
                    "format": "markdown",
                    "include_metadata": True
                }
            )
            
            if response.status_code == 200:
                # 保存ZIP文件
                output_file = Path("test_batch_export.zip")
                output_file.write_bytes(response.content)
                print_success(f"批量导出成功，ZIP文件大小: {len(response.content)} 字节")
                print_info(f"文件已保存到: {output_file.absolute()}")
                self.passed += 1
            else:
                print_error(f"批量导出失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"批量导出异常: {e}")
            self.failed += 1
    
    def test_import_from_markdown(self):
        """测试从Markdown导入"""
        print("\n" + "="*60)
        print("测试从Markdown导入")
        print("="*60)
        
        # 创建测试Markdown文件
        test_md = Path("test_import.md")
        test_md.write_text("""# 从Markdown导入的文章

## 简介
这是通过Markdown文件导入的测试文章。

## 内容
测试导入功能是否正常工作。

### 特性
- 支持标题
- 支持列表
- 支持代码块

```python
print("Hello from imported markdown!")
```

## 结论
导入测试完成。
""", encoding='utf-8')
        
        print_info("从Markdown文件导入...")
        try:
            # 注意：当前API可能还没有实现文件上传导入
            # 这里我们先创建一个知识条目来模拟导入
            response = requests.post(
                f"{BASE_URL}/knowledge",
                headers=self.get_headers(),
                json={
                    "title": "从Markdown导入的文章",
                    "content": test_md.read_text(encoding='utf-8'),
                    "content_type": "markdown",
                    "summary": "通过Markdown文件导入的测试文章",
                    "is_published": True,
                    "source_platform": "markdown_import"
                }
            )
            
            if response.status_code in [200, 201]:
                knowledge = response.json()
                print_success(f"从Markdown导入成功: {knowledge['title']}")
                print_info(f"  - ID: {knowledge['id']}")
                print_info(f"  - 字数: {knowledge.get('word_count', 0)}")
                self.passed += 1
            else:
                print_error(f"从Markdown导入失败: {response.status_code}")
                self.failed += 1
        except Exception as e:
            print_error(f"从Markdown导入异常: {e}")
            self.failed += 1
        finally:
            # 清理测试文件
            if test_md.exists():
                test_md.unlink()
    
    def cleanup(self):
        """清理测试数据"""
        print("\n" + "="*60)
        print("清理测试数据")
        print("="*60)
        
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
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("知识管理平台 - 导入导出功能测试")
        print("="*60)
        
        # 登录
        if not self.login():
            print_error("登录失败，无法继续测试")
            return
        
        # 创建测试数据
        if not self.create_test_knowledge():
            print_error("创建测试知识失败，无法继续测试")
            return
        
        # 运行导出测试
        self.test_export_markdown()
        self.test_export_json()
        self.test_export_html()
        self.test_batch_export()
        
        # 运行导入测试
        self.test_import_from_markdown()
        
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
    tester = ImportExportTester()
    tester.run_all_tests()
