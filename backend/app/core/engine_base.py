"""
Base Engine Interface.

A lightweight, generic Abstract Base Class defining the contract for all engines
in the Elevator Configuration & Pricing pipeline.

Enables future orchestration layers (like ConfigurationPipeline) to treat all
engines polymorphically, and permits transparent telemetry middleware.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.models.domain import EngineStartupReport

ContextT = TypeVar("ContextT")
ReportT = TypeVar("ReportT")


class BaseEngine(ABC, Generic[ContextT, ReportT]):
    """Abstract base class for all processing engines in the pipeline."""

    @abstractmethod
    def validate_startup(self) -> EngineStartupReport:
        """
        Verify that all required registries, repositories, and caches
        are loaded and ready to process requests.

        Returns:
            EngineStartupReport indicating readiness.
        """
        pass

    @abstractmethod
    def resolve(self, context: ContextT) -> ReportT:
        """
        Execute the engine's logic using the provided context.

        Args:
            context: The context object encapsulating configuration and runtime state.

        Returns:
            A typed report detailing the execution results.
        """
        pass
