from collections import deque

from app.models.domain import (
    Dependency,
    DependencyEdge,
    DependencyGraph,
    DependencyNode,
)


class CircularDependencyError(Exception):
    """Raised when a cycle is detected in the dependency graph."""

    pass


class GraphBuilder:
    """Constructs and analyzes the DependencyGraph."""

    @staticmethod
    def build_graph(dependencies: list[Dependency]) -> DependencyGraph:
        """Builds a DependencyGraph from a list of dependencies."""
        graph = DependencyGraph(nodes={}, adjacency_list={}, reverse_adjacency={})

        for dep in dependencies:
            # Ensure nodes exist
            if dep.source_id not in graph.nodes:
                graph.nodes[dep.source_id] = DependencyNode(
                    entity_id=dep.source_id, entity_type="UNKNOWN"
                )
            if dep.target_id not in graph.nodes:
                graph.nodes[dep.target_id] = DependencyNode(
                    entity_id=dep.target_id, entity_type="UNKNOWN"
                )

            # Add Edge
            edge = DependencyEdge(dependency=dep, is_active=True)

            if dep.source_id not in graph.adjacency_list:
                graph.adjacency_list[dep.source_id] = []
            graph.adjacency_list[dep.source_id].append(edge)

            if dep.target_id not in graph.reverse_adjacency:
                graph.reverse_adjacency[dep.target_id] = []
            graph.reverse_adjacency[dep.target_id].append(edge)

        return graph

    @staticmethod
    def populate_node_types(graph: DependencyGraph, catalogue) -> None:
        """Updates entity_type for all nodes using the catalogue."""
        known_components = {c.id for c in catalogue.components}
        known_options = {o.id for o in catalogue.feature_options}

        for node in graph.nodes.values():
            if node.entity_id in known_components:
                node.entity_type = "COMPONENT"
            elif node.entity_id in known_options:
                node.entity_type = "OPTION"
            else:
                node.entity_type = "UNKNOWN"

    @staticmethod
    def get_topological_sort(graph: DependencyGraph) -> list[str]:
        """
        Returns a list of node IDs in topological order using Kahn's algorithm.
        Only considers active edges.
        Raises CircularDependencyError if a cycle is detected.
        """
        in_degree: dict[str, int] = dict.fromkeys(graph.nodes, 0)

        # Calculate in-degrees considering only active edges
        for u in graph.adjacency_list:
            for edge in graph.adjacency_list[u]:
                if edge.is_active:
                    v = edge.dependency.target_id
                    in_degree[v] += 1

        # Queue for nodes with no incoming active edges
        queue = deque([node_id for node_id in in_degree if in_degree[node_id] == 0])
        topo_order = []

        while queue:
            u = queue.popleft()
            topo_order.append(u)

            if u in graph.adjacency_list:
                for edge in graph.adjacency_list[u]:
                    if edge.is_active:
                        v = edge.dependency.target_id
                        in_degree[v] -= 1
                        if in_degree[v] == 0:
                            queue.append(v)

        if len(topo_order) != len(graph.nodes):
            # A cycle exists. Find the nodes in the cycle for the error message.
            unresolved = [node_id for node_id in graph.nodes if in_degree[node_id] > 0]
            raise CircularDependencyError(
                f"Circular dependency detected involving nodes: {unresolved}"
            )

        return topo_order
