"""
analytics/timeline.py
Chronological Analysis & Interactive Timeline Visualization
Role: Member 4 (UI / UX / Analytics)
"""

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analytics.charts import CATEGORY_COLORS, get_color_for_category


def build_timeline_dataframe(memories: list[dict]) -> pd.DataFrame:
    """Converts a list of memory dictionaries into a normalized timeline DataFrame."""
    if not memories:
        return pd.DataFrame()

    records = []
    for m in memories:
        # Date fallback to today if missing
        date_str = m.get("created_at") or ""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            dt = datetime.utcnow()

        records.append({
            "id": m.get("id"),
            "title": m.get("title", "Untitled"),
            "category": m.get("category", "General"),
            "importance": m.get("importance", 1),
            "summary": m.get("summary", ""),
            "date": dt,
            "date_label": dt.strftime("%b %d, %Y"),
            "tags_str": ", ".join(m.get("tags") or [])
        })

    df = pd.DataFrame(records)
    return df.sort_values(by="date")


def create_timeline_chart(memories: list[dict]) -> go.Figure:
    """
    Creates an interactive scatter timeline showing memory creations across time,
    with circle size scaled to importance and colored by category.
    """
    if not memories:
        fig = go.Figure()
        fig.add_annotation(text="No chronological data recorded", showarrow=False, font=dict(size=14))
        fig.update_layout(height=340, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    df = build_timeline_dataframe(memories)

    # Size mapped from importance (1-5 -> 14 to 30)
    sizes = [max(12, int(imp) * 6) for imp in df["importance"]]
    colors = [get_color_for_category(cat) for cat in df["category"]]

    # Hover text
    hover_texts = [
        f"<b>{row['title']}</b><br>"
        f"Category: {row['category']}<br>"
        f"Date: {row['date_label']}<br>"
        f"Importance: {'⭐' * int(row['importance'])}<br>"
        f"Summary: {row['summary'][:80]}..."
        for _, row in df.iterrows()
    ]

    fig = go.Figure()

    # Timeline connecting line
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["importance"],
        mode="lines",
        line=dict(color="rgba(156, 163, 175, 0.4)", width=2, dash="dot"),
        hoverinfo="skip",
        showlegend=False
    ))

    # Scatter markers for each memory
    for cat in df["category"].unique():
        cat_mask = df["category"] == cat
        cat_df = df[cat_mask]
        cat_sizes = [max(12, int(imp) * 6) for imp in cat_df["importance"]]
        cat_hover = [
            f"<b>{row['title']}</b><br>"
            f"Category: {row['category']}<br>"
            f"Date: {row['date_label']}<br>"
            f"Importance: {'⭐' * int(row['importance'])}<br>"
            f"Summary: {row['summary'][:80]}..."
            for _, row in cat_df.iterrows()
        ]

        fig.add_trace(go.Scatter(
            x=cat_df["date"],
            y=cat_df["importance"],
            mode="markers+text",
            name=cat,
            marker=dict(
                size=cat_sizes,
                color=get_color_for_category(cat),
                line=dict(color="#FFFFFF", width=1.5),
                opacity=0.9
            ),
            text=cat_df["title"].apply(lambda t: t[:16] + ".." if len(t) > 16 else t),
            textposition="top center",
            textfont=dict(size=10),
            hovertext=cat_hover,
            hoverinfo="text"
        ))

    fig.update_layout(
        title=dict(text="<b>Interactive Memory Timeline</b>", font=dict(size=16)),
        xaxis=dict(
            title="Date Created",
            showgrid=True,
            gridcolor="rgba(200,200,200,0.2)"
        ),
        yaxis=dict(
            title="Importance Level",
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["⭐ Low", "⭐⭐ Normal", "⭐⭐⭐ Moderate", "⭐⭐⭐⭐ High", "⭐⭐⭐⭐⭐ Critical"],
            range=[0.5, 5.8],
            showgrid=True,
            gridcolor="rgba(200,200,200,0.2)"
        ),
        height=360,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    return fig


def get_activity_summary(memories: list[dict]) -> dict:
    """Calculates key temporal and behavioral metrics across all memories."""
    if not memories:
        return {
            "total_count": 0,
            "this_week": 0,
            "this_month": 0,
            "top_category": "None",
            "avg_importance": 0.0,
            "high_priority_count": 0
        }

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    this_week = 0
    this_month = 0
    high_priority = 0
    importances = []
    category_counts = {}

    for m in memories:
        cat = m.get("category", "General")
        category_counts[cat] = category_counts.get(cat, 0) + 1

        imp = m.get("importance", 1)
        try:
            imp_val = int(imp)
            importances.append(imp_val)
            if imp_val >= 4:
                high_priority += 1
        except Exception:
            pass

        date_str = m.get("created_at") or ""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt >= seven_days_ago:
                this_week += 1
            if dt >= thirty_days_ago:
                this_month += 1
        except Exception:
            # If date couldn't be parsed, treat as recent
            this_week += 1
            this_month += 1

    top_cat = max(category_counts, key=category_counts.get) if category_counts else "None"
    avg_imp = round(sum(importances) / len(importances), 1) if importances else 1.0

    return {
        "total_count": len(memories),
        "this_week": this_week,
        "this_month": this_month,
        "top_category": top_cat,
        "avg_importance": avg_imp,
        "high_priority_count": high_priority
    }
