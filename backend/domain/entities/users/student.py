"""Legacy module — use domain.users.user.User with roles instead."""

from domain.entities.users.user import User

# Backward compatibility alias
Student = User
