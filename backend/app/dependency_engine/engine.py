import copy
import time
import uuid
from datetime import UTC, datetime

from app.core.constants import DependencyType, RuleSeverity, RuleTriggerType
from app.dependency_engine.graph import GraphBuilder
from app.models.domain import (
    Configuration,
    ConfigurationMutation,
    DependencyResolutionReport,
    ProductCatalogue,
    RuleContext,
    ValidationMessage,
)
from app.rules.dsl import ConditionEvaluator, ConditionParser


class DependencyEngine:
    """Orchestrates dependency resolution using the graph."""

    def __init__(self, catalogue: ProductCatalogue) -> None:
        self.catalogue = catalogue
        # Build the static graph once
        self._static_graph = GraphBuilder.build_graph(catalogue.dependencies)
        GraphBuilder.populate_node_types(self._static_graph, catalogue)

        self.parser = ConditionParser()
        self.evaluator = ConditionEvaluator()

    def resolve(self, configuration: Configuration) -> DependencyResolutionReport:
        """Evaluates graph edge conditions and traverses it topologically to resolve engineering constraints."""
        start_time = time.perf_counter()
        timestamp = datetime.now(UTC).isoformat()
        correlation_id = str(uuid.uuid4())

        # Deepcopy because we will mutate is_active based on conditions
        graph = copy.deepcopy(self._static_graph)

        # 1. Evaluate Conditions on Edges (Hybrid approach)
        context = RuleContext(
            configuration=configuration,
            catalogue=self.catalogue,
            current_rule=None,
            trigger_type=RuleTriggerType.ON_SELECTION,
            execution_timestamp=timestamp,
            correlation_id=correlation_id,
        )

        edges_traversed = 0
        for node_id, edges in graph.adjacency_list.items():
            for edge in edges:
                edges_traversed += 1
                if edge.dependency.condition_expression:
                    try:
                        ast_node = self.parser.parse(
                            edge.dependency.condition_expression
                        )
                        edge.is_active = self.evaluator.evaluate(ast_node, context)
                    except Exception:
                        # Log parsing/eval failures, deactivate edge for safety
                        edge.is_active = False
                        if not configuration.validation_results:
                            pass  # Typically engine ensures this is initialized

        # 2. Get Topological Sort Order
        # Any CircularDependencyError thrown here will be caught by the router,
        # or we could catch it and fail gracefully.
        topo_order = GraphBuilder.get_topological_sort(graph)

        nodes_evaluated = len(topo_order)
        components_added = []
        options_added = []
        conflicts_detected = []

        # 3. Traverse and Apply Dependencies
        # Only process nodes that are actually "selected" or "resolved"
        # We start with what the user/rule engine gave us.
        active_set = set(configuration.selected_feature_options) | set(
            configuration.resolved_components
        )

        for node_id in topo_order:
            if node_id not in active_set:
                continue  # Node is not active in this configuration

            # If node is active, check its active outgoing edges
            if node_id in graph.adjacency_list:
                for edge in graph.adjacency_list[node_id]:
                    if not edge.is_active:
                        continue

                    target_id = edge.dependency.target_id
                    dep_type = edge.dependency.dependency_type
                    node_type = graph.nodes[target_id].entity_type

                    if (
                        dep_type == DependencyType.REQUIRES
                        or dep_type == DependencyType.DETERMINES
                    ):
                        if target_id not in active_set:
                            active_set.add(target_id)

                            # Mutate configuration
                            if node_type == "COMPONENT":
                                configuration.resolved_components.append(target_id)
                                components_added.append(target_id)
                            elif node_type == "OPTION":
                                configuration.selected_feature_options.append(target_id)
                                options_added.append(target_id)

                            # Log mutation
                            configuration.mutations.append(
                                ConfigurationMutation(
                                    timestamp=timestamp,
                                    source_engine="DEPENDENCY_ENGINE",
                                    entity_id=target_id,
                                    mutation_type="ADDED",
                                    reason=f"Required by {node_id} ({edge.dependency.id})",
                                )
                            )

                    elif dep_type == DependencyType.EXCLUDES:
                        if target_id in active_set:
                            # Conflict!
                            conflicts_detected.append(target_id)
                            if configuration.validation_results:
                                configuration.validation_results.errors.append(
                                    ValidationMessage(
                                        severity=RuleSeverity.ERROR,
                                        code="DEP_CONFLICT",
                                        message=f"{node_id} strictly excludes {target_id}, but both are present.",
                                        source_entity_id=edge.dependency.id,
                                    )
                                )
                                configuration.validation_results.is_valid = False

                    elif dep_type == DependencyType.RECOMMENDS:
                        if target_id not in active_set:
                            if configuration.validation_results:
                                configuration.validation_results.info.append(
                                    ValidationMessage(
                                        severity=RuleSeverity.INFO,
                                        code="DEP_RECOMMENDS",
                                        message=f"{node_id} recommends {target_id}.",
                                        source_entity_id=edge.dependency.id,
                                    )
                                )

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        return DependencyResolutionReport(
            configuration_id=configuration.configuration_id,
            nodes_evaluated=nodes_evaluated,
            edges_traversed=edges_traversed,
            components_added=components_added,
            options_added=options_added,
            conflicts_detected=conflicts_detected,
            execution_time_ms=execution_time_ms,
            summary=f"Resolved {nodes_evaluated} nodes in {execution_time_ms:.2f}ms. Added {len(components_added)} components, {len(options_added)} options.",
        )
