import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Importy względne wewnątrz pakietu aegis_sim
from aegis_sim.core.models import DependencyEdge, Node, NodeCategory, NodeStatus
from aegis_sim.analytics.graph_analyzer import TopologyGraphEngine

app = typer.Typer(help="AEGIS-SIM: C5ISR Strategy & Predictive Scenario Simulator")
console = Console()


def create_sample_c5isr_topology() -> TopologyGraphEngine:
    """Tworzy przykładową, złożoną topologię C5ISR do analizy ryzyka."""
    engine = TopologyGraphEngine()

    # 1. Tworzenie węzłów (Nodes)
    nodes = [
        Node(id="HQ_C2", name="Central Command & Control", category=NodeCategory.C2_NODE, redundancy_level=0),
        Node(id="SAT_LINK_01", name="Primary SATCOM Relay", category=NodeCategory.COMMUNICATION, redundancy_level=1),
        Node(id="RADAR_ARRAY_A", name="Early Warning Radar Alpha", category=NodeCategory.SENSOR, redundancy_level=0),
        Node(id="RADAR_ARRAY_B", name="Early Warning Radar Beta", category=NodeCategory.SENSOR, redundancy_level=0),
        Node(id="ANALYTICS_HUB", name="Intel Processing Server Farm", category=NodeCategory.COMPUTE, redundancy_level=1),
        Node(id="FORWARD_BASE_01", name="Forward Operating Base Alpha", category=NodeCategory.LOGISTICS, redundancy_level=2),
    ]

    for node in nodes:
        engine.add_node(node)

    # 2. Tworzenie relacji zależności (Dependencies)
    dependencies = [
        DependencyEdge(source_id="RADAR_ARRAY_A", target_id="SAT_LINK_01", weight=0.9),
        DependencyEdge(source_id="RADAR_ARRAY_B", target_id="SAT_LINK_01", weight=0.8),
        DependencyEdge(source_id="SAT_LINK_01", target_id="ANALYTICS_HUB", weight=1.0),
        DependencyEdge(source_id="ANALYTICS_HUB", target_id="HQ_C2", weight=1.0),
        DependencyEdge(source_id="HQ_C2", target_id="FORWARD_BASE_01", weight=0.7),
    ]

    for edge in dependencies:
        engine.add_dependency(edge)

    return engine


@app.command(name="analyze")
def analyze() -> None:
    """Uruchamia analizę topologii C5ISR i generuje raport ryzyka SPOF."""
    console.print(
        Panel.fit(
            "[bold cyan]🛡️ AEGIS-SIM Engine[/bold cyan]\n[dim]C5ISR Topology Risk & SPOF Analyzer[/dim]",
            border_style="cyan",
        )
    )

    engine = create_sample_c5isr_topology()

    with console.status("[bold green]Analizowanie struktury grafu i wyliczanie metryk..."):
        assessments = engine.analyze_topology_risk()

    # Tworzenie czytelnej tabeli w terminalu
    table = Table(title="C5ISR Infrastructure Risk Assessment Report", header_style="bold magenta")
    table.add_column("Node ID", style="cyan")
    table.add_column("Centrality Score", justify="right")
    table.add_column("SPOF Status", justify="center")
    table.add_column("Cascade Risk", justify="right")
    table.add_column("Mitigation Strategy", style="yellow")

    for report in assessments:
        spof_text = "[bold red]YES[/bold red]" if report.single_point_of_failure else "[green]NO[/green]"
        risk_color = "red" if report.cascade_risk_score > 0.6 else ("yellow" if report.cascade_risk_score > 0.3 else "green")
        
        table.add_row(
            report.node_id,
            f"{report.centrality_score:.4f}",
            spof_text,
            f"[{risk_color}]{report.cascade_risk_score * 100:.1f}%[/{risk_color}]",
            report.recommended_mitigation or "[dim]None required[/dim]",
        )

    console.print(table)


if __name__ == "__main__":
    app()