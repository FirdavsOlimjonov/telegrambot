"""
Import all models here so Alembic autogenerate can discover them.
Order matters for FK resolution — define parents before children.
"""

from app.models.base import Base, TimestampMixin, SoftDeleteMixin
from app.models.direction import Direction
from app.models.speciality import Specialty
from app.models.position_code import PositionCode
from app.models.admin_user import AdminUser

__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "Direction",
    "Specialty",
    "PositionCode",
    "AdminUser",
]
