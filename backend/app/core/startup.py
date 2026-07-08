"""
Application lifecycle — startup validation and shutdown hooks.

Startup sequence:
  1. Validate all required JSON data files (exist + parseable).
  2. Pre-warm the DataLoader cache.
  3. Log readiness banner.

Shutdown sequence:
  1. Log graceful shutdown message.

Fail-fast policy:
  Any validation failure raises RuntimeError to abort startup.
  This prevents the application from silently serving requests with
  missing or corrupt data files.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.exceptions import DataFileNotFoundException, DataFormatException
from app.utils.data_loader import DataLoader
from app.utils.catalogue_validator import CatalogueValidator, CatalogueValidationException

logger = logging.getLogger(__name__)


def validate_data_files(data_dir: str) -> None:
    """
    Verify every required JSON data file exists and is parseable.

    Args:
        data_dir: Path string to the data directory (relative to backend/).

    Raises:
        RuntimeError: If any file is missing or malformed. Includes filenames.
    """
    loader = DataLoader(data_dir=data_dir)
    results = loader.validate_all()

    failures = [name for name, ok in results.items() if not ok]

    if failures:
        msg = (
            f"Startup validation failed. "
            f"The following data files are missing or malformed: {failures}. "
            f"Ensure all JSON files exist in '{data_dir}'."
        )
        logger.critical(msg)
        raise RuntimeError(msg)

    logger.info("Basic JSON validation passed. Running Catalogue Validator...")
    validator = CatalogueValidator(loader)
    try:
        validator.validate()
    except CatalogueValidationException as exc:
        logger.critical("Startup aborted due to Catalogue integrity errors.")
        raise RuntimeError(str(exc)) from exc

    logger.info("All %d data files validated successfully.", len(results))


def _prewarm_cache(data_dir: str) -> None:
    """
    Pre-load all data files into the DataLoader cache.

    This avoids the first-request latency spike on a cold start.
    Any load error here is unexpected (validation passed), so we log it
    but do not abort — the cache will self-heal on the next request.
    """
    from app.core.constants import DataFile

    loader = DataLoader(data_dir=data_dir)
    for data_file in DataFile:
        try:
            loader.load(data_file.value)
            logger.debug("Pre-warmed cache for: %s", data_file.value)
        except Exception as exc:
            logger.warning("Cache pre-warm failed for %s: %s", data_file.value, exc)


def build_lifespan(data_dir: str):
    """
    Build and return the FastAPI lifespan context manager.

    Using the lifespan pattern (not @app.on_event) as recommended
    for FastAPI 0.93+ and required for async context management.

    Args:
        data_dir: Path string to the data directory.

    Returns:
        Async context manager accepted by FastAPI(lifespan=...).
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # app parameter required by FastAPI lifespan protocol
        # ── STARTUP ───────────────────────────────────────────────
        logger.info("=" * 60)
        logger.info(" Elevator Configuration Engine — Starting up")
        logger.info("=" * 60)

        try:
            validate_data_files(data_dir)
            _prewarm_cache(data_dir)
            
            # Initialize core orchestrator and store
            from app.utils.data_loader import DataLoader
            from app.models.domain import ProductCatalogue
            from app.services.configuration_pipeline import ConfigurationPipeline
            from app.rules.evaluator import RuleEvaluator
            from app.rules.registry import RuleRegistry
            from app.rules.action_handlers import ActionRegistry
            from app.dependency_engine.resolver import DependencyResolver
            from app.pricing_engine.engine import PricingEngine
            from app.pricing_engine.registry import PricingRegistry
            from app.pricing_engine.validator import PricingValidator
            from app.services.store import InMemoryConfigurationStore
            
            loader = DataLoader(data_dir=data_dir)
            
            # Load raw data and build ProductCatalogue aggregate
            catalogue_data = {
                "metadata": (loader.load("catalog_metadata.json") or [{}])[0],
                "categories": loader.load("categories.json"),
                "feature_groups": loader.load("feature_groups.json"),
                "features": loader.load("features.json"),
                "components": loader.load("components.json"),
                "feature_options": loader.load("feature_options.json"),
                "mappings": loader.load("feature_mappings.json"),
                "dependencies": loader.load("dependencies.json"),
                "pricing": loader.load("pricing.json"),
            }
            catalogue = ProductCatalogue(**catalogue_data)
            
            rule_registry = RuleRegistry(catalogue=catalogue)
            rule_registry.load_and_validate()
            
            action_registry = ActionRegistry()
            # In a real app we'd register actual actions here, but for now we just provide the registry
            
            from app.pricing_engine.repository import PricingRepository
            pricing_registry = PricingRegistry(repository=PricingRepository(), validator=PricingValidator())
            pricing_registry.load_and_validate()
            
            pipeline = ConfigurationPipeline(
                catalogue=catalogue,
                rule_evaluator=RuleEvaluator(catalogue=catalogue, rule_registry=rule_registry, action_registry=action_registry),
                dependency_resolver=DependencyResolver(catalogue=catalogue),
                pricing_engine=PricingEngine(),
                pricing_registry=pricing_registry
            )
            store = InMemoryConfigurationStore(max_configurations=1000)
            
            app.state.pipeline = pipeline
            app.state.store = store

        except (DataFileNotFoundException, DataFormatException, RuntimeError, CatalogueValidationException) as exc:
            logger.critical("Fatal startup error: %s", exc)
            raise

        logger.info("Application ready. Accepting requests.")
        logger.info("-" * 60)

        yield  # ← Application serves requests here

        # ── SHUTDOWN ──────────────────────────────────────────────
        logger.info("-" * 60)
        logger.info("Application shutting down. Goodbye.")

    return lifespan
