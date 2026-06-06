"""
WHISPER v1.3.0 — Sol-hop trajectory visualization.

Dependency-free version.

Generates:
- JSON trajectory trace
- SVG graph visualization

No matplotlib.
No networkx.
Pure Python.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from compare_node_score_reset_v01 import build_pre_reset_flv_scores
from path_sampler_v01 import select_source_target
from sol_anchored_hop_policy_v01 import (
    graph_neighbors,
    route_sol_anchored_hop_by_hop,
)
from topology_v01 import generate_topology


def graph_nodes(graph: Any) -> List[str]:
    if hasattr(graph, "nodes"):
        nodes = graph.nodes
        if callable(nodes):
            nodes = nodes()
        return list(nodes)

    if hasattr(graph, "node_count"):
        return [f"n{i}" for i in range(graph.node_count)]

    raise TypeError("graph must expose nodes or node_count")


def graph_edges(graph: Any) -> List[Tuple[str, str]]:
    if hasattr(graph, "edges"):
        edges = graph.edges
        if callable(edges):
            edges = edges()
        return [(e[0], e[1]) for e in edges]

    if hasattr(graph, "edge_list"):
        return list(graph.edge_list)

    edges = set()
    for node in graph_nodes(graph):
        for neighbor in graph_neighbors(graph, node):
            a, b = sorted([node, neighbor])
            edges.add((a, b))

    return sorted(edges)


def trajectory_edges(path: List[str]) -> List[Tuple[str, str]]:
    return [(path[i], path[i + 1]) for i in range(len(path) - 1)]


def circular_layout(nodes: List[str], width: int, height: int) -> Dict[str, Tuple[float, float]]:
    """
    Deterministic circular layout.

    Good enough for trajectory debugging.
    """
    cx = width / 2
    cy = height / 2
    radius = min(width, height) * 0.42

    ordered = sorted(nodes)
    pos = {}

    for i, node in enumerate(ordered):
        angle = 2 * math.pi * i / max(1, len(ordered))
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        pos[node] = (x, y)

    return pos


def svg_line(x1, y1, x2, y2, stroke="#1f6feb", width=1.0, opacity=1.0, marker=False):
    marker_attr = ' marker-end="url(#arrow)"' if marker else ""
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{stroke}" stroke-width="{width}" opacity="{opacity}"{marker_attr}/>'
    )


def svg_circle(x, y, r, fill="#1f6feb", stroke="#ffffff", width=1.0, opacity=1.0):
    return (
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{width}" opacity="{opacity}"/>'
    )


def svg_text(x, y, text, size=11, fill="#dbeafe", anchor="middle"):
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}" font-family="monospace">{text}</text>'
    )


def render_svg(
    nodes: List[str],
    edges: List[Tuple[str, str]],
    path: List[str],
    source: str,
    target: str,
    delivered: bool,
    loop_detected: bool,
    hop_budget: int,
    cascade_mode: str,
    cascade_strength: float,
    seed: str,
    output_path: str,
) -> None:
    width = 1400
    height = 1000

    pos = circular_layout(nodes, width, height)
    path_node_set = set(path)
    path_edge_list = trajectory_edges(path)
    path_edge_set = set(path_edge_list)

    lines = []

    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    lines.append('<rect width="100%" height="100%" fill="#020617"/>')

    lines.append("""
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/>
  </marker>
