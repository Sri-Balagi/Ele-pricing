import time
import uuid
import logging
from datetime import datetime, timezone
from typing import List

from app.core.constants import ConfigurationStatus, RuleTriggerType, ErrorCode
from app.core.engine_base import BaseEngine
from app.core.exceptions import StartupValidationError, PipelineExecutionError
from app.models.domain import (
    Configuration,
    PipelineContext,
    PipelineExecutionReport,
    PipelineMetrics,
    EngineStartupReport,
    ProductCatalogue,
    RuleContext,
    DependencyResolutionContext,
    DependencyResolutionReport
)
from app.rules.evaluator import RuleEvaluator
from app.dependency_engine.resolver import DependencyResolver
from app.pricing_engine.engine import PricingEngine
from app.pricing_engine.context import PricingContext
from app.pricing_engine.registry import PricingRegistry
from app.pricing_engine.validator import PricingValidator

logger = logging.getLogger(__name__)

class ConfigurationPipeline:
    """
    The central orchestration layer for all Elevator Configuration engines.
    
    Responsibilities:
    - Generate unique PIPELINE correlation IDs.
    - Validate engine startup readiness.
    - Invoke engines in correct execution order.
    - Own and transition Configuration.status.
    - Aggregate engine reports into a single PipelineExecutionReport.
    """

    def __init__(
        self,
        catalogue: ProductCatalogue,
        rule_evaluator: RuleEvaluator,
        dependency_resolver: DependencyResolver,
        pricing_engine: PricingEngine,
        pricing_registry: PricingRegistry
    ):
        self.catalogue = catalogue
        
        # Engine registration in strictly defined execution order
        self.engines: List[BaseEngine] = [
            rule_evaluator,
            dependency_resolver,
            pricing_engine
        ]
        
        # Direct refs for context construction
        self.rule_evaluator = rule_evaluator
        self.dependency_resolver = dependency_resolver
        self.pricing_engine = pricing_engine
        self.pricing_registry = pricing_registry

    def _generate_correlation_id(self) -> str:
        return f"PIPE-{uuid.uuid4()}"

    def validate_startup(self) -> list[EngineStartupReport]:
        """Validate that all registered engines are ready for execution."""
        reports = []
        for engine in self.engines:
            report = engine.validate_startup()
            reports.append(report)
            if not report.ready:
                logger.error(
                    f"Engine {report.engine_name} failed startup validation: {report.errors}"
                )
        return reports

    def execute(self, configuration: Configuration, request_source: str = "API") -> PipelineExecutionReport:
        """
        Run the fully orchestrated engine pipeline against the given configuration.
        """
        t0 = time.perf_counter()
        correlation_id = self._generate_correlation_id()
        execution_timestamp = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"[{correlation_id}] BeforePipeline: Executing for config {configuration.configuration_id}")

        # 1. Pipeline Startup Validation
        t_startup = time.perf_counter()
        startup_reports = self.validate_startup()
        startup_time_ms = (time.perf_counter() - t_startup) * 1000
        
        if any(not r.ready for r in startup_reports):
            logger.error(f"[{correlation_id}] Pipeline aborted due to startup validation failure.")
            raise StartupValidationError("One or more engines failed startup validation.")

        report = PipelineExecutionReport(
            correlation_id=correlation_id,
            final_configuration_status=configuration.status,
            startup_reports=startup_reports
        )
        report.metrics.startup_validation_time_ms = startup_time_ms

        # Pipeline Error Policy State
        pipeline_success = True

        # ==========================================
        # Engine 1: Rule Engine
        # ==========================================
        logger.info(f"[{correlation_id}] BeforeEngine: RuleEngine")
        rule_context = RuleContext(
            configuration=configuration,
            catalogue=self.catalogue,
            trigger_type=RuleTriggerType.ON_SELECTION,
            execution_timestamp=execution_timestamp,
            correlation_id=correlation_id
        )
        try:
            rule_report = self.rule_evaluator.resolve(rule_context)
            report.rule_engine_report = rule_report
            report.metrics.engines_executed += 1
            logger.info(f"[{correlation_id}] AfterEngine: RuleEngine (Success)")
        except Exception as e:
            logger.error(f"[{correlation_id}] Rule Engine failed: {e}")
            report.errors.append(f"{ErrorCode.RULE_001}: Rule Engine Failed - {str(e)}")
            pipeline_success = False

        if not pipeline_success:
            return self._finalize_pipeline(report, configuration, ConfigurationStatus.DRAFT, t0)

        # ==========================================
        # Engine 2: Dependency Engine
        # ==========================================
        logger.info(f"[{correlation_id}] BeforeEngine: DependencyEngine")
        dep_report = DependencyResolutionReport(configuration_id=configuration.configuration_id)
        dep_context = DependencyResolutionContext(
            configuration=configuration,
            catalogue=self.catalogue,
            report=dep_report,
            correlation_id=correlation_id,
            execution_timestamp=execution_timestamp
        )
        try:
            dep_report = self.dependency_resolver.resolve(dep_context)
            report.dependency_engine_report = dep_report
            report.metrics.engines_executed += 1
            
            # Policy: If there are detected cycles, fail the pipeline
            if len(dep_report.cycles_detected) > 0:
                report.errors.append(f"{ErrorCode.DEP_001}: Circular dependencies detected.")
                pipeline_success = False
                logger.error(f"[{correlation_id}] AfterEngine: DependencyEngine (Failed - Cycle Detected)")
            else:
                logger.info(f"[{correlation_id}] AfterEngine: DependencyEngine (Success)")
        except Exception as e:
            logger.error(f"[{correlation_id}] Dependency Engine failed: {e}")
            report.errors.append(f"{ErrorCode.DEP_001}: Dependency Engine Failed - {str(e)}")
            pipeline_success = False
            
        if not pipeline_success:
            return self._finalize_pipeline(report, configuration, ConfigurationStatus.DRAFT, t0)

        # After Dependency success, transition to VALIDATED
        configuration.status = ConfigurationStatus.VALIDATED

        # ==========================================
        # Mock BOM Generation (Placeholder for M5/6)
        # ==========================================
        from app.models.domain import BillOfMaterials, BOMItem
        if not configuration.bill_of_materials:
            configuration.bill_of_materials = BillOfMaterials(
                items=[BOMItem(component_id=c, quantity=1) for c in configuration.resolved_components],
                total_components=len(configuration.resolved_components)
            )

        # ==========================================
        # Engine 3: Pricing Engine
        # ==========================================
        logger.info(f"[{correlation_id}] BeforeEngine: PricingEngine")
        price_context = PricingContext(
            configuration=configuration,
            catalogue=self.catalogue,
            pricing_registry=self.pricing_registry,
            correlation_id=correlation_id,
            execution_timestamp=execution_timestamp
        )
        try:
            pricing_report = self.pricing_engine.resolve(price_context)
            report.pricing_engine_report = pricing_report
            report.metrics.engines_executed += 1
            
            if len(pricing_report.errors) > 0:
                report.errors.extend(pricing_report.errors)
                pipeline_success = False
                logger.error(f"[{correlation_id}] AfterEngine: PricingEngine (Failed - Missing Prices)")
            else:
                logger.info(f"[{correlation_id}] AfterEngine: PricingEngine (Success)")
        except Exception as e:
            logger.error(f"[{correlation_id}] Pricing Engine failed: {e}")
            report.errors.append(f"{ErrorCode.PRICE_001}: Pricing Engine Failed - {str(e)}")
            pipeline_success = False
            
        if not pipeline_success:
            return self._finalize_pipeline(report, configuration, ConfigurationStatus.VALIDATED, t0)
            
        # After Pricing success, transition to PRICED
        configuration.status = ConfigurationStatus.PRICED

        # ==========================================
        # Finalization
        # ==========================================
        return self._finalize_pipeline(report, configuration, configuration.status, t0)

    def _finalize_pipeline(
        self, report: PipelineExecutionReport, configuration: Configuration, 
        final_status: ConfigurationStatus, start_time: float
    ) -> PipelineExecutionReport:
        """Helper to cleanly wrap up pipeline timing and final status."""
        configuration.status = final_status
        report.final_configuration_status = final_status
        report.metrics.total_execution_time_ms = (time.perf_counter() - start_time) * 1000
        report.metrics.success = len(report.errors) == 0
        
        logger_msg = "PipelineSucceeded" if report.metrics.success else "PipelineFailed"
        logger.info(f"[{report.correlation_id}] {logger_msg}: Completed in {report.metrics.total_execution_time_ms:.2f}ms with status {final_status}")
        
        return report
