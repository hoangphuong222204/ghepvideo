"""Comprehensive unit and integration test suite for the AIMS Pro Database Layer."""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.database import (
    DatabaseManager,
    CampaignCreate,
    CampaignSchema,
    MarketingAssetCreate,
    MarketingAssetSchema,
    AuditLogSchema,
    DatabaseConnectionError,
    ModelNotFoundError,
)
from src.database.models import Campaign, MarketingAsset, AuditLog
from src.database.query_builder import DynamicQueryBuilder


class TestDatabaseLayer(unittest.TestCase):
    """Integrative tests verifying the complete feature set of Module 03: Database Layer."""

    def setUp(self) -> None:
        """Sets up a clean in-memory SQLite database connection for each test."""
        # Using a fresh in-memory database per test to keep them completely isolated and fast
        self.connection_url = "sqlite:///:memory:"
        
        # Reset the Singleton instance for testing purposes
        DatabaseManager._instance = None
        
        self.db = DatabaseManager(connection_url=self.connection_url)
        self.db.initialize_schema()

    def tearDown(self) -> None:
        """Cleans up the database connections after each test."""
        if self.db._engine:
            self.db._engine.dispose()
        DatabaseManager._instance = None

    def test_singleton_behavior(self) -> None:
        """Verifies that DatabaseManager enforces a strict thread-safe Singleton design."""
        another_db = DatabaseManager()
        self.assertIs(self.db, another_db)

    def test_health_check_and_reconnect(self) -> None:
        """Verifies connection pool health checks and reconnection mechanics."""
        self.assertTrue(self.db.health_check())
        
        # Reconnect should rebuild connections cleanly without crashing
        self.db.reconnect()
        self.assertTrue(self.db.health_check())

    def test_unit_of_work_and_cascade_delete(self) -> None:
        """Verifies the Unit of Work pattern, basic CRUD operations, and cascade deletions."""
        # 1. Create Campaign
        with self.db.unit_of_work() as uow:
            campaign = uow.campaigns.create({
                "title": "AIMS Test Campaign",
                "description": "Integration Test Suite",
                "target_audience": "Developers",
                "budget": 500.0,
                "is_active": True
            })
            campaign_id = campaign.id
            self.assertIsNotNone(campaign_id)
            self.assertEqual(campaign.title, "AIMS Test Campaign")

            # Create MarketingAsset tied to the Campaign
            asset = uow.assets.create({
                "campaign_id": campaign_id,
                "title": "Logo Mockup",
                "asset_type": "image",
                "file_path": "exports/logo.png",
                "gemini_prompt": "Vector style marketing logo"
            })
            asset_id = asset.id
            self.assertIsNotNone(asset_id)

        # 2. Retrieve and Verify eager loading
        with self.db.unit_of_work() as uow:
            retrieved_campaign = uow.campaigns.get_campaign_with_assets(campaign_id)
            self.assertEqual(retrieved_campaign.title, "AIMS Test Campaign")
            self.assertEqual(len(retrieved_campaign.assets), 1)
            self.assertEqual(retrieved_campaign.assets[0].title, "Logo Mockup")

        # 3. List and Filter
        with self.db.unit_of_work() as uow:
            active_campaigns = uow.campaigns.get_active_campaigns()
            self.assertTrue(any(c.id == campaign_id for c in active_campaigns))

            assets_by_type = uow.assets.get_assets_by_type("image")
            self.assertTrue(any(a.id == asset_id for a in assets_by_type))

        # 4. Update
        with self.db.unit_of_work() as uow:
            updated = uow.campaigns.update(campaign_id, {"budget": 1200.0, "title": "AIMS Updated"})
            self.assertEqual(updated.budget, 1200.0)
            self.assertEqual(updated.title, "AIMS Updated")

        # 5. Delete and verify cascading deletes
        with self.db.unit_of_work() as uow:
            uow.campaigns.delete(campaign_id)
            
            # Campaign should be gone
            with self.assertRaises(ModelNotFoundError):
                uow.campaigns.get_by_id(campaign_id)
                
            # Dependent assets should be automatically cascade-deleted
            assets = uow.assets.get_assets_by_campaign(campaign_id)
            self.assertEqual(len(assets), 0)

    def test_audit_logging_repository(self) -> None:
        """Verifies the Audit Logging repository capabilities."""
        with self.db.unit_of_work() as uow:
            log = uow.logs.log_event(
                event_type="TEST_RUN",
                description="Database test suite executed",
                user_ref="system_test"
            )
            log_id = log.id
            self.assertIsNotNone(log_id)

        with self.db.unit_of_work() as uow:
            retrieved_logs = uow.logs.get_logs_by_event("TEST_RUN")
            self.assertEqual(len(retrieved_logs), 1)
            self.assertEqual(retrieved_logs[0].user_ref, "system_test")
            self.assertEqual(retrieved_logs[0].description, "Database test suite executed")

    def test_dynamic_query_builder(self) -> None:
        """Verifies that the DynamicQueryBuilder correctly constructs fluent queries."""
        # Populate some campaigns for builder testing
        with self.db.unit_of_work() as uow:
            uow.campaigns.create({"title": "SaaS Launch", "budget": 1000.0, "is_active": True})
            uow.campaigns.create({"title": "E-Commerce Discount", "budget": 500.0, "is_active": False})
            uow.campaigns.create({"title": "SaaS Winter Sale", "budget": 2000.0, "is_active": True})

        # Test fluent queries
        with self.db.session_scope() as session:
            # Query active SaaS campaigns sorted by budget descending
            builder = (
                DynamicQueryBuilder(Campaign)
                .filter_equal("is_active", True)
                .filter_like("title", "SaaS")
                .order_by("budget", descending=True)
            )
            
            stmt = builder.build()
            results = list(session.scalars(stmt).all())
            
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].title, "SaaS Winter Sale")  # 2000.0 > 1000.0
            self.assertEqual(results[1].title, "SaaS Launch")

    def test_backup_and_restore_sqlite(self) -> None:
        """Verifies hot backups and restores on file-based SQLite database."""
        with TemporaryDirectory() as temp_dir:
            # Create a file-based SQLite DB inside the temp directory
            db_file_path = Path(temp_dir) / "test_active.db"
            backup_folder = Path(temp_dir) / "backups"
            
            # Instantiate a separate DatabaseManager bound to the file-based SQLite database
            DatabaseManager._instance = None
            file_db = DatabaseManager(connection_url=f"sqlite:///{db_file_path.as_posix()}")
            file_db.initialize_schema()

            # 1. Populate some test data
            with file_db.unit_of_work() as uow:
                uow.campaigns.create({"title": "Backup Target Campaign"})

            # 2. Trigger online hot backup
            backup_path_str = file_db.backup_database(custom_dest_folder=str(backup_folder))
            self.assertTrue(os.path.exists(backup_path_str))
            
            # 3. Create a change that we intend to roll back with the restore
            with file_db.unit_of_work() as uow:
                uow.campaigns.create({"title": "Temporary Post-Backup Campaign"})
                count = uow.campaigns.count()
                self.assertEqual(count, 2)

            # 4. Trigger restore from backup
            file_db.restore_database(backup_path_str)
            
            # 5. Verify the state returned to only the pre-backup campaign
            with file_db.unit_of_work() as uow:
                count_after_restore = uow.campaigns.count()
                self.assertEqual(count_after_restore, 1)
                
                campaign = uow.campaigns.get_all()[0]
                self.assertEqual(campaign.title, "Backup Target Campaign")

            file_db._engine.dispose()


if __name__ == "__main__":
    unittest.main()
