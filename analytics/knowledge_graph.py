"""
analytics/knowledge_graph.py
Interactive Network Knowledge Graph Visualization for Smart Memory Vault
Visualizes interconnected relationships between Vault Root, Categories, Tags, and Memories.
"""

import math
import plotly.graph_objects as go
from typing import List, Dict, Any
from .charts import CATEGORY_COLORS, get_color_for_category

def create_interactive_knowledge_graph(memories: List[Dict[str, Any]], category_filter: str = "All") -> go.Figure:
    """
    Constructs a 2D interactive radial network graph with nodes for Vault, Categories, Tags, and Memories.
    """
    if not memories:
        fig = go.Figure()
        fig.add_annotation(
            text="No memories in vault to visualize graph.",
            showarrow=False,
            font=dict(size=14, color="#9CA3AF")
        )
        fig.update_layout(
            template="plotly_dark",
            height=520,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor="rgba(17, 24, 39, 0.7)"
        )
        return fig

    filtered_mems = memories if category_filter == "All" else [m for m in memories if m.get("category") == category_filter]
    if not filtered_mems:
        filtered_mems = memories

    nodes = {}
    edges = []

    # 1. Root Node (Vault Center)
    root_id = "root_vault"
    nodes[root_id] = {
        "label": "🧠 Memory Vault",
        "type": "root",
        "color": "#6366F1",
        "size": 34,
        "hover": f"Central Vault Core<br>Total Records: {len(filtered_mems)}",
        "x": 0.0,
        "y": 0.0
    }

    # 2. Category Nodes
    categories = sorted(list({m.get("category", "General") for m in filtered_mems}))
    num_cats = len(categories)
    cat_radius = 2.4

    for i, cat in enumerate(categories):
        cat_id = f"cat_{cat}"
        angle = (2 * math.pi * i) / max(1, num_cats)
        cx = cat_radius * math.cos(angle)
        cy = cat_radius * math.sin(angle)
        cat_color = get_color_for_category(cat)

        cat_mem_count = sum(1 for m in filtered_mems if m.get("category") == cat)
        nodes[cat_id] = {
            "label": f"📁 {cat}",
            "type": "category",
            "color": cat_color,
            "size": 24,
            "hover": f"<b>Category: {cat}</b><br>{cat_mem_count} memory items",
            "x": cx,
            "y": cy
        }
        edges.append((root_id, cat_id, "#4F46E5", 2))

    # 3. Memory & Tag Nodes
    tag_set = set()
    for m in filtered_mems:
        for t in (m.get("tags") or []):
            if t and str(t).strip():
                tag_set.add(str(t).lower().strip())

    top_tags = list(tag_set)[:12]
    tag_radius = 4.2
    for j, tag in enumerate(top_tags):
        tag_id = f"tag_{tag}"
        angle = (2 * math.pi * j) / max(1, len(top_tags)) + 0.3
        tx = tag_radius * math.cos(angle)
        ty = tag_radius * math.sin(angle)
        nodes[tag_id] = {
            "label": f"#{tag}",
            "type": "tag",
            "color": "#818CF8",
            "size": 14,
            "hover": f"<b>Tag Keyword:</b> #{tag}",
            "x": tx,
            "y": ty
        }

    mem_radius = 3.6
    for k, mem in enumerate(filtered_mems[:20]):
        mem_id = f"mem_{mem.get('id', k)}"
        cat = mem.get("category", "General")
        cat_id = f"cat_{cat}"
        
        # Position memory near its category
        if cat_id in nodes:
            base_x = nodes[cat_id]["x"]
            base_y = nodes[cat_id]["y"]
            offset_angle = (k * 1.7) % (2 * math.pi)
            spread = 1.0 + ((k % 3) * 0.35)
            mx = base_x + spread * math.cos(offset_angle)
            my = base_y + spread * math.sin(offset_angle)
        else:
            angle = (2 * math.pi * k) / max(1, len(filtered_mems))
            mx = mem_radius * math.cos(angle)
            my = mem_radius * math.sin(angle)

        imp_stars = "⭐" * int(mem.get("importance", 1))
        title = mem.get("title", "Untitled")
        short_title = title if len(title) <= 22 else title[:20] + "..."
        summary = (mem.get("summary") or mem.get("description", ""))[:140]

        nodes[mem_id] = {
            "label": short_title,
            "type": "memory",
            "color": get_color_for_category(cat),
            "size": 16,
            "hover": f"<b>{title}</b><br>Category: {cat}<br>Priority: {imp_stars}<br><i>{summary}...</i>",
            "x": mx,
            "y": my
        }

        # Edge from Category to Memory
        if cat_id in nodes:
            edges.append((cat_id, mem_id, "#374151", 1.2))

        # Edge from Tags to Memory
        for t in (mem.get("tags") or []):
            clean_t = str(t).lower().strip()
            tag_node_id = f"tag_{clean_t}"
            if tag_node_id in nodes:
                edges.append((tag_node_id, mem_id, "rgba(129, 140, 248, 0.4)", 0.8))

    # Build Plotly Edge Traces
    edge_x = []
    edge_y = []
    for u, v, _, _ in edges:
        if u in nodes and v in nodes:
            edge_x.extend([nodes[u]["x"], nodes[v]["x"], None])
            edge_y.extend([nodes[u]["y"], nodes[v]["y"], None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.1, color="rgba(156, 163, 175, 0.35)"),
        hoverinfo="none",
        mode="lines"
    )

    # Build Plotly Node Traces by Group
    node_traces = []
    types_config = [
        ("root", "Vault Core", 1.0),
        ("category", "Categories", 0.95),
        ("tag", "Tags", 0.85),
        ("memory", "Memories", 0.9)
    ]

    for n_type, group_name, opacity in types_config:
        type_nodes = [n for n in nodes.values() if n["type"] == n_type]
        if not type_nodes:
            continue

        trace = go.Scatter(
            x=[n["x"] for n in type_nodes],
            y=[n["y"] for n in type_nodes],
            mode="markers+text" if n_type in ["root", "category"] else "markers",
            text=[n["label"] for n in type_nodes] if n_type in ["root", "category"] else None,
            textposition="top center",
            textfont=dict(color="#F3F4F6", size=11, family="Plus Jakarta Sans"),
            hoverinfo="text",
            hovertext=[n["hover"] for n in type_nodes],
            name=group_name,
            marker=dict(
                size=[n["size"] for n in type_nodes],
                color=[n["color"] for n in type_nodes],
                opacity=opacity,
                line=dict(width=1.5, color="#FFFFFF")
            )
        )
        node_traces.append(trace)

    fig = go.Figure(
        data=[edge_trace] + node_traces,
        layout=go.Layout(
            title=dict(
                text=f"<b>🧠 Interactive Knowledge Mind Map</b> ({len(filtered_mems)} memories connected)",
                font=dict(size=16, color="#F3F4F6")
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.12,
                xanchor="center",
                x=0.5,
                font=dict(color="#9CA3AF")
            ),
            hovermode="closest",
            margin=dict(b=40, l=20, r=20, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(17, 24, 39, 0.85)",
            paper_bgcolor="rgba(17, 24, 39, 0)",
            height=560
        )
    )

    return fig
