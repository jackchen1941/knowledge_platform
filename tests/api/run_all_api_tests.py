#!/usr/bin/env python3
"""
运行所有API测试
Run all API tests
"""

import subprocess
import sys
from pathlib import Path

# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

def run_test(test_file):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_file.name}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=PROJECT_ROOT,
        capture_output=False
    )
    
    return result.returncode == 0

def main():
    """运行所有API测试"""
    print("="*60)
    print("API测试套件")
    print("="*60)
    
    # 查找所有测试文件
    test_files = sorted(SCRIPT_DIR.glob("test_*_api.py"))
    
    if not test_files:
        print("❌ 未找到测试文件")
        return 1
    
    print(f"\n找到 {len(test_files)} 个测试文件:\n")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    
    # 运行所有测试
    results = {}
    for test_file in test_files:
        success = run_test(test_file)
        results[test_file.name] = success
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
