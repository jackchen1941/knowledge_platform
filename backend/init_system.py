#!/usr/bin/env python3
"""
Initialize the complete system including database and authentication.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import init_database, create_tables
from app.core.init_auth import initialize_auth_system


async def main():
    """Initialize the complete system."""
    print("🚀 Initializing Knowledge Management Platform...")
    
    try:
        # 1. Initialize database
        print("📊 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully!")
        
        # 2. Create database tables
        print("🏗️  Creating database tables...")
        await create_tables()
        print("✅ Database tables created successfully!")
        
        # 3. Initialize authentication system
        print("🔐 Initializing authentication system...")
        result = await initialize_auth_system()
        print("✅ Authentication system initialized successfully!")
        
        print("\n🎉 System initialization completed!")
        print("\nDefault credentials:")
        print("  👑 Admin: admin@example.com / admin123")
        print("  👤 User:  user@example.com / user123")
        print("\nYou can now start the server with: python3 -m app.main")
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())