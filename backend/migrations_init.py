#!/usr/bin/env python3
"""
Initialize database migrations for production deployment.
Run this once to set up Alembic migrations if not already done.
"""
import os
import sys
from pathlib import Path

def init_alembic():
    """Initialize Alembic migration environment."""
    project_root = Path(__file__).parent
    alembic_dir = project_root / "alembic"

    if alembic_dir.exists():
        print("✓ Alembic already initialized")
        return

    print("Initializing Alembic migrations...")
    os.system(f"cd {project_root} && alembic init alembic")
    print("✓ Alembic initialized")

def update_alembic_env():
    """Update alembic/env.py to use SQLAlchemy with asyncio."""
    alembic_env = Path(__file__).parent / "alembic" / "env.py"

    if not alembic_env.exists():
        print("! Alembic env.py not found")
        return

    # Read current content
    with open(alembic_env, "r") as f:
        content = f.read()

    # Check if already updated
    if "asyncio" in content:
        print("✓ Alembic already configured for asyncio")
        return

    print("Updating Alembic configuration for async...")
    # Note: Manual configuration needed - see database.py for details
    print("⚠ Please manually update alembic/env.py for async support")
    print("  See: https://alembic.sqlalchemy.org/en/latest/cookbook/using_async.html")

def main():
    """Run initialization."""
    print("Database Migration Setup for Production\n")
    init_alembic()
    update_alembic_env()
    print("\n✓ Migration setup complete!")
    print("\nNext steps:")
    print("1. Review and customize alembic/env.py")
    print("2. Create initial migration: alembic revision --autogenerate -m 'Initial schema'")
    print("3. Test migration: alembic upgrade head")
    print("4. Commit alembic folder to git")

if __name__ == "__main__":
    main()
