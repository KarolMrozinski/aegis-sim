from typing import Dict, List
import networkx as nx

from aegis_sim.core.models import DependencyEdge, Node, NodeStatus, RiskAssessment


class TopologyGraphEngine:
    """Silnik analityczny budujący graf zależności C5ISR i wyliczający metryki ryzyka."""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self._nodes_registry: Dict[str, Node] = {}

    def add_node(self, node: Node) -> None:
        """Dodaje węzeł do struktury grafu wraz z jego właściwościami."""
        self._nodes_registry[node.id] = node
        self.graph.add_node(
            node.id,
            name=node.name,
            category=node.category.value,
            status=node.status.value,
            capacity=node.capacity,
        )

    def add_dependency(self, edge: DependencyEdge) -> None:
        """Dodaje krawędź zależności skierowanej między węzłami."""
        if edge.source_id not in self.graph or edge.target_id not in self.graph:
            raise ValueError("Oba węzły relacji muszą być wcześniej zarejestrowane w grafie.")
        
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            weight=edge.weight,
            latency_ms=edge.latency_ms,
        )

    def calculate_betweenness_centrality(self) -> Dict[str, float]:
        """Wylicza wskaźnik centralności pośrednictwa dla węzłów."""
        if len(self.graph) == 0:
            return {}
        return nx.betweenness_centrality(self.graph)

    def identify_single_points_of_failure(self) -> List[str]:
        """
        Identyfikuje węzły, których usunięcie powoduje rozspójnienie grafu 
        lub odcięcie kluczowych podsystemów (SPOF).
        """
        spof_nodes: List[str] = []
        centrality = self.calculate_betweenness_centrality()

        for node_id, node in self._nodes_registry.items():
            # Kryterium SPOF: wysoka centralność + brak redundancji
            if node.redundancy_level == 0 and centrality.get(node_id, 0.0) > 0.1:
                spof_nodes.append(node_id)
            elif self.graph.in_degree(node_id) > 2 and self.graph.out_degree(node_id) > 2 and node.redundancy_level <= 1:
                spof_nodes.append(node_id)

        return spof_nodes

    def analyze_topology_risk(self) -> List[RiskAssessment]:
        """Generuje pełny raport oceny ryzyka dla całej topologii."""
        centrality_scores = self.calculate_betweenness_centrality()
        spof_list = set(self.identify_single_points_of_failure())
        assessments: List[RiskAssessment] = []

        for node_id, node in self._nodes_registry.items():
            score = centrality_scores.get(node_id, 0.0)
            is_spof = node_id in spof_list
            
            # Kalkulacja prawdopodobieństwa propagacji kaskadowej
            cascade_risk = min(1.0, score * 1.5 + (0.3 if is_spof else 0.0))
            
            recommendation = None
            if is_spof:
                recommendation = "CRITICAL: Zwiększ redundancję węzła (redundancy_level + 1) lub utwórz alternatywny link przesyłowy."
            elif cascade_risk > 0.6:
                recommendation = "WARNING: Wysoki wskaźnik przepływu. Wdrożyć dynamiczne równoważenie obciążenia (load balancing)."

            assessments.append(
                RiskAssessment(
                    node_id=node_id,
                    centrality_score=round(score, 4),
                    single_point_of_failure=is_spof,
                    cascade_risk_score=round(cascade_risk, 4),
                    recommended_mitigation=recommendation,
                )
            )

        return assessments