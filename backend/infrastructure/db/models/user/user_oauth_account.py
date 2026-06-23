import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class UserOAuthAccount(Base):
    __tablename__ = "user_oauth_account"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    provider_email: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    __table_args__ = (
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_user_oauth_provider_account"),
    )
