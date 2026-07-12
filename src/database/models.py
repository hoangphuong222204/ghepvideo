"""SQLAlchemy declarative models for the AIMS Pro Database Layer."""

import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import declarative_base, relationship

# Classic style declarative base that is 100% forward-compatible with SQLAlchemy 2.0
Base = declarative_base()


class Campaign(Base):
    """Campaign model managing marketing campaigns."""
    
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    target_audience = Column(String(255), nullable=True)
    budget = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    # Relationship to assets
    assets = relationship(
        "MarketingAsset", back_populates="campaign", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, title='{self.title}', active={self.is_active})>"


class MarketingAsset(Base):
    """MarketingAsset model tracking generated marketing materials."""
    
    __tablename__ = "marketing_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(
        Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False, index=True)  # "video", "audio", "image", "text"
    file_path = Column(String(1024), nullable=True)
    gemini_prompt = Column(Text, nullable=True)
    is_exported = Column(Boolean, default=False)
    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    # Relationship to campaign
    campaign = relationship("Campaign", back_populates="assets")

    def __repr__(self) -> str:
        return f"<MarketingAsset(id={self.id}, type='{self.asset_type}', title='{self.title}')>"


class AuditLog(Base):
    """AuditLog model recording vital database events and transactions."""
    
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    user_ref = Column(String(100), nullable=True)
    timestamp = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, event='{self.event_type}', timestamp={self.timestamp})>"
