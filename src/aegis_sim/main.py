from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from aegis_sim.core.models import DependencyEdge, Node, NodeCategory, NodeStatus
from aegis_sim.analytics.graph_analyzer import TopologyGraphEngine
from aegis_sim.exporters.mermaid import MermaidExporter
from aegis_sim.core.models import SimulationEvent
from aegis_sim.red_team.adversary import AdversarySimulator

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


@app.command(name="export")
def export_diagram(output: Path = Path("docs/topology.md")) -> None:
    """Eksportuje wygenerowany graf topologii C5ISR do pliku Markdown w formacie Mermaid.js."""
    engine = create_sample_c5isr_topology()
    exporter = MermaidExporter(engine)
    
    exporter.export_to_file(output)
    console.print(f"[bold green]✔[/bold green] Graf topologii pomyślnie wyeksportowany do: [cyan]{output}[/cyan]")

@app.command(name="simulate")
def simulate_attack(
    target: str = typer.Option("SAT_LINK_01", help="ID węzła poddawanego atakowi"),
    impact: float = typer.Option(0.8, help="Siła ataku (0.1 - 1.0)"),
) -> None:
    """Symuluje atak Red Team na wybrany węzeł i kalkuluje degradację kaskadową."""
    console.print(
        Panel.fit(
            f"[bold red]⚔️ Red Team Attack Simulation[/bold red]\nTarget: [cyan]{target}[/cyan] | Impact Factor: [yellow]{impact * 100:.0f}%[/yellow]",
            border_style="red",
        )
    )

    base_engine = create_sample_c5isr_topology()
    simulator = AdversarySimulator(base_engine)

    event = SimulationEvent(
        event_id="EVT_RED_01",
        target_node_id=target,
        impact_factor=impact,
        description=f"Automated Red Team disruption on {target}",
    )

    history = simulator.inject_event(event)

    table = Table(title="Cascade Degradation Report", header_style="bold magenta")
    table.add_column("Node ID", style="cyan")
    table.add_column("Initial Capacity", justify="right")
    table.add_column("Post-Attack Capacity", justify="right")
    table.add_column("Degradation Delta", justify="right", style="red")

    for node_id, old_cap, new_cap in history:
        delta = old_cap - new_cap
        table.add_row(
            node_id,
            f"{old_cap:.1f}%",
            f"{new_cap:.1f}%",
            f"-{delta:.1f}%",
        )

    console.print(table)


if __name__ == "__main__":
    app()