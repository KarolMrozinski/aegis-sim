from pathlib import Path
from aegis_sim.analytics.graph_analyzer import TopologyGraphEngine


class MermaidExporter:
    """Generuje diagramy topologii w formacie Mermaid.js na podstawie stanu grafu C5ISR."""

    def __init__(self, engine: TopologyGraphEngine) -> None:
        self.engine = engine

    def generate_diagram(self) -> str:
        spof_nodes = set(self.engine.identify_single_points_of_failure())
        lines = ["```mermaid", "graph TD"]

        # 1. Definiowanie stylów dla węzłów krytycznych (SPOF) i standardowych
        lines.append("    classDef spof fill:#f96,stroke:#333,stroke-width:2px,color:#000;")
        lines.append("    classDef normal fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff;")

        # 2. Mapowanie węzłów
        for node_id, data in self.engine.graph.nodes(data=True):
            name = data.get("name", node_id)
            category = data.get("category", "")
            node_label = f'{node_id}["{name}<br/>({category})"]'
            
            lines.append(f"    {node_label}")
            if node_id in spof_nodes:
                lines.append(f"    class {node_id} spof;")
            else:
                lines.append(f"    class {node_id} normal;")

        # 3. Mapowanie relacji/krawędzi zależności
        for source, target, edge_data in self.engine.graph.edges(data=True):
            weight = edge_data.get("weight", 1.0)
            lines.append(f"    {source} -->|w={weight:.1f}| {target}")

        lines.append("```")
        return "\n".join(lines)

    def export_to_file(self, output_path: Path) -> None:
        """Zapisuje wygenerowany diagram Mermaid do wskazanego pliku Markdown."""
        content = self.generate_diagram()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")