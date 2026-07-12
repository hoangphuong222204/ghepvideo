"""Concrete model-specific repositories extending the generic BaseRepository."""

import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.database.base_repository import BaseRepository
from src.database.models import Campaign, MarketingAsset, AuditLog
from src.database.exceptions import ModelNotFoundError, DatabaseError

logger = logging.getLogger("AIMSPro.Database.Repository")


class CampaignRepository(BaseRepository[Campaign]):
    """Concrete repository managing Campaign records."""

    def __init__(self, session: Session) -> None:
        """Initializes with Campaign model."""
        super().__init__(Campaign, session)

    def get_active_campaigns(self) -> List[Campaign]:
        """Retrieves all active campaigns.

        Returns:
            A list of active Campaign model instances.
        """
        return self.get_all(filters={"is_active": True}, order_by=Campaign.created_at.desc())

    def get_campaign_with_assets(self, campaign_id: int) -> Campaign:
        """Retrieves a single campaign with its assets eagerly loaded in a single query.

        Args:
            campaign_id: The primary key of the campaign.

        Returns:
            The Campaign model instance with assets populated.

        Raises:
            ModelNotFoundError: If no campaign matches.
        """
        stmt = (
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(joinedload(Campaign.assets))
        )
        result = self.session.scalars(stmt).unique().first()
        if result is None:
            raise ModelNotFoundError(f"Campaign with id {campaign_id} not found.")
        return result


class MarketingAssetRepository(BaseRepository[MarketingAsset]):
    """Concrete repository managing MarketingAsset records."""

    def __init__(self, session: Session) -> None:
        """Initializes with MarketingAsset model."""
        super().__init__(MarketingAsset, session)

    def get_assets_by_campaign(self, campaign_id: int) -> List[MarketingAsset]:
        """Retrieves all marketing assets associated with a specific campaign.

        Args:
            campaign_id: The campaign foreign key ID.

        Returns:
            A list of matching MarketingAsset instances.
        """
        return self.get_all(filters={"campaign_id": campaign_id}, order_by=MarketingAsset.created_at.desc())

    def get_assets_by_type(self, asset_type: str) -> List[MarketingAsset]:
        """Retrieves all marketing assets of a certain type (e.g. 'video').

        Args:
            asset_type: The asset category string.

        Returns:
            A list of matching MarketingAsset instances.
        """
        return self.get_all(filters={"asset_type": asset_type.lower()}, order_by=MarketingAsset.created_at.desc())

    def get_exported_assets(self) -> List[MarketingAsset]:
        """Retrieves all assets that have been marked as exported.

        Returns:
            A list of exported MarketingAsset instances.
        """
        return self.get_all(filters={"is_exported": True}, order_by=MarketingAsset.created_at.desc())


class AuditLogRepository(BaseRepository[AuditLog]):
    """Concrete repository managing AuditLog records."""

    def __init__(self, session: Session) -> None:
        """Initializes with AuditLog model."""
        super().__init__(AuditLog, session)

    def get_logs_by_event(self, event_type: str) -> List[AuditLog]:
        """Retrieves all audit logs matching a specific event type.

        Args:
            event_type: The event category string.

        Returns:
            A list of AuditLog instances.
        """
        return self.get_all(filters={"event_type": event_type}, order_by=AuditLog.timestamp.desc())

    def log_event(self, event_type: str, description: str, user_ref: Optional[str] = None) -> AuditLog:
        """Creates and immediately persists an audit log record.

        Args:
            event_type: The event category string.
            description: Concise summary details.
            user_ref: Optional user or subsystem reference.

        Returns:
            The created AuditLog instance.
        """
        data = {
            "event_type": event_type,
            "description": description,
            "user_ref": user_ref,
        }
        return self.create(data)
