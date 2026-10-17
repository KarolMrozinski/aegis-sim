from copy import deepcopy
from typing import List, Tuple
from aegis_sim.analytics.graph_analyzer import TopologyGraphEngine
from aegis_sim.core.models import NodeStatus, SimulationEvent


class AdversarySimulator:
    """Silnik symulacyjny do wstrzykiwania ataków i obliczania degradacji kaskadowej."""

    def __init__(self, engine: TopologyGraphEngine) -> None:
        # Praca na kopii grafu, aby nie modyfikować domyślnego stanu topologii
        self.engine = deepcopy(engine)

    def inject_event(self, event: SimulationEvent) -> List[Tuple[str, float, float]]:
        """
        Wstrzykuje zdarzenie awarii/ataku na wyznaczony węzeł i propaguje degradację
        po połączonych krawędziach zależności.
        
        Zwraca listę zmian w postaci: (node_id, stara_wydajność, nowa_wydajność)
        """
        if event.target_node_id not in self.engine.graph:
            raise ValueError(f"Węzeł {event.target_node_id} nie istnieje w topologii.")

        impact_history: List[Tuple[str, float, float]] = []
        visited = set()

        # Kolejka do BFS: (węzeł_docelowy, czynnik_wpływu)
        queue: List[Tuple[str, float]] = [(event.target_node_id, event.impact_factor)]

        while queue:
            current_node, current_impact = queue.pop(0)
            if current_node in visited:
                continue
            
            visited.add(current_node)

            # Pobranie dotychczasowych metryk węzła z grafu
            node_data = self.engine.graph.nodes[current_node]
            old_capacity = node_data.get("capacity", 100.0)

            # Wyliczenie nowej wydajności z uwzględnieniem redukcji wpływu
            degradation = current_impact * 100.0
            new_capacity = max(0.0, old_capacity - degradation)

            # Aktualizacja stanu w grafie
            node_data["capacity"] = new_capacity
            if new_capacity == 0.0:
                node_data["status"] = NodeStatus.OFFLINE.value
            elif new_capacity < 50.0:
                node_data["status"] = NodeStatus.CRITICAL.value
            else:
                node_data["status"] = NodeStatus.DEGRADED.value

            impact_history.append((current_node, old_capacity, new_capacity))

            # Propagacja uszkodzenia na węzły zależne (wychodzące krawędzie)
            for successor in self.engine.graph.successors(current_node):
                edge_data = self.engine.graph.get_edge_data(current_node, successor)
                edge_weight = edge_data.get("weight", 1.0) if edge_data else 1.0
                
                # Wpływ wyjściowy maleje w zależności od wagi relacji
                propagated_impact = current_impact * edge_weight * 0.75
                if propagated_impact > 0.1:  # Próg odcięcia dalszej propagacji
                    queue.append((successor, propagated_impact))

        return impact_history