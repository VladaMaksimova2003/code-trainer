from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base


class Submission(Base):
    __tablename__ = "submission"

    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    task_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    code: Mapped[str] = mapped_column(sa.Text, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False, default="queued")
    success: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    linter_errors: Mapped[list["SubmissionLintError"]] = relationship(
        "SubmissionLintError", back_populates="submission", cascade="all, delete-orphan"
    )
    pattern_errors: Mapped[list["SubmissionPatternError"]] = relationship(
        "SubmissionPatternError",
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    test_results: Mapped[list["SubmissionTestResult"]] = relationship(
        "SubmissionTestResult",
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    teacher_comments: Mapped[list["SubmissionComment"]] = relationship(
        "SubmissionComment",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionComment.created_at",
    )


class SubmissionLintError(Base):
    __tablename__ = "submission_lint_error"

    submission_id: Mapped[int] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="CASCADE"), nullable=False, index=True
    )
    error_type: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    submission: Mapped["Submission"] = relationship(
        "Submission", back_populates="linter_errors"
    )


class SubmissionPatternError(Base):
    __tablename__ = "submission_pattern_error"

    submission_id: Mapped[int] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="CASCADE"), nullable=False, index=True
    )
    error_type: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    submission: Mapped["Submission"] = relationship(
        "Submission", back_populates="pattern_errors"
    )


class SubmissionTestResult(Base):
    __tablename__ = "submission_test_result"

    submission_id: Mapped[int] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    inputs: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)
    expected: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)
    actual: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)
    message: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)

    submission: Mapped["Submission"] = relationship(
        "Submission", back_populates="test_results"
    )
