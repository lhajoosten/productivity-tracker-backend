"""
All-in-one script to setup a complete development environment.

This script will:
1. Seed RBAC (roles and permissions)
2. Seed test data (organizations, departments, teams, users)

Requires an existing superuser account.
"""

import sys

from productivity_tracker.scripts.seed_rbac import seed_rbac
from productivity_tracker.scripts.seed_test_data import seed_test_data


def setup_dev_environment(superuser_id: str):
    """Setup complete development environment with RBAC and test data."""
    print("\n" + "=" * 80)
    print("DEVELOPMENT ENVIRONMENT SETUP")
    print("=" * 80)
    print("\nThis will setup your development environment with:")
    print("  1. RBAC roles and permissions")
    print("  2. Test organizations, departments, teams, and users")
    print("\n" + "=" * 80 + "\n")

    # Step 1: Seed RBAC
    print("STEP 1: Seeding RBAC...")
    print("-" * 80)
    try:
        seed_rbac()
    except Exception as e:
        print(f"❌ Failed to seed RBAC: {e}")
        return 1

    # Step 2: Seed test data
    print("\n\nSTEP 2: Seeding test data...")
    print("-" * 80)
    result = seed_test_data(superuser_id)
    if result != 0:
        print("❌ Failed to seed test data")
        return 1

    print("\n" + "=" * 80)
    print("🎉 DEVELOPMENT ENVIRONMENT SETUP COMPLETE!")
    print("=" * 80)
    print("\nYou can now start developing with realistic test data.")
    print("\n" + "=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "=" * 80)
        print("SETUP DEVELOPMENT ENVIRONMENT")
        print("=" * 80)
        print("\nUsage: python setup_dev_env.py <superuser_id>")
        print("\nExample:")
        print('  python setup_dev_env.py "ad9c3024-8c65-4ec9-a2d8-0347f8106f0d"')
        print("\nThis will:")
        print("  - Create RBAC roles and permissions")
        print("  - Create test organizations (TechCorp, Innovate Solutions)")
        print("  - Create departments and teams")
        print("  - Create test users with various roles")
        print("\n" + "=" * 80 + "\n")
        sys.exit(1)

    superuser_id = sys.argv[1]
    sys.exit(setup_dev_environment(superuser_id))
