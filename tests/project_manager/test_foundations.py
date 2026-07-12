"""Unit tests for the foundations of Module 11: Project Manager.

This suite validates model initialization, post-init constraints, serialization behavior,
enum stability, exception hierarchy, and package-level public exports.
"""

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

import src.project_manager as pm


class TestProjectFoundations(unittest.TestCase):
    """Foundational test suite for Module 11 exceptions, models, and protocols."""

    def test_public_imports(self) -> None:
        """Verify all major foundations, exceptions, models, and protocols are exported."""
        # Exceptions
        self.assertTrue(hasattr(pm, "ProjectManagerError"))
        self.assertTrue(hasattr(pm, "ProjectNotFoundError"))
        self.assertTrue(hasattr(pm, "AssetPathEscapeError"))
        self.assertTrue(hasattr(pm, "HistoryError"))

        # Models
        self.assertTrue(hasattr(pm, "ProjectStatus"))
        self.assertTrue(hasattr(pm, "ProjectMetadata"))
        self.assertTrue(hasattr(pm, "ProjectSettings"))
        self.assertTrue(hasattr(pm, "ProjectDocument"))

        # Protocols
        self.assertTrue(hasattr(pm, "ProjectManagerProtocol"))
        self.assertTrue(hasattr(pm, "WorkspaceManagerProtocol"))

    def test_exception_hierarchy(self) -> None:
        """Verify the custom exception class inheritance structure matches design spec."""
        self.assertTrue(issubclass(pm.ProjectManagerError, Exception))
        self.assertTrue(issubclass(pm.ProjectConfigError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.InvalidProjectRequestError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.InvalidProjectNameError, pm.InvalidProjectRequestError))
        self.assertTrue(issubclass(pm.InvalidProjectPathError, pm.InvalidProjectRequestError))

        self.assertTrue(issubclass(pm.ProjectNotFoundError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.ProjectAlreadyExistsError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.ProjectOpenError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.ProjectSaveError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.ProjectCloseError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.ProjectDeleteError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.WorkspaceCleanupError, pm.ProjectDeleteError))

        self.assertTrue(issubclass(pm.ProjectValidationError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.ProjectCorruptionError, pm.ProjectValidationError))
        self.assertTrue(issubclass(pm.UnsupportedProjectVersionError, pm.ProjectValidationError))
        self.assertTrue(issubclass(pm.ProjectMigrationError, pm.ProjectManagerError))

        self.assertTrue(issubclass(pm.SerializationError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.DeserializationError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.RepositoryError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.AtomicWriteError, pm.RepositoryError))

        self.assertTrue(issubclass(pm.AssetError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.AssetNotFoundError, pm.AssetError))
        self.assertTrue(issubclass(pm.AssetAlreadyRegisteredError, pm.AssetError))
        self.assertTrue(issubclass(pm.InvalidAssetTypeError, pm.AssetError))
        self.assertTrue(issubclass(pm.AssetImportError, pm.AssetError))
        self.assertTrue(issubclass(pm.AssetCopyError, pm.AssetError))
        self.assertTrue(issubclass(pm.AssetMoveError, pm.AssetError))
        self.assertTrue(issubclass(pm.AssetDeleteError, pm.AssetError))
        self.assertTrue(issubclass(pm.AssetPathEscapeError, pm.AssetError))

        self.assertTrue(issubclass(pm.HistoryError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.UndoUnavailableError, pm.HistoryError))
        self.assertTrue(issubclass(pm.RedoUnavailableError, pm.HistoryError))
        self.assertTrue(issubclass(pm.SnapshotCreationError, pm.HistoryError))
        self.assertTrue(issubclass(pm.SnapshotRestoreError, pm.HistoryError))

        self.assertTrue(issubclass(pm.AutosaveError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.AutosaveUnavailableError, pm.AutosaveError))
        self.assertTrue(issubclass(pm.RecoveryError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.BackupError, pm.ProjectManagerError))

        self.assertTrue(issubclass(pm.ProjectLockError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.ProjectAlreadyLockedError, pm.ProjectLockError))
        self.assertTrue(issubclass(pm.StaleLockError, pm.ProjectLockError))
        self.assertTrue(issubclass(pm.ConcurrentModificationError, pm.ProjectManagerError))
        self.assertTrue(issubclass(pm.RecentProjectsError, pm.ProjectManagerError))

    def test_enum_stability(self) -> None:
        """Ensure all domain enums are stable and map to expected wire strings/values."""
        self.assertEqual(pm.ProjectStatus.NO_PROJECT_OPEN.value, "no_project_open")
        self.assertEqual(pm.ProjectStatus.OPEN.value, "open")
        self.assertEqual(pm.ProjectStatus.ERROR.value, "error")

        self.assertEqual(pm.ProjectOperationStatus.SUCCESS.value, "success")
        self.assertEqual(pm.ProjectOperationStatus.FAILED.value, "failed")

        self.assertEqual(pm.ProjectAssetType.VIDEO.value, "video")
        self.assertEqual(pm.ProjectAssetType.AUDIO.value, "audio")
        self.assertEqual(pm.ProjectAssetType.SUBTITLE.value, "subtitle")

        self.assertEqual(pm.AssetStorageMode.INTERNAL.value, "internal")
        self.assertEqual(pm.AssetStorageMode.EXTERNAL.value, "external")

        self.assertEqual(pm.AssetSourceType.IMPORTED.value, "imported")
        self.assertEqual(pm.AssetSourceType.GENERATED.value, "generated")

        self.assertEqual(pm.ProjectChangeType.METADATA.value, "metadata")
        self.assertEqual(pm.ProjectChangeType.SETTINGS.value, "settings")

        self.assertEqual(pm.HistoryActionType.COMMIT.value, "commit")
        self.assertEqual(pm.HistoryActionType.UNDO.value, "undo")

        self.assertEqual(pm.SnapshotType.AUTO.value, "auto")
        self.assertEqual(pm.SnapshotType.MANUAL.value, "manual")

        self.assertEqual(pm.LockStatus.FREE.value, "free")
        self.assertEqual(pm.LockStatus.LOCKED.value, "locked")

        self.assertEqual(pm.RecoveryStatus.AVAILABLE.value, "available")
        self.assertEqual(pm.RecoveryStatus.RECOVERED.value, "recovered")

        self.assertEqual(pm.ProjectSchemaVersion.V1.value, "1.0.0")

    def test_project_metadata_validation(self) -> None:
        """Verify validation constraints inside ProjectMetadata."""
        now = datetime.now(timezone.utc)
        meta = pm.ProjectMetadata(
            project_id="proj-123",
            name="My Project",
            description="A test project",
            created_at=now,
            modified_at=now,
            application_version="1.0.0",
        )
        self.assertEqual(meta.project_id, "proj-123")
        self.assertEqual(meta.name, "My Project")

        # Invalid empty project_id
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectMetadata(
                project_id="",
                name="My Project",
                description="",
                created_at=now,
                modified_at=now,
                application_version="1.0.0",
            )

        # Invalid empty name
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectMetadata(
                project_id="proj-123",
                name="   ",
                description="",
                created_at=now,
                modified_at=now,
                application_version="1.0.0",
            )

        # Invalid revision numbers
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectMetadata(
                project_id="proj-123",
                name="My Project",
                description="",
                created_at=now,
                modified_at=now,
                application_version="1.0.0",
                revision_number=0,
            )

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectMetadata(
                project_id="proj-123",
                name="My Project",
                description="",
                created_at=now,
                modified_at=now,
                application_version="1.0.0",
                last_saved_revision=-1,
            )

    def test_platform_settings_validation(self) -> None:
        """Verify constraints in platform settings."""
        settings = pm.ProjectPlatformSettings(
            target_platform="youtube_shorts",
            default_aspect_ratio="9:16",
            default_resolution="1080x1920",
            default_frame_rate=60,
        )
        self.assertEqual(settings.default_frame_rate, 60)

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectPlatformSettings(target_platform="  ")

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectPlatformSettings(default_frame_rate=0)

    def test_project_settings_validation(self) -> None:
        """Verify constraints in general settings."""
        settings = pm.ProjectSettings(
            default_script_duration_seconds=45.0,
            autosave_interval_seconds=60,
            history_retention_limit=100,
            snapshot_retention_limit=5,
        )
        self.assertEqual(settings.default_script_duration_seconds, 45.0)

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectSettings(default_script_duration_seconds=-10.0)

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectSettings(autosave_interval_seconds=0)

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectSettings(history_retention_limit=-1)

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectSettings(snapshot_retention_limit=-5)

    def test_project_references_validation(self) -> None:
        """Verify script, speech, subtitle, and render reference validations."""
        now = datetime.now(timezone.utc)

        # Script Reference
        ref_script = pm.ProjectScriptReference(
            script_id="script-456",
            title="Short Video",
            content_text="Hello world!",
            generated_at=now,
        )
        self.assertEqual(ref_script.script_id, "script-456")
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectScriptReference(script_id="", title="A", content_text="B", generated_at=now)

        # Speech Reference
        ref_speech = pm.ProjectSpeechReference(
            speech_id="speech-789",
            script_id="script-456",
            audio_path="audio/v.wav",
            voice_id="voice-01",
            duration_seconds=5.4,
            generated_at=now,
        )
        self.assertEqual(ref_speech.speech_id, "speech-789")
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectSpeechReference(
                speech_id="", script_id="b", audio_path="c", voice_id="d", duration_seconds=1.0, generated_at=now
            )
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectSpeechReference(
                speech_id="a", script_id="b", audio_path="c", voice_id="d", duration_seconds=-1.0, generated_at=now
            )

        # Subtitle Reference
        ref_sub = pm.ProjectSubtitleReference(
            subtitle_id="sub-111",
            script_id="script-456",
            subtitle_path="subs/s.srt",
            style_preset="tiktok_bold",
            generated_at=now,
        )
        self.assertEqual(ref_sub.subtitle_id, "sub-111")
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectSubtitleReference(subtitle_id=" ", script_id="b", subtitle_path="c", style_preset="d", generated_at=now)

        # Render Reference
        ref_render = pm.ProjectRenderReference(
            render_id="render-999",
            output_path="renders/out.mp4",
            duration_seconds=15.0,
            file_size_bytes=1048576,
            video_codec="h264",
            audio_codec="aac",
            resolution="1080x1920",
            frame_rate=30.0,
            rendered_at=now,
        )
        self.assertEqual(ref_render.render_id, "render-999")
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectRenderReference(
                render_id="",
                output_path="a",
                duration_seconds=1.0,
                file_size_bytes=1,
                video_codec="h264",
                audio_codec="aac",
                resolution="1080",
                frame_rate=30.0,
                rendered_at=now,
            )
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectRenderReference(
                render_id="r",
                output_path="a",
                duration_seconds=-0.5,
                file_size_bytes=1,
                video_codec="h264",
                audio_codec="aac",
                resolution="1080",
                frame_rate=30.0,
                rendered_at=now,
            )
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectRenderReference(
                render_id="r",
                output_path="a",
                duration_seconds=1.0,
                file_size_bytes=-100,
                video_codec="h264",
                audio_codec="aac",
                resolution="1080",
                frame_rate=30.0,
                rendered_at=now,
            )
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectRenderReference(
                render_id="r",
                output_path="a",
                duration_seconds=1.0,
                file_size_bytes=1,
                video_codec="h264",
                audio_codec="aac",
                resolution="1080",
                frame_rate=-1.0,
                rendered_at=now,
            )

    def test_project_asset_validation(self) -> None:
        """Verify ProjectAsset and AssetMetadata post-init constraints."""
        asset_meta = pm.AssetMetadata(mime_type="image/png", duration_seconds=None, width=1920, height=1080)
        now = datetime.now(timezone.utc)
        asset = pm.ProjectAsset(
            asset_id="asset-555",
            asset_type=pm.ProjectAssetType.IMAGE,
            display_name="Logo Icon",
            relative_path="assets/logo.png",
            storage_mode=pm.AssetStorageMode.INTERNAL,
            source_type=pm.AssetSourceType.IMPORTED,
            file_size_bytes=2048,
            created_at=now,
            modified_at=now,
            metadata=asset_meta,
        )
        self.assertEqual(asset.asset_id, "asset-555")
        self.assertEqual(asset.metadata.width, 1920)

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectAsset(
                asset_id="",
                asset_type=pm.ProjectAssetType.IMAGE,
                display_name="a",
                relative_path="b",
                storage_mode=pm.AssetStorageMode.INTERNAL,
                source_type=pm.AssetSourceType.IMPORTED,
                file_size_bytes=100,
            )
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectAsset(
                asset_id="id",
                asset_type=pm.ProjectAssetType.IMAGE,
                display_name=" ",
                relative_path="b",
                storage_mode=pm.AssetStorageMode.INTERNAL,
                source_type=pm.AssetSourceType.IMPORTED,
                file_size_bytes=100,
            )
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectAsset(
                asset_id="id",
                asset_type=pm.ProjectAssetType.IMAGE,
                display_name="a",
                relative_path="",
                storage_mode=pm.AssetStorageMode.INTERNAL,
                source_type=pm.AssetSourceType.IMPORTED,
                file_size_bytes=100,
            )
        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectAsset(
                asset_id="id",
                asset_type=pm.ProjectAssetType.IMAGE,
                display_name="a",
                relative_path="b",
                storage_mode=pm.AssetStorageMode.INTERNAL,
                source_type=pm.AssetSourceType.IMPORTED,
                file_size_bytes=-5,
            )

    def test_project_state_transitions(self) -> None:
        """Verify the immutable project state properties."""
        state = pm.ProjectState(
            status=pm.ProjectStatus.OPEN,
            dirty=True,
            current_revision=15,
            last_saved_revision=12,
            active_project_path=Path("/workspace/project1"),
            active_project_id="proj-123",
            read_only=False,
            lock_status=pm.LockStatus.LOCKED,
            autosave_available=True,
            undo_available=True,
            redo_available=False,
        )
        self.assertEqual(state.status, pm.ProjectStatus.OPEN)
        self.assertTrue(state.dirty)
        self.assertEqual(state.current_revision, 15)
        self.assertEqual(state.lock_status, pm.LockStatus.LOCKED)
        self.assertTrue(state.undo_available)
        self.assertFalse(state.redo_available)

    def test_project_changes_and_history(self) -> None:
        """Verify ProjectChange and HistoryEntry."""
        now = datetime.now(timezone.utc)
        change = pm.ProjectChange(
            change_id="change-1",
            change_type=pm.ProjectChangeType.SETTINGS,
            timestamp=now,
            description="Changed autosave interval",
            inverse_patch={"settings": {"autosave_interval_seconds": 300}},
            forward_patch={"settings": {"autosave_interval_seconds": 60}},
        )
        self.assertEqual(change.change_id, "change-1")
        self.assertEqual(change.change_type, pm.ProjectChangeType.SETTINGS)

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.ProjectChange(
                change_id="",
                change_type=pm.ProjectChangeType.SETTINGS,
                timestamp=now,
                description="desc",
            )

        entry = pm.HistoryEntry(
            revision=5,
            action_type=pm.HistoryActionType.COMMIT,
            timestamp=now,
            description="Committed settings change",
            changes=[change],
        )
        self.assertEqual(entry.revision, 5)
        self.assertEqual(entry.changes[0].change_id, "change-1")

        with self.assertRaises(pm.InvalidProjectRequestError):
            pm.HistoryEntry(
                revision=0,
                action_type=pm.HistoryActionType.COMMIT,
                timestamp=now,
                description="desc",
            )

    def test_validation_reports(self) -> None:
        """Verify validation issue and report integrity."""
        issue1 = pm.ValidationIssue(
            severity="warning",
            code="W_ASSET_MISSING",
            message="Optional music file is missing",
            field_path="assets.music-1",
        )
        self.assertEqual(issue1.severity, "warning")

        with self.assertRaises(pm.ProjectValidationError):
            pm.ValidationIssue(severity="critical", code="E_ERR", message="Wrong severity")

        # Validation report with errors must coerce is_valid to False
        issue_err = pm.ValidationIssue(severity="error", code="E_METADATA_NAME", message="Project name cannot be empty")
        report = pm.ValidationReport(is_valid=True, issues=[issue1, issue_err])

        # Post-init should force is_valid to False because of issue_err
        self.assertFalse(report.is_valid)

    def test_project_operation_results(self) -> None:
        """Verify different project results initialization."""
        now = datetime.now(timezone.utc)

        # General Result
        op_res = pm.ProjectOperationResult(
            operation_id="op-1",
            status=pm.ProjectOperationStatus.SUCCESS,
            project_id="proj-123",
        )
        self.assertEqual(op_res.operation_id, "op-1")

        # Open Result
        open_res = pm.ProjectOpenResult(
            operation_id="op-2",
            status=pm.ProjectOperationStatus.SUCCESS,
            project_id="proj-123",
            project_path=Path("/project1"),
            project_state=pm.ProjectState(pm.ProjectStatus.OPEN, False, 1, 1),
            read_only_status=False,
            validation_report=pm.ValidationReport(is_valid=True),
            recovery_available=False,
            migration_performed=False,
        )
        self.assertEqual(open_res.project_id, "proj-123")

        # Save Result
        save_res = pm.ProjectSaveResult(
            operation_id="op-3",
            status=pm.ProjectOperationStatus.SUCCESS,
            project_id="proj-123",
            project_path=Path("/project1"),
            revision=2,
            saved_timestamp=now,
        )
        self.assertEqual(save_res.revision, 2)

        # Delete Result
        delete_res = pm.ProjectDeleteResult(
            operation_id="op-4",
            status=pm.ProjectOperationStatus.SUCCESS,
            project_id="proj-123",
            deleted_project_path=Path("/project1"),
            deletion_mode="permanent",
        )
        self.assertEqual(delete_res.deletion_mode, "permanent")

    def test_project_document_serialization(self) -> None:
        """Verify ProjectDocument structure and serializability of dictionaries."""
        now = datetime.now(timezone.utc)
        metadata = pm.ProjectMetadata(
            project_id="proj-100",
            name="Serial Project",
            description="",
            created_at=now,
            modified_at=now,
            application_version="1.0.0",
        )
        settings = pm.ProjectSettings()
        doc = pm.ProjectDocument(
            metadata=metadata,
            settings=settings,
        )

        d = doc.to_dict()
        self.assertEqual(d["metadata"]["project_id"], "proj-100")
        self.assertEqual(d["settings"]["default_render_preset"], "medium")

        # Verify that json.dumps works if we custom-serialize datetime or use string representation
        # (This confirms standard dict structures from asdict are clean)
        def json_serial(obj):
            if isinstance(obj, (datetime, Path)):
                return str(obj)
            raise TypeError("Type not serializable")

        json_str = json.dumps(d, default=json_serial)
        self.assertTrue(isinstance(json_str, str))


if __name__ == "__main__":
    unittest.main()
