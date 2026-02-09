#!/usr/bin/env python3
"""
Test runner script for Knowledge Management Platform

This script provides a convenient way to run different categories of tests
from the project root directory.
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False

def run_backend_tests():
    """Run backend unit tests."""
    os.chdir("backend")
    success = run_command("python -m pytest tests/ -v", "Backend Unit Tests")
    os.chdir("..")
    return success

def run_integration_tests():
    """Run integration tests."""
    success = True
    test_files = [
        "tests/integration/test_all_features.py",
        "tests/integration/test_auth_complete.py",
        "tests/integration/test_knowledge_complete.py",
        "tests/integration/test_simple.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            cmd = f"python {test_file}"
            test_name = Path(test_file).stem.replace('_', ' ').title()
            if not run_command(cmd, f"Integration Test: {test_name}"):
                success = False
        else:
            print(f"⚠️ Test file not found: {test_file}")
    
    return success

def run_security_tests():
    """Run security tests."""
    test_file = "tests/security/test_security_comprehensive.py"
    if os.path.exists(test_file):
        return run_command(f"python {test_file}", "Security Tests")
    else:
        print(f"⚠️ Security test file not found: {test_file}")
        return False

def run_system_tests():
    """Run system tests."""
    success = True
    test_files = [
        "tests/system/test_system.py",
        "tests/system/optimize_and_finalize.py",
        "tests/system/validate_database.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            cmd = f"python {test_file}"
            test_name = Path(test_file).stem.replace('_', ' ').title()
            if not run_command(cmd, f"System Test: {test_name}"):
                success = False
        else:
            print(f"⚠️ Test file not found: {test_file}")
    
    return success

def run_feature_tests():
    """Run feature tests."""
    success = True
    test_files = [
        "tests/features/test_auth.py",
        "tests/features/test_complete_auth.py",
        "tests/features/test_knowledge_simple.py",
        "tests/features/test_new_features.py",
        "tests/features/test_notification_feature.py",
        "tests/features/test_simple_startup.py",
        "tests/features/test_sync_feature.py",
        "tests/features/test_websocket.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            cmd = f"python {test_file}"
            test_name = Path(test_file).stem.replace('_', ' ').title()
            if not run_command(cmd, f"Feature Test: {test_name}"):
                success = False
        else:
            print(f"⚠️ Test file not found: {test_file}")
    
    return success

def run_all_tests():
    """Run all test categories."""
    print("🚀 Running All Tests for Knowledge Management Platform")
    print("=" * 80)
    
    results = {
        "Backend Unit Tests": run_backend_tests(),
        "Integration Tests": run_integration_tests(),
        "Security Tests": run_security_tests(),
        "System Tests": run_system_tests(),
        "Feature Tests": run_feature_tests()
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for category, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{category:<25} {status}")
    
    print("-" * 80)
    print(f"Total: {passed_tests}/{total_tests} test categories passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests for Knowledge Management Platform")
    parser.add_argument("--category", "-c", 
                       choices=["backend", "integration", "security", "system", "feature", "all"],
                       default="all",
                       help="Test category to run (default: all)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Ensure we're in the project root
    if not os.path.exists("backend") or not os.path.exists("tests"):
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected structure: backend/, tests/, frontend/")
        sys.exit(1)
    
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test_knowledge_platform.db"
    
    success = True
    
    if args.category == "backend":
        success = run_backend_tests()
    elif args.category == "integration":
        success = run_integration_tests()
    elif args.category == "security":
        success = run_security_tests()
    elif args.category == "system":
        success = run_system_tests()
    elif args.category == "feature":
        success = run_feature_tests()
    elif args.category == "all":
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()