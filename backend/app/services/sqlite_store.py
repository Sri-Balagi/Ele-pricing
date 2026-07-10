"""
SQLite-backed ConfigurationStore.

Drop-in replacement for InMemoryConfigurationStore.
Implements BaseConfigurationStore exactly, plus adds:
  - search(query) for autocomplete
  - get_dashboard_metrics() for the Dashboard page

All DB access is async (SQLAlchemy 2.0 + aiosqlite).
Because FastAPI endpoints are async, we call these from async context.
The few legacy sync callers (startup validation, etc.) are not affected
because they don't call store methods.
"""

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import String, func, select

from app.core.constants import ConfigurationStatus
from app.db.database import AsyncSessionLocal
from app.db.models import ConfigurationRecord
from app.models.domain import Configuration
from app.services.store import BaseConfigurationStore

logger = logging.getLogger(__name__)

_QUOTED_STATUSES = {ConfigurationStatus.QUOTED, ConfigurationStatus.EXPORTED}
_COMPLETED_STATUSES = {"QUOTED", "EXPORTED"}


def _to_record(
    config: Configuration, existing_id: int | None = None
) -> ConfigurationRecord:
    """Serialize a Configuration domain object into an ORM record."""
    now = datetime.now(UTC).isoformat()
    pricing_total: float | None = None
    if config.pricing_summary:
        try:
            pricing_total = float(config.pricing_summary.total_after_tax)
        except Exception:
            pass
    return ConfigurationRecord(
        id=existing_id,
        configuration_id=config.configuration_id,
        project_name=config.project_name or "",
        status=config.status.value
        if hasattr(config.status, "value")
        else str(config.status),
        selected_category=config.selected_category or "",
        pricing_total=pricing_total,
        data=config.model_dump_json(),
        created_at=config.created_at or now,
        updated_at=now,
    )


def _from_record(record: ConfigurationRecord) -> Configuration:
    """Deserialize an ORM record back into a Configuration domain object."""
    return Configuration.model_validate_json(record.data)