</defs>
""")

    title = (
        f"WHISPER v1.3.0 Sol-Hop Trajectory | seed={seed} | "
        f"mode={cascade_mode} | strength={cascade_strength} | "
        f"delivered={delivered} | loop={loop_detected} | hops={max(0, len(path)-1)}/{hop_budget}"
    )

    lines.append(svg_text(width / 2, 36, title, size=18, fill="#e0f2fe"))

    # Base edges
    for a, b in edges:
        if a not in pos or b not in pos:
            continue
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        lines.append(svg_line(x1, y1, x2, y2, stroke="#334155", width=0.8, opacity=0.35))

    # Base nodes
    for node in nodes:
        x, y = pos[node]
        lines.append(svg_circle(x, y, 4, fill="#64748b", stroke="#0f172a", width=0.5, opacity=0.6))

    # Path edges with arrows
    for i, (a, b) in enumerate(path_edge_list):
        if a not in pos or b not in pos:
            continue
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        width_edge = 2.5 + min(i, 6) * 0.25
        lines.append(svg_line(x1, y1, x2, y2, stroke="#38bdf8", width=width_edge, opacity=0.95, marker=True))

    # Path nodes
    for i, node in enumerate(path):
        if node not in pos:
            continue
        x, y = pos[node]
        lines.append(svg_circle(x, y, 9, fill="#38bdf8", stroke="#e0f2fe", width=1.5, opacity=1.0))
        lines.append(svg_text(x, y - 14, str(i), size=10, fill="#fef9c3"))

    # Source / target
    if source in pos:
        x, y = pos[source]
        lines.append(svg_circle(x, y, 16, fill="#22c55e", stroke="#dcfce7", width=2.0))
        lines.append(svg_text(x, y + 34, f"SRC {source}", size=13, fill="#dcfce7"))

    if target in pos:
        x, y = pos[target]
        color = "#facc15" if delivered else "#ef4444"
        lines.append(svg_circle(x, y, 18, fill=color, stroke="#fef9c3", width=2.0))
        lines.append(svg_text(x, y + 38, f"DST {target}", size=13, fill="#fef9c3"))

    # Labels for path nodes
    for node in path_node_set:
        if node not in pos:
            continue
        x, y = pos[node]
        lines.append(svg_text(x, y + 24, node, size=10, fill="#bfdbfe"))

    lines.append("</svg>")

    Path(output_path).write_text("\n".join(lines))


def visualize_trajectory(
    config_path: str = "experiments/example.json",
    seed: str = "sol-hop-demo",
    hop_budget: int = 12,
    cascade_mode: str = "hybrid",
    cascade_strength: float = 4.0,
    fractal_id: str = "36",
    json_path: str = "outputs/sol_hop_trajectory_v01.json",
    svg_path: str = "outputs/sol_hop_trajectory_v01.svg",
) -> Dict[str, Any]:
    config = json.loads(Path(config_path).read_text())

    graph = generate_topology(config, seed)
    source, target = select_source_target(graph, f"{seed}:pair")

    policy_cfg = config.get("policy", {})
    route_count = int(policy_cfg.get("route_count", 3))
    fractal_count = int(policy_cfg.get("fractal_count", 36))

    flv = build_pre_reset_flv_scores(
        graph=graph,
        source=source,
        target=target,
        route_count=route_count,
        fractal_id=fractal_count,
        seed=seed,
        pre_reset_epochs=5,
    )

    result = route_sol_anchored_hop_by_hop(
        graph=graph,
        source=source,
        target=target,
        receiver_ephemeral_id=f"receiver:{target}:ephemeral",
        sol_id=f"sol:{seed}",
        epoch="1",
        session_nonce=f"nonce:{seed}",
        node_scores=flv["node_scores"],
        seed=seed,
        hop_budget=hop_budget,
        use_directional_cascade=cascade_mode == "topological",
        cascade_mode=cascade_mode,
        cascade_strength=cascade_strength,
        fractal_id=fractal_id,
    )

    out_json = Path(json_path)
    out_svg = Path(svg_path)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_svg.parent.mkdir(parents=True, exist_ok=True)

    trace = {
        "seed": seed,
        "source": source,
        "target": target,
        "hop_budget": hop_budget,
        "cascade_mode": cascade_mode,
        "cascade_strength": cascade_strength,
        "fractal_id": fractal_id,
        "delivered": result["delivered"],
        "loop_detected": result["loop_detected"],
        "hop_count": result["hop_count"],
        "path": result["path"],
        "sol_anchor_alias_prefix": result["sol_anchor_alias"][:16],
        "hop_weights": result["hop_weights"],
    }

    out_json.write_text(json.dumps(trace, indent=2, sort_keys=True))

    render_svg(
        nodes=graph_nodes(graph),
        edges=graph_edges(graph),
        path=result["path"],
        source=source,
        target=target,
        delivered=result["delivered"],
        loop_detected=result["loop_detected"],
        hop_budget=hop_budget,
        cascade_mode=cascade_mode,
        cascade_strength=cascade_strength,
        seed=seed,
        output_path=str(out_svg),
    )

    print(f"Wrote {out_json}")
    print(f"Wrote {out_svg}")
    print("Path:", result["path"])
    print("Delivered:", result["delivered"])
    print("Loop detected:", result["loop_detected"])

    return trace


if __name__ == "__main__":
    visualize_trajectory()
