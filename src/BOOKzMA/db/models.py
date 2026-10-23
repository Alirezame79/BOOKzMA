from datetime import date, datetime, time

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Index,
    CheckConstraint,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from BOOKzMA.constants import DEFAULT_TIMEZONE
from BOOKzMA.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    display_name: Mapped[str | None] = mapped_column(String(128))
    username: Mapped[str | None] = mapped_column(String(64))
    broadcast_unavailable: Mapped[bool] = mapped_column(default=False, server_default="false")
    timezone: Mapped[str] = mapped_column(
        String(64), default=DEFAULT_TIMEZONE, server_default=DEFAULT_TIMEZONE
    )
    leaderboard_opt_out: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReadingLog(Base):
    __tablename__ = "reading_logs"
    __table_args__ = (Index("ix_reading_logs_day", "day"),)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StreakFreeze(Base):
    __tablename__ = "streak_freezes"
    __table_args__ = (
        CheckConstraint("kind IN ('earned', 'used')", name="ck_streak_freeze_kind"),
        UniqueConstraint("user_id", "kind", "day", name="uq_streak_freeze_user_kind_day"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(8))
    day: Mapped[date] = mapped_column(Date)


class ActivityDay(Base):
    __tablename__ = "activity_days"
    __table_args__ = (Index("ix_activity_days_day", "day"),)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(Date, primary_key=True)


class BroadcastCampaign(Base):
    __tablename__ = "broadcast_campaigns"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'sending', 'completed', 'cancelled')",
            name="ck_broadcast_campaign_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column(String(4096))
    status: Mapped[str] = mapped_column(String(16), default="pending", server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class BroadcastDelivery(Base):
    __tablename__ = "broadcast_deliveries"
    __table_args__ = (
        UniqueConstraint("campaign_id", "user_id", name="uq_broadcast_delivery_campaign_user"),
        Index("ix_broadcast_delivery_campaign_status", "campaign_id", "status"),
        CheckConstraint(
            "status IN ('pending', 'sending', 'sent', 'failed', 'cancelled')",
            name="ck_broadcast_delivery_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("broadcast_campaigns.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(16), default="pending", server_default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_error: Mapped[str | None] = mapped_column(String(128))
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (UniqueConstraint("user_id", "remind_at", name="uq_reminder_user_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    remind_at: Mapped[time] = mapped_column(Time)
    last_sent_on: Mapped[date | None] = mapped_column(Date)
    attempt_date: Mapped[date | None] = mapped_column(Date)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    retry_after_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
