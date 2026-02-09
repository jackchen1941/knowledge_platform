#!/usr/bin/env python3
print("Hello from Python!")
print("Testing basic functionality...")

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

try:
    from app.models.user import User
    print("✅ User model imported successfully")
except Exception as e:
    print(f"❌ Failed to import User model: {e}")

try:
    from app.services.auth import AuthService
    print("✅ Auth service imported successfully")
except Exception as e:
    print(f"❌ Failed to import Auth service: {e}")

print("Test completed!")