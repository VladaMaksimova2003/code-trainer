import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base


class UserRole(Base):
    __tablename__ = "user_role"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "role", name="uq_user_role_user_id_role"),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(sa.String(64), nullable=False)

    user = relationship("User", back_populates="role_assignments")
