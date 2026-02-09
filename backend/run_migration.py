#!/usr/bin/env python3
"""
Simple script to run Alembic migrations with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup environment variables for database migration."""
    # Set default environment variables if not already set
    env_vars = {
        'DATABASE_URL': 'sqlite+aiosqlite:///./knowledge_platform.db',
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'ENVIRONMENT': 'development',
        'DEBUG': 'true'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

def run_alembic_command(command_args):
    """Run alembic command with proper setup."""
    setup_environment()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Run alembic command
    cmd = ['alembic'] + command_args
    print(f"Running: {' '.join(cmd)}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Success!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running alembic: {e}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <alembic_command> [args...]")
        print("Examples:")
        print("  python run_migration.py revision --autogenerate -m 'Initial schema'")
        print("  python run_migration.py upgrade head")
        print("  python run_migration.py current")
        sys.exit(1)
    
    # Pass all arguments except script name to alembic
    alembic_args = sys.argv[1:]
    success = run_alembic_command(alembic_args)
    sys.exit(0 if success else 1)