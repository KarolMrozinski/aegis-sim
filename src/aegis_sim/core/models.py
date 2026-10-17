from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class NodeCategory(str, Enum):
    C2_NODE = "C2_NODE"                   # Command & Control
    COMMUNICATION = "COMMUNICATION"       # Network / Relay / Satellite Link
    SENSOR = "SENSOR"                     # Radar / OSINT / Reconnaissance
    LOGISTICS = "LOGISTICS"               # Resource / Supply Chain / Infrastructure
    COMPUTE = "COMPUTE"                   # Server / Processing Hub


class NodeStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"


class DependencyEdge(BaseModel):
    """Reprezentuje skierowaną zależność między dwoma węzłami w grafie C5ISR."""
    source_id: str = Field(..., description="ID węzła źródłowego (dostawcy zasobu/sygnału)")
    target_id: str = Field(..., description="ID węzła docelowego (zależnego)")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Krytyczność relacji (0.0 - 1.0)")
    latency_ms: float = Field(default=10.0, ge=0.0, description="Opóźnienie przepływu danych w ms")


class Node(BaseModel):
    """Reprezentuje pojedynczy zasób/komponent w topologii C5ISR."""
    id: str = Field(..., description="Unikalny identyfikator węzła")
    name: str = Field(..., description="Czytelna nazwa zasobu")
    category: NodeCategory
    status: NodeStatus = Field(default=NodeStatus.OPERATIONAL)
    capacity: float = Field(default=100.0, ge=0.0, le=100.0, description="Wydajność operacyjna %")
    redundancy_level: int = Field(default=1, ge=0, description="Liczba zapasowych ścieżek/węzłów")
    metadata: Dict[str, str] = Field(default_factory=dict)


class SimulationEvent(BaseModel):
    """Zdarzenie symulacji wstrzykiwane do silnika (np. atak Red Team, awaria)."""
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    target_node_id: str
    impact_factor: float = Field(..., ge=0.0, le=1.0, description="Stopień degradacji (1.0 = całkowita awaria)")
    description: str


class RiskAssessment(BaseModel):
    """Wynik analizy ryzyka topologii wygenerowany przez silnik grafowy."""
    node_id: str
    centrality_score: float = Field(..., description="Wskaźnik węzłowy (Betweenness Centrality)")
    single_point_of_failure: bool = Field(..., description="Czy wyłączenie węzła paraliżuje podsystem")
    cascade_risk_score: float = Field(..., ge=0.0, le=1.0, description="Prawdopodobieństwo propagacji awarii")
    recommended_mitigation: Optional[str] = None