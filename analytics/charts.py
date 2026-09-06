"""
analytics/charts.py
Visualizations for Smart Memory Vault using Plotly
Role: Member 4 (UI / UX / Analytics)
"""

from collections import Counter
import pandas as pd
import plotly.graph_objects as go

# Custom color palette for categories
CATEGORY_COLORS = {
    "Work": "#3B82F6",       # Blue
    "Health": "#10B981",     # Emerald green
    "Finance": "#F59E0B",    # Amber
    "Study": "#8B5CF6",      # Purple
    "Personal": "#EC4899",   # Pink
    "General": "#6B7280",    # Slate gray
}


def get_color_for_category(category: str) -> str:
    return CATEGORY_COLORS.get(category, "#6366F1")


def create_category_distribution_chart(memories: list[dict]) -> go.Figure:
    """Creates a donut chart representing distribution across categories."""
    if not memories:
        fig = go.Figure()
        fig.add_annotation(text="No memories available yet", showarrow=False, font=dict(size=14))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    df = pd.DataFrame(memories)
    cat_counts = df["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]

    colors = [get_color_for_category(c) for c in cat_counts["category"]]

    fig = go.Figure(data=[go.Pie(
        labels=cat_counts["category"],
        values=cat_counts["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent",
        hoverinfo="label+value+percent",
        textfont=dict(size=12)
    )])

    fig.update_layout(
        title=dict(text="<b>Memories by Category</b>", font=dict(size=16)),
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig


def create_importance_histogram(memories: list[dict]) -> go.Figure:
    """Creates a bar chart showing distribution of importance ratings (1 to 5 stars)."""
    if not memories:
        fig = go.Figure()
        fig.add_annotation(text="No memories available yet", showarrow=False, font=dict(size=14))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    df = pd.DataFrame(memories)
    # Ensure all levels 1-5 are counted
    importance_counts = {lvl: 0 for lvl in range(1, 6)}
    for val in df.get("importance", []):
        try:
            val_int = int(val)
            if 1 <= val_int <= 5:
                importance_counts[val_int] += 1
        except (ValueError, TypeError):
            pass

    labels = ["⭐ Low (1)", "⭐⭐ Normal (2)", "⭐⭐⭐ Moderate (3)", "⭐⭐⭐⭐ High (4)", "⭐⭐⭐⭐⭐ Critical (5)"]
    counts = [importance_counts[i] for i in range(1, 6)]
    colors = ["#94A3B8", "#60A5FA", "#34D399", "#FBBF24", "#EF4444"]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=counts,
        marker=dict(color=colors, line=dict(color="#FFFFFF", width=1.5)),
        text=counts,
        textposition="auto"
    )])

    fig.update_layout(
        title=dict(text="<b>Priority & Importance Breakdown</b>", font=dict(size=16)),
        xaxis_title="Importance Level",
        yaxis_title="Count",
        height=320,
        margin=dict(l=20, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(200,200,200,0.2)", allowstep=False, dtick=1)
    )
    return fig


def create_sentiment_chart(memories: list[dict]) -> go.Figure:
    """Creates a horizontal bar chart displaying sentiment classifications."""
    if not memories:
        fig = go.Figure()
        fig.add_annotation(text="No sentiment data available", showarrow=False, font=dict(size=14))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    df = pd.DataFrame(memories)
    sentiments = df.get("sentiment", pd.Series(["Neutral"] * len(df)))
    sent_counts = sentiments.value_counts().reset_index()
    sent_counts.columns = ["sentiment", "count"]

    sentiment_color_map = {
        "Positive": "#10B981",
        "Neutral": "#6B7280",
        "Negative": "#EF4444",
        "Urgent / Critical": "#DC2626",
    }
    bar_colors = [sentiment_color_map.get(s, "#8B5CF6") for s in sent_counts["sentiment"]]

    fig = go.Figure(data=[go.Bar(
        y=sent_counts["sentiment"],
        x=sent_counts["count"],
        orientation="h",
        marker=dict(color=bar_colors),
        text=sent_counts["count"],
        textposition="auto"
    )])

    fig.update_layout(
        title=dict(text="<b>Emotional & Urgency Polarity</b>", font=dict(size=16)),
        xaxis_title="Number of Memories",
        yaxis_title="Sentiment",
        height=300,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(200,200,200,0.2)", dtick=1)
    )
    return fig


def create_top_tags_chart(memories: list[dict], top_n: int = 8) -> go.Figure:
    """Creates a frequency bar chart of the most common tags."""
    all_tags = []
    for m in memories:
        tags = m.get("tags") or []
        if isinstance(tags, list):
            all_tags.extend([str(t).lower() for t in tags if str(t).strip()])

    if not all_tags:
        fig = go.Figure()
        fig.add_annotation(text="No tags discovered yet", showarrow=False, font=dict(size=14))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    tag_counts = Counter(all_tags).most_common(top_n)
    tags, counts = zip(*reversed(tag_counts))

    fig = go.Figure(data=[go.Bar(
        y=list(tags),
        x=list(counts),
        orientation="h",
        marker=dict(
            color=list(counts),
            colorscale="Purples",
            line=dict(color="#FFFFFF", width=1)
        ),
        text=list(counts),
        textposition="auto"
    )])

    fig.update_layout(
        title=dict(text=f"<b>Top {min(top_n, len(tags))} Keyword Tags</b>", font=dict(size=16)),
        xaxis_title="Frequency",
        height=320,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(200,200,200,0.2)", dtick=1)
    )
    return fig
