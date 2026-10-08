from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class RepairModel(Base):
    __tablename__ = "repairs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(32), default="QUEUED", index=True)
    source_file = Column(String(255), nullable=False)
    test_file = Column(String(255), nullable=False)
    target_test = Column(String(255), nullable=False)
    max_attempts = Column(Integer, default=3)
    current_attempt = Column(Integer, default=0)
    trace_id = Column(String(128), default="")
    trace_url = Column(String(512), nullable=True)
    error_message = Column(Text, nullable=True)
    final_diff = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    attempts = relationship("AttemptModel", back_populates="repair", cascade="all, delete-orphan", order_by="AttemptModel.attempt_number")
    events = relationship("EventModel", back_populates="repair", cascade="all, delete-orphan", order_by="EventModel.timestamp")


class AttemptModel(Base):
    __tablename__ = "attempts"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    repair_id = Column(String(64), ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    hypothesis = Column(Text, default="")
    coder_plan = Column(Text, default="")
    diff = Column(Text, default="")
    target_passed = Column(Boolean, default=False)
    regression_passed = Column(Boolean, default=False)
    critic_verdict = Column(String(32), default="REVISE")
    critic_analysis = Column(Text, default="")
    critic_confidence = Column(Float, nullable=True)
    failure_type = Column(String(64), default="")
    latency_ms = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    repair = relationship("RepairModel", back_populates="attempts")
    test_runs = relationship("TestRunModel", back_populates="attempt", cascade="all, delete-orphan")


class TestRunModel(Base):
    __tablename__ = "test_runs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    repair_id = Column(String(64), ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id = Column(String(64), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=True, index=True)
    type = Column(String(32), nullable=False)  # "TARGET" or "REGRESSION"
    passed = Column(Boolean, default=False)
    exit_code = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    stdout = Column(Text, default="")
    stderr = Column(Text, default="")
    failure_type = Column(String(64), default="")

    created_at = Column(DateTime(timezone=True), default=utc_now)

    attempt = relationship("AttemptModel", back_populates="test_runs")


class EventModel(Base):
    __tablename__ = "events"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    repair_id = Column(String(64), ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    payload = Column(Text, default="{}")
    timestamp = Column(DateTime(timezone=True), default=utc_now)

    repair = relationship("RepairModel", back_populates="events")
