"""
analytics/reporter.py
Data Export & PDF Report Generation
Role: Member 4 (UI / UX / Analytics)
"""

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List


def export_to_csv(memories: List[Dict[str, Any]]) -> str:
    """Exports a list of memory dicts to a CSV formatted string."""
    if not memories:
        return ""

    fieldnames = ["id", "title", "category", "importance", "summary", "description", "tags", "created_at"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for m in memories:
        row = m.copy()
        if isinstance(row.get("tags"), list):
            row["tags"] = "; ".join(str(t) for t in row["tags"])
        writer.writerow(row)

    return output.getvalue()


def export_to_json(memories: List[Dict[str, Any]]) -> str:
    """Exports memories and system metadata to structured JSON format."""
    export_payload = {
        "exported_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_count": len(memories),
        "memories": memories
    }
    return json.dumps(export_payload, indent=2, ensure_ascii=False)


def _sanitize_for_pdf(text: str) -> str:
    """Sanitizes text to prevent encoding crashes with default PDF core fonts."""
    if not text:
        return ""
    # Map common unicode quotes and dashes
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "--",
        "\u2026": "...", "\u2022": "*",
        "⭐": "*", "🧠": "", "🔍": "", "📊": "", "📈": "", "✍️": "", "📄": ""
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    # Encode to latin-1 or replace
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf_report(user_info: Dict[str, Any], memories: List[Dict[str, Any]], stats: Dict[str, Any]) -> bytes:
    """
    Generates an executive PDF report using fpdf2.
    Includes summary statistics, category distribution, and detailed memory logs.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        # Fallback text if fpdf2 is unavailable
        content = f"SMART MEMORY VAULT REPORT\nUser: {user_info.get('username')}\nMemories: {len(memories)}\n"
        return content.encode("utf-8")

    class VaultReportPDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 16)
            self.set_text_color(31, 41, 55)  # Dark slate
            self.cell(0, 10, "Smart Memory Vault - Personal Dossier", new_x="LMARGIN", new_y="NEXT", align="C")
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(107, 114, 128)
            now_str = datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")
            self.cell(0, 6, f"Generated on {now_str}", new_x="LMARGIN", new_y="NEXT", align="C")
            self.line(10, 28, 200, 28)
            self.ln(6)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(156, 163, 175)
            self.cell(0, 10, f"Smart Memory Vault | Page {self.page_no()}/{{nb}}", align="C")

    pdf = VaultReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # User Profile Block
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(37, 99, 235)  # Primary blue
    pdf.cell(0, 8, "User Profile & Vault Status", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(55, 65, 81)
    username = _sanitize_for_pdf(user_info.get("username", "Guest"))
    email = _sanitize_for_pdf(user_info.get("email", "N/A"))
    pdf.cell(95, 6, f"Username: {username}", ln=0)
    pdf.cell(95, 6, f"Email: {email}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Executive KPI Summary Table
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(47, 8, f"Total Memories: {stats.get('total_count', len(memories))}", 1, 0, "C", fill=True)
    pdf.cell(47, 8, f"Urgent/Critical: {stats.get('high_priority_count', 0)}", 1, 0, "C", fill=True)
    pdf.cell(47, 8, f"Top Category: {stats.get('top_category', 'N/A')}", 1, 0, "C", fill=True)
    pdf.cell(47, 8, f"Avg Priority: {stats.get('avg_importance', '1.0')}/5", 1, 1, "C", fill=True)
    pdf.ln(6)

    # Memory Entries Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 8, f"Stored Memory Entries ({len(memories)} records)", new_x="LMARGIN", new_y="NEXT")

    if not memories:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 8, "No memory items currently stored in the vault.", new_x="LMARGIN", new_y="NEXT")
    else:
        for idx, mem in enumerate(memories, start=1):
            # Item Box
            pdf.set_draw_color(229, 231, 235)
            pdf.set_fill_color(249, 250, 251)

            title = _sanitize_for_pdf(mem.get("title", f"Memory #{idx}"))
            category = _sanitize_for_pdf(mem.get("category", "General"))
            importance = mem.get("importance", 1)
            date_str = _sanitize_for_pdf(mem.get("created_at", ""))
            summary = _sanitize_for_pdf(mem.get("summary", mem.get("description", "")))
            tags = mem.get("tags") or []
            tags_str = _sanitize_for_pdf(", ".join(str(t) for t in tags))

            # Header line of entry
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(17, 24, 39)
            pdf.cell(120, 7, f"{idx}. {title}", ln=0)

            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(75, 85, 99)
            pdf.cell(70, 7, f"[{category}] | Priority: {importance}/5 | {date_str}", new_x="LMARGIN", new_y="NEXT", align="R")

            # Summary Body
            if summary:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(55, 65, 81)
                pdf.multi_cell(0, 5, f"Summary: {summary}")

            # Tags line
            if tags_str:
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(107, 114, 128)
                pdf.cell(0, 5, f"Tags: {tags_str}", new_x="LMARGIN", new_y="NEXT")

            pdf.ln(3)

    return bytes(pdf.output())
