#!/usr/bin/env python3
"""
Verification script for attachment implementation.

This script checks if all required components are properly implemented.
"""

import sys
import os
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
backend_dir = project_root / "backend"

# Add backend directory to Python path
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ["TESTING"] = "true"

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} MISSING: {filepath}")
        return False

def check_import(module_path: str, description: str) -> bool:
    """Check if a module can be imported."""
    try:
        parts = module_path.split('.')
        module = __import__(module_path)
        for part in parts[1:]:
            module = getattr(module, part)
        print(f"✓ {description}: {module_path}")
        return True
    except Exception as e:
        print(f"✗ {description} FAILED: {module_path} - {e}")
        return False

def main():
    """Run verification checks."""
    print("=" * 60)
    print("Attachment Implementation Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check model
    print("1. Checking Model...")
    checks.append(check_file_exists(
        "app/models/attachment.py",
        "Attachment Model"
    ))
    checks.append(check_import(
        "app.models.attachment",
        "Import Attachment Model"
    ))
    print()
    
    # Check schemas
    print("2. Checking Schemas...")
    checks.append(check_file_exists(
        "app/schemas/attachment.py",
        "Attachment Schemas"
    ))
    checks.append(check_import(
        "app.schemas.attachment",
        "Import Attachment Schemas"
    ))
    print()
    
    # Check service
    print("3. Checking Service...")
    checks.append(check_file_exists(
        "app/services/attachment.py",
        "Attachment Service"
    ))
    checks.append(check_import(
        "app.services.attachment",
        "Import Attachment Service"
    ))
    print()
    
    # Check API endpoints
    print("4. Checking API Endpoints...")
    checks.append(check_file_exists(
        "app/api/v1/endpoints/attachments.py",
        "Attachment Endpoints"
    ))
    checks.append(check_import(
        "app.api.v1.endpoints.attachments",
        "Import Attachment Endpoints"
    ))
    print()
    
    # Check tests
    print("5. Checking Tests...")
    checks.append(check_file_exists(
        "tests/test_attachment_api.py",
        "Attachment API Tests"
    ))
    print()
    
    # Check configuration
    print("6. Checking Configuration...")
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        # Check upload settings
        if hasattr(settings, 'UPLOAD_DIR'):
            print(f"✓ UPLOAD_DIR configured: {settings.UPLOAD_DIR}")
            checks.append(True)
        else:
            print("✗ UPLOAD_DIR not configured")
            checks.append(False)
        
        if hasattr(settings, 'MAX_FILE_SIZE'):
            print(f"✓ MAX_FILE_SIZE configured: {settings.MAX_FILE_SIZE} bytes")
            checks.append(True)
        else:
            print("✗ MAX_FILE_SIZE not configured")
            checks.append(False)
        
        if hasattr(settings, 'ALLOWED_FILE_TYPES'):
            print(f"✓ ALLOWED_FILE_TYPES configured: {len(settings.ALLOWED_FILE_TYPES)} types")
            checks.append(True)
        else:
            print("✗ ALLOWED_FILE_TYPES not configured")
            checks.append(False)
    except Exception as e:
        print(f"✗ Configuration check failed: {e}")
        checks.extend([False, False, False])
    print()
    
    # Check dependencies
    print("7. Checking Dependencies...")
    try:
        import PIL
        print(f"✓ Pillow installed: {PIL.__version__}")
        checks.append(True)
    except ImportError:
        print("✗ Pillow not installed")
        checks.append(False)
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! Attachment implementation is complete.")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
