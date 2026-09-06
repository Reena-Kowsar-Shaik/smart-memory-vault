"""
analytics package
Visualizations, Chronological Timeline, and PDF/CSV/JSON Reporting
Role: Member 4 (UI / UX / Analytics)
"""

from .charts import (
    CATEGORY_COLORS,
    get_color_for_category,
    create_category_distribution_chart,
    create_importance_histogram,
    create_sentiment_chart,
    create_top_tags_chart
)

from .timeline import (
    build_timeline_dataframe,
    create_timeline_chart,
    get_activity_summary
)

from .reporter import (
    export_to_csv,
    export_to_json,
    generate_pdf_report
)

__all__ = [
    "CATEGORY_COLORS",
    "get_color_for_category",
    "create_category_distribution_chart",
    "create_importance_histogram",
    "create_sentiment_chart",
    "create_top_tags_chart",
    "build_timeline_dataframe",
    "create_timeline_chart",
    "get_activity_summary",
    "export_to_csv",
    "export_to_json",
    "generate_pdf_report"
]