def _run_sync(coro):
    """Run an async coroutine from sync context (used for BaseConfigurationStore compat)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


class SQLiteConfigurationStore(BaseConfigurationStore):
    """
    Persistent, async SQLite store implementing BaseConfigurationStore.

    Async methods (create_async, get_async, etc.) are the primary interface.
    Sync wrappers are provided for backward-compat with any sync callers.
    """

    # ── Async interface (preferred) ───────────────────────────────────────────

    async def create_async(self, config: Configuration) -> Configuration:
        async with AsyncSessionLocal() as session:
            # Check for unique project name
            if config.project_name:
                existing = await session.execute(
                    select(ConfigurationRecord).where(
                        func.lower(ConfigurationRecord.project_name)
                        == config.project_name.strip().lower()
                    )
                )
                if existing.scalar_one_or_none():
                    raise ValueError(
                        f"A project with the name '{config.project_name}' already exists."
                    )

            record = _to_record(config)
            session.add(record)
            await session.commit()
            await session.refresh(record)

            # Reassign configuration_id to be the PK
            new_id = str(record.id)
            config.configuration_id = new_id
            record.configuration_id = new_id
            record.data = config.model_dump_json()

            session.add(record)
            await session.commit()

        logger.debug("SQLiteStore.create: %s", config.configuration_id)
        return config

    async def get_async(self, configuration_id: str) -> Configuration | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ConfigurationRecord).where(
                    ConfigurationRecord.configuration_id == configuration_id
                )
            )
            record = result.scalar_one_or_none()
            return _from_record(record) if record else None

    async def update_async(self, config: Configuration) -> Configuration:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ConfigurationRecord).where(
                    ConfigurationRecord.configuration_id == config.configuration_id
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                raise KeyError(
                    f"Configuration {config.configuration_id} not found for update."
                )

            if (
                config.project_name
                and config.project_name.strip().lower()
                != (record.project_name or "").strip().lower()
            ):
                existing = await session.execute(
                    select(ConfigurationRecord).where(
                        func.lower(ConfigurationRecord.project_name)
                        == config.project_name.strip().lower()
                    )
                )
                if existing.scalar_one_or_none():
                    raise ValueError(
                        f"A project with the name '{config.project_name}' already exists."
                    )

            now = datetime.now(UTC).isoformat()
            record.project_name = config.project_name or ""
            record.status = (
                config.status.value
                if hasattr(config.status, "value")
                else str(config.status)
            )
            record.selected_category = config.selected_category or ""
            if config.pricing_summary:
                try:
                    record.pricing_total = float(config.pricing_summary.total_after_tax)
                except Exception:
                    pass
            record.data = config.model_dump_json()
            record.updated_at = now
            await session.commit()
        return config

    async def delete_async(self, configuration_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ConfigurationRecord).where(
                    ConfigurationRecord.configuration_id == configuration_id
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                return False
            await session.delete(record)
            await session.commit()
        return True

    async def exists_async(self, configuration_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.count()).where(
                    ConfigurationRecord.configuration_id == configuration_id
                )
            )
            return result.scalar() > 0

    async def list_async(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Returns list of dicts with display_id computed from row_number."""
        async with AsyncSessionLocal() as session:
            # Use a subquery to assign display_id (sequential, ordered by PK)
            subq = select(
                ConfigurationRecord,
                func.row_number()
                .over(order_by=ConfigurationRecord.id)
                .label("display_id"),
            ).subquery()
            result = await session.execute(
                select(subq).order_by(subq.c.id.desc()).offset(offset).limit(limit)
            )
            rows = result.fetchall()
        configs = []
        for row in rows:
            config = Configuration.model_validate_json(row.data)
            configs.append(
                {
                    "display_id": row.display_id,
                    "configuration_id": row.configuration_id,
                    "project_name": row.project_name,
                    "status": row.status,
                    "selected_category": row.selected_category,
                    "pricing_total": row.pricing_total,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                    "config": config,
                }
            )
        return configs

    async def search_async(self, query: str, limit: int = 20) -> list[dict]:
        """Case-insensitive search by project_name or display_id prefix."""
        async with AsyncSessionLocal() as session:
            subq = select(
                ConfigurationRecord,
                func.row_number()
                .over(order_by=ConfigurationRecord.id)
                .label("display_id"),
            ).subquery()
            q = query.strip().lower()
            result = await session.execute(
                select(subq)
                .where(
                    func.lower(subq.c.project_name).contains(q)
                    | func.cast(subq.c.display_id, String).contains(q)
                    | func.lower(subq.c.configuration_id).contains(q)
                )
                .order_by(subq.c.id.asc())
                .limit(limit)
            )
            rows = result.fetchall()
        return [
            {
                "display_id": row.display_id,
                "configuration_id": row.configuration_id,
                "project_name": row.project_name,
                "status": row.status,
                "selected_category": row.selected_category,
                "pricing_total": row.pricing_total,
            }
            for row in rows
        ]

    async def get_dashboard_metrics_async(self) -> dict:
        async with AsyncSessionLocal() as session:
            total_result = await session.execute(
                select(func.count()).select_from(ConfigurationRecord)
            )
            total = total_result.scalar() or 0

            completed_result = await session.execute(
                select(func.count()).where(
                    ConfigurationRecord.status.in_(list(_COMPLETED_STATUSES))
                )
            )
            completed = completed_result.scalar() or 0

            avg_result = await session.execute(
                select(func.avg(ConfigurationRecord.pricing_total)).where(
                    ConfigurationRecord.status.in_(list(_COMPLETED_STATUSES)),
                    ConfigurationRecord.pricing_total.isnot(None),
                )
            )
            avg_quote = avg_result.scalar()

        return {
            "total_configurations": total,
            "completed_quotes": completed,
            "configurations_on_hold": total - completed,
            "average_quote_value": round(float(avg_quote), 2) if avg_quote else 0.0,
        }

    # ── Sync wrappers (BaseConfigurationStore ABC) ────────────────────────────

    def create(self, config: Configuration) -> Configuration:
        return _run_sync(self.create_async(config))

    def get(self, configuration_id: str) -> Configuration | None:
        return _run_sync(self.get_async(configuration_id))

    def update(self, config: Configuration) -> Configuration:
        return _run_sync(self.update_async(config))

    def delete(self, configuration_id: str) -> bool:
        return _run_sync(self.delete_async(configuration_id))

    def exists(self, configuration_id: str) -> bool:
        return _run_sync(self.exists_async(configuration_id))

    def list(self, limit: int = 100, offset: int = 0) -> list[Configuration]:
        rows = _run_sync(self.list_async(limit=limit, offset=offset))
        return [r["config"] for r in rows]
