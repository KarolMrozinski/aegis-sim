# 🛡️ AEGIS-SIM: C5ISR Strategy & Predictive Scenario Simulator

[![Architecture](https://img.shields.io/badge/architecture-Event--Driven%20%7C%20Graph--Based-blue)](#)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#)
[![License](https://img.shields.io/badge/license-Non--Commercial-orange)](#)

> **AEGIS-SIM** to silnik symulacji strategicznej przeznaczony do analizy zależności w infrastrukturze C5ISR, detekcji słabych ogniw (**Single Points of Failure**) oraz modelowania kaskadowych efektów ataków Red Team.

---

## ✨ Kluczowe funkcjonalności

- **Graph Topology & SPOF Detection:** Wyliczanie centralności pośrednictwa (*Betweenness Centrality*) i wykrywanie krytycznych węzłów bez redundancji (`NetworkX`).
- **Red Team Adversary Simulator:** Symulacja propagacji degradacji i awarii kaskadowej wzdłuż krawędzi zależności.
- **Dynamic CLI Dashboard:** Terminalowy interfejs raportujący status infrastruktury przed i po ataku (`Rich` + `Typer`).
- **Mermaid.js Exporter:** Automatyczny eksport topologii sieci do interaktywnych diagramów w plikach Markdown.

---

## 🏗️ Wygenerowana Topologia C5ISR

```mermaid
graph TD
    classDef spof fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef normal fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff;

    HQ_C2["Central Command & Control<br/>(C2_NODE)"]
    class HQ_C2 spof;
    SAT_LINK_01["Primary SATCOM Relay<br/>(COMMUNICATION)"]
    class SAT_LINK_01 normal;
    RADAR_ARRAY_A["Early Warning Radar Alpha<br/>(SENSOR)"]
    class RADAR_ARRAY_A normal;
    RADAR_ARRAY_B["Early Warning Radar Beta<br/>(SENSOR)"]
    class RADAR_ARRAY_B normal;
    ANALYTICS_HUB["Intel Processing Server Farm<br/>(COMPUTE)"]
    class ANALYTICS_HUB normal;
    FORWARD_BASE_01["Forward Operating Base Alpha<br/>(LOGISTICS)"]
    class FORWARD_BASE_01 normal;

    RADAR_ARRAY_A -->|w=0.9| SAT_LINK_01
    RADAR_ARRAY_B -->|w=0.8| SAT_LINK_01
    SAT_LINK_01 -->|w=1.0| ANALYTICS_HUB
    ANALYTICS_HUB -->|w=1.0| HQ_C2
    HQ_C2 -->|w=0.7| FORWARD_BASE_01