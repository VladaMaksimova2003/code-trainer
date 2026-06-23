"""
Create or update the default super-user (admin@test.com).

For a completely empty database, prefer:
  poetry run python scripts/reset_database.py --yes
"""

from ensure_super_user import ensure_super_user

if __name__ == "__main__":
    ensure_super_user()
