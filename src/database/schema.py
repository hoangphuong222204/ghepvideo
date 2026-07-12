"""Dataclass-based DTO (Data Transfer Object) schemas for the Database Layer."""

import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CampaignCreate:
    """Schema for creating a new Campaign."""
    title: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    budget: float = 0.0
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Converts Schema to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "target_audience": self.target_audience,
            "budget": self.budget,
            "is_active": self.is_active,
        }


@dataclass
class CampaignSchema:
    """Schema representing a fully-loaded Campaign."""
    id: int
    title: str
    description: Optional[str]
    target_audience: Optional[str]
    budget: float
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    assets: List["MarketingAssetSchema"] = field(default_factory=list)

    @classmethod
    def from_model(cls, model: Any) -> "CampaignSchema":
        """Builds schema from a Campaign database model instance."""
        return cls(
            id=model.id,
            title=model.title,
            description=model.description,
            target_audience=model.target_audience,
            budget=model.budget,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            assets=[
                MarketingAssetSchema.from_model(a) for a in getattr(model, "assets", [])
            ],
        )


@dataclass
class MarketingAssetCreate:
    """Schema for creating a new MarketingAsset."""
    campaign_id: int
    title: str
    asset_type: str
    file_path: Optional[str] = None
    gemini_prompt: Optional[str] = None
    is_exported: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Converts Schema to dictionary."""
        return {
            "campaign_id": self.campaign_id,
            "title": self.title,
            "asset_type": self.asset_type,
            "file_path": self.file_path,
            "gemini_prompt": self.gemini_prompt,
            "is_exported": self.is_exported,
        }


@dataclass
class MarketingAssetSchema:
    """Schema representing a fully-loaded MarketingAsset."""
    id: int
    campaign_id: int
    title: str
    asset_type: str
    file_path: Optional[str]
    gemini_prompt: Optional[str]
    is_exported: bool
    created_at: datetime.datetime

    @classmethod
    def from_model(cls, model: Any) -> "MarketingAssetSchema":
        """Builds schema from a MarketingAsset database model instance."""
        return cls(
            id=model.id,
            campaign_id=model.campaign_id,
            title=model.title,
            asset_type=model.asset_type,
            file_path=model.file_path,
            gemini_prompt=model.gemini_prompt,
            is_exported=model.is_exported,
            created_at=model.created_at,
        )


@dataclass
class AuditLogSchema:
    """Schema representing an AuditLog record."""
    id: int
    event_type: str
    description: str
    user_ref: Optional[str]
    timestamp: datetime.datetime

    @classmethod
    def from_model(cls, model: Any) -> "AuditLogSchema":
        """Builds schema from an AuditLog database model instance."""
        return cls(
            id=model.id,
            event_type=model.event_type,
            description=model.description,
            user_ref=model.user_ref,
            timestamp=model.timestamp,
        )
