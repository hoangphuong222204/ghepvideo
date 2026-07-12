"""History log tracking rendered prompts, variables, metadata, and conversions."""

import datetime
import json
import os
import uuid
from typing import Any, Dict, List, Optional
from src.prompt_engine.exceptions import StorageError
from src.prompt_engine.models import PromptHistoryRecord
from src.logger.logger_manager import LoggerManager

logger = LoggerManager().get_logger("prompt_engine.prompt_history")

# Conditional database manager importing
try:
    from src.database.database_manager import DatabaseManager
    from src.database.models import AuditLog
    _has_db = True
except ImportError:
    _has_db = False


class PromptHistoryManager:
    """Records diagnostic metadata, variable snapshots, latency, and conversions for generated prompts."""

    def __init__(self, history_filepath: str = "./assets/prompt_history.jsonl") -> None:
        """Initializes history logging with a targeting storage path."""
        self._history_filepath = os.path.abspath(history_filepath)
        os.makedirs(os.path.dirname(self._history_filepath), exist_ok=True)
        logger.info(f"Initialized Prompt History logger at: {self._history_filepath}")

    def add_record(
        self,
        template_name: str,
        version: str,
        provider: str,
        user_prompt: str,
        variables_used: Dict[str, Any],
        system_prompt: Optional[str] = None,
        developer_prompt: Optional[str] = None,
        is_success: bool = True,
        error_message: Optional[str] = None,
        response_latency_ms: Optional[float] = None,
    ) -> PromptHistoryRecord:
        """Saves a new prompt execution entry to the local JSON lines file and SQL audit logs."""
        record_id = str(uuid.uuid4())
        record = PromptHistoryRecord(
            id=record_id,
            template_name=template_name,
            version=version,
            provider=provider,
            user_prompt=user_prompt,
            variables_used=variables_used,
            system_prompt=system_prompt,
            developer_prompt=developer_prompt,
            is_success=is_success,
            error_message=error_message,
            response_latency_ms=response_latency_ms,
        )

        # 1. Write to local JSONL file
        try:
            serialized = {
                "id": record.id,
                "template_name": record.template_name,
                "version": record.version,
                "provider": record.provider,
                "user_prompt": record.user_prompt,
                "variables_used": record.variables_used,
                "timestamp": record.timestamp.isoformat(),
                "system_prompt": record.system_prompt,
                "developer_prompt": record.developer_prompt,
                "is_success": record.is_success,
                "error_message": record.error_message,
                "response_latency_ms": record.response_latency_ms,
                "conversion_recorded": record.conversion_recorded,
            }
            with open(self._history_filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(serialized, ensure_ascii=False) + "\n")
            logger.debug(f"Saved prompt invocation record {record_id} to disk.")
        except Exception as e:
            logger.error(f"Failed to persist historical record locally: {e}")

        # 2. Write to SQLAlchemy Database Audit Logs if available
        if _has_db:
            try:
                db_manager = DatabaseManager()
                # Run database action inside a safe transaction block if session is active
                with db_manager.session_scope() as session:
                    audit = AuditLog(
                        event_type="PROMPT_RENDER",
                        description=(
                            f"Rendered template '{template_name}' (v{version}) for provider '{provider}'. "
                            f"Success: {is_success}. Latency: {response_latency_ms}ms"
                        ),
                        user_ref="prompt_engine_module",
                    )
                    session.add(audit)
                logger.debug("Logged prompt invocation to SQLAlchemy AuditLog.")
            except Exception as db_err:
                logger.warning(f"Failed to log prompt execution to SQLAlchemy AuditLog: {db_err}")

        return record

    def get_history(self, template_name: Optional[str] = None) -> List[PromptHistoryRecord]:
        """Loads prompt invocation histories from the local log store, optionally filtered."""
        records: List[PromptHistoryRecord] = []
        if not os.path.exists(self._history_filepath):
            return records

        try:
            with open(self._history_filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if template_name and data.get("template_name") != template_name:
                            continue

                        records.append(
                            PromptHistoryRecord(
                                id=data["id"],
                                template_name=data["template_name"],
                                version=data["version"],
                                provider=data["provider"],
                                user_prompt=data["user_prompt"],
                                variables_used=data["variables_used"],
                                timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
                                system_prompt=data.get("system_prompt"),
                                developer_prompt=data.get("developer_prompt"),
                                is_success=data.get("is_success", True),
                                error_message=data.get("error_message"),
                                response_latency_ms=data.get("response_latency_ms"),
                                conversion_recorded=data.get("conversion_recorded", False),
                            )
                        )
                    except Exception as parse_err:
                        logger.warning(f"Failed to parse history line: {parse_err}")
        except Exception as e:
            raise StorageError(f"Failed to load prompt history from file: {e}") from e

        # Sort by latest descending
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records

    def mark_conversion(self, record_id: str) -> bool:
        """Searches for a record with the given ID and sets conversion_recorded to True."""
        if not os.path.exists(self._history_filepath):
            return False

        updated = False
        temp_filepath = self._history_filepath + ".tmp"

        try:
            with open(self._history_filepath, "r", encoding="utf-8") as fin, \
                 open(temp_filepath, "w", encoding="utf-8") as fout:
                for line in fin:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("id") == record_id:
                        data["conversion_recorded"] = True
                        updated = True
                    fout.write(json.dumps(data, ensure_ascii=False) + "\n")

            if updated:
                os.replace(temp_filepath, self._history_filepath)
                logger.info(f"Marked conversion for prompt history record: {record_id}")
            else:
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
        except Exception as e:
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except Exception:
                    pass
            raise StorageError(f"Failed to mark conversion for record '{record_id}': {e}") from e

        return updated
