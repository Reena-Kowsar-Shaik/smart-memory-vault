"""
Smart Memory Vault - Main Streamlit Application
Unified UI/UX & Intelligent Knowledge Dashboard

Faithfully implements the visual architecture blueprint:
1. Top Visual Flow: Add Memory -> Process & Extract -> Auto Tagging -> Store & Organize -> Ask/Search -> Get Smart Answer
2. Core Screens: Dashboard, All Memories (with Memory Details Inspector), Add Memory Multi-Modal Hub, Tags, Timeline, Ask My Memory (AI Chatbot), Reminders, Settings & Exports.
3. Bottom Key Features Banner: Semantic Search, Automatic Tagging, Voice Recording, Chatbot, Document Summarization, Timeline View, Important Memory Detection, Encryption & Security.
"""

import os
import io
import re
import json
import base64
import random
import textwrap
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# Core & Backend Imports
from core.database import init_db, MemoryRepository, UserRepository
from core.auth import login_user, register_user
from pipeline import process_document, process_url
from nlp_engine import process_memory, search_engine, categorizer, sentiment_engine, summarizer, quiz_engine, rag_engine, voice_transcriber

# Analytics & Reporting Imports
from analytics.charts import (
    CATEGORY_COLORS,
    get_color_for_category,
    create_category_distribution_chart,
    create_importance_histogram,
    create_sentiment_chart,
    create_top_tags_chart
)
from analytics.timeline import build_timeline_dataframe, create_timeline_chart, get_activity_summary
from analytics.reporter import export_to_csv, export_to_json, generate_pdf_report
from analytics.knowledge_graph import create_interactive_knowledge_graph
from analytics.streak_tracker import calculate_user_streaks, calculate_achievement_badges

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Memory Vault",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Ambient Dark Obsidian Gradient Theme */
    .stApp {
        background: radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.09) 0%, transparent 45%),
                    radial-gradient(circle at 85% 85%, rgba(56, 189, 248, 0.07) 0%, transparent 45%),
                    radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.04) 0%, transparent 55%),
                    #080C14;
        color: #F8FAFC;
    }

    .main .block-container {
        padding-top: 1.25rem;
        padding-bottom: 3.5rem;
        max-width: 96%;
    }

    /* Modern Glassmorphic Top Hero Header */
    .dash-hero-glass {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.88) 0%, rgba(30, 27, 75, 0.75) 50%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(129, 140, 248, 0.25);
        border-radius: 18px;
        padding: 16px 22px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.45), 0 0 20px -3px rgba(99, 102, 241, 0.2);
    }
    .hero-avatar-ring {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 50%, #8B5CF6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.45rem;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.45);
        flex-shrink: 0;
    }
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 10px #10B981, 0 0 20px #10B981;
        animation: pulseAnimation 2s infinite;
        margin-right: 6px;
    }
    @keyframes pulseAnimation {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .sync-status-badge {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 9999px;
        padding: 5px 14px;
        font-size: 0.76rem;
        font-weight: 700;
        color: #34D399;
        display: inline-flex;
        align-items: center;
        letter-spacing: 0.02em;
    }

    /* Metric Glass Cards - Vibrant Glowing Top Neon Bar */
    .kpi-card {
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 18px;
        text-align: left;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(14px);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 18px -4px rgba(0, 0, 0, 0.35);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.6);
        box-shadow: 0 12px 28px -6px rgba(99, 102, 241, 0.25), 0 0 15px rgba(99, 102, 241, 0.15);
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3.5px;
    }
    .kpi-card.purple::before { background: linear-gradient(90deg, #A855F7, #6366F1); }
    .kpi-card.blue::before { background: linear-gradient(90deg, #38BDF8, #3B82F6); }
    .kpi-card.emerald::before { background: linear-gradient(90deg, #34D399, #059669); }
    .kpi-card.amber::before { background: linear-gradient(90deg, #FBBF24, #EA580C); }

    .kpi-icon-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        font-size: 1.1rem;
        margin-bottom: 6px;
    }
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 2px;
    }
    .kpi-val {
        font-family: 'Outfit', sans-serif;
        font-size: 1.75rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.15;
        margin-bottom: 2px;
        background: linear-gradient(135deg, #FFFFFF 30%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-sub {
        font-size: 0.72rem;
        color: #64748B;
        font-weight: 500;
    }

    /* Button Enhancements */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.88rem;
        padding: 0.5rem 1rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.12);
        background: linear-gradient(145deg, #1E293B, #0F172A);
        color: #F1F5F9;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        border-color: #6366F1;
        box-shadow: 0 6px 18px -3px rgba(99, 102, 241, 0.4);
        color: #FFFFFF;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 50%, #4338CA 100%) !important;
        border: 1px solid rgba(165, 180, 252, 0.4) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.55) !important;
        transform: translateY(-2px);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 0.88rem;
        color: #94A3B8;
        background: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #E2E8F0;
        background: rgba(255, 255, 255, 0.03);
    }
    .stTabs [aria-selected="true"] {
        color: #818CF8 !important;
        border-bottom: 2.5px solid #6366F1 !important;
        background: rgba(99, 102, 241, 0.08) !important;
    }

    /* Form Fields & Dropzone Styling */
    div[data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.65);
        border: 1.5px dashed rgba(99, 102, 241, 0.4);
        border-radius: 14px;
        padding: 12px;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #818CF8;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.15);
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0F172A !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3) !important;
    }

    /* Memory Card Modern Styles */
    .mem-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: all 0.22s ease-in-out;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 16px -3px rgba(0, 0, 0, 0.35);
    }
    .mem-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -4px rgba(99, 102, 241, 0.25);
    }
    .mem-tag-chip {
        display: inline-block;
        background: rgba(99, 102, 241, 0.14);
        color: #C7D2FE;
        border: 1px solid rgba(99, 102, 241, 0.28);
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 6px;
        margin-right: 5px;
        margin-top: 3px;
        font-family: 'JetBrains Mono', monospace;
    }
    .mem-cat-badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 800;
        border-radius: 9999px;
        color: white;
        letter-spacing: 0.02em;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }

    /* Flashcard Study Styles */
    .flashcard-frame {
        background: linear-gradient(145deg, rgba(30, 27, 75, 0.95), rgba(15, 23, 42, 0.98));
        border: 1.5px solid rgba(99, 102, 241, 0.6);
        border-radius: 18px;
        padding: 28px 32px;
        text-align: center;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 12px 35px -5px rgba(99, 102, 241, 0.4);
        margin: 14px 0;
        transition: all 0.3s ease;
    }
    .flashcard-topic-badge {
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #C7D2FE;
        background: rgba(99, 102, 241, 0.25);
        border: 1px solid rgba(129, 140, 248, 0.4);
        padding: 4px 14px;
        border-radius: 20px;
        letter-spacing: 0.08em;
        margin-bottom: 12px;
        display: inline-block;
    }
    .flashcard-main-text {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.5;
        max-width: 700px;
    }
    .flashcard-hint {
        font-size: 0.82rem;
        color: #94A3B8;
        margin-top: 14px;
        font-style: italic;
    }

    /* Celebration Banner */
    .celebration-toast {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 182, 212, 0.15) 100%);
        border: 1.5px solid #10B981;
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 8px 24px -4px rgba(16, 185, 129, 0.35);
        animation: toastGlow 2s infinite alternate;
    }
    @keyframes toastGlow {
        from { box-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }
        to { box-shadow: 0 0 25px rgba(16, 185, 129, 0.5); }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Database Initialization & State Management
# -----------------------------------------------------------------------------
@st.cache_resource
def bootstrap_database():
    """Initializes tables on startup."""
    init_db()
    return True

bootstrap_database()

# Session State defaults
if "user" not in st.session_state:
    st.session_state["user"] = None

if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "Dashboard"

if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

if "selected_memory_id" not in st.session_state:
    st.session_state["selected_memory_id"] = None

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": "👋 Hi there! I'm your **Memory AI Assistant**. Ask me anything about your notes, projects, skills, documents, or past records!"
        }
    ]

if "filter_tag" not in st.session_state:
    st.session_state["filter_tag"] = "All"


def render_html(html_str: str):
    """Renders HTML in Streamlit cleanly without indentation or blank line issues."""
    clean_lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    st.markdown("\n".join(clean_lines), unsafe_allow_html=True)


def trigger_celebration_blast(balloons: bool = True):
    """Triggers high-energy confetti cannon particle fireworks blast and balloons."""
    if balloons:
        st.balloons()
    confetti_html = """
    <div id="confetti-blast-root" style="position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:999999;"></div>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
    <script>
        function launchFireworksBlast() {
            var targetWin = window.parent || window;
            var cFunc = (targetWin.confetti) ? targetWin.confetti : confetti;
            
            if (cFunc) {
                // High-velocity center explosive blast
                cFunc({
                    particleCount: 160,
                    spread: 100,
                    origin: { y: 0.6 },
                    colors: ['#6366F1', '#EC4899', '#38BDF8', '#10B981', '#F59E0B', '#A855F7']
                });

                // Left Cannon
                setTimeout(function() {
                    cFunc({
                        particleCount: 90,
                        angle: 60,
                        spread: 65,
                        origin: { x: 0.05, y: 0.75 },
                        colors: ['#6366F1', '#38BDF8', '#10B981']
                    });
                }, 200);

                // Right Cannon
                setTimeout(function() {
                    cFunc({
                        particleCount: 90,
                        angle: 120,
                        spread: 65,
                        origin: { x: 0.95, y: 0.75 },
                        colors: ['#EC4899', '#F59E0B', '#A855F7']
                    });
                }, 350);
            }
        }
        launchFireworksBlast();
    </script>
    """
    try:
        components.html(confetti_html, height=1, width=1)
    except Exception:
        pass


def get_memory_visual_meta(mem: dict) -> dict:
    title = (mem.get("title") or "").lower()
    tags = [t.lower() for t in (mem.get("tags") or [])]
    cat = (mem.get("category") or "General").lower()

    if any(k in title or k in tags for k in ["youtube", "video", "yt", "url_ingestion", "watch", "hiring", "accenture", "http", "www."]):
        return {
            "type_name": "YouTube / Web",
            "icon": "🎬",
            "badge_bg": "rgba(239, 68, 68, 0.18)",
            "badge_color": "#F87171",
            "badge_border": "rgba(239, 68, 68, 0.45)",
            "card_border_left": "#EF4444",
            "card_bg": "linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%)",
            "icon_bg": "rgba(239, 68, 68, 0.22)",
            "icon_color": "#EF4444"
        }
    elif any(k in title or k in tags for k in ["image", "ocr", "jpg", "jpeg", "png", "photo", "whatsapp image", "whiteboard", "certificate"]):
        return {
            "type_name": "Image & OCR",
            "icon": "🖼️",
            "badge_bg": "rgba(6, 182, 212, 0.18)",
            "badge_color": "#38BDF8",
            "badge_border": "rgba(6, 182, 212, 0.45)",
            "card_border_left": "#06B6D4",
            "card_bg": "linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%)",
            "icon_bg": "rgba(6, 182, 212, 0.22)",
            "icon_color": "#06B6D4"
        }
    elif any(k in title or k in tags for k in ["voice", "audio", "mic", "speech", "recording"]):
        return {
            "type_name": "Voice Recording",
            "icon": "🎙️",
            "badge_bg": "rgba(168, 85, 247, 0.18)",
            "badge_color": "#C084FC",
            "badge_border": "rgba(168, 85, 247, 0.45)",
            "card_border_left": "#A855F7",
            "card_bg": "linear-gradient(135deg, rgba(168, 85, 247, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%)",
            "icon_bg": "rgba(168, 85, 247, 0.22)",
            "icon_color": "#A855F7"
        }
    elif any(k in title or k in tags for k in ["pdf", "document", "docx", "doc", "report", "resume", "cert"]):
        return {
            "type_name": "PDF / Document",
            "icon": "📄",
            "badge_bg": "rgba(245, 158, 11, 0.18)",
            "badge_color": "#FBBF24",
            "badge_border": "rgba(245, 158, 11, 0.45)",
            "card_border_left": "#F59E0B",
            "card_bg": "linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%)",
            "icon_bg": "rgba(245, 158, 11, 0.22)",
            "icon_color": "#F59E0B"
        }
    elif cat == "study" or any(k in title or k in tags for k in ["study", "exam", "quiz", "notes", "lecture", "formula", "course"]):
        return {
            "type_name": "Study Knowledge",
            "icon": "🧠",
            "badge_bg": "rgba(99, 102, 241, 0.18)",
            "badge_color": "#A5B4FC",
            "badge_border": "rgba(99, 102, 241, 0.45)",
            "card_border_left": "#6366F1",
            "card_bg": "linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%)",
            "icon_bg": "rgba(99, 102, 241, 0.22)",
            "icon_color": "#A5B4FC"
        }
    elif cat == "work" or any(k in title or k in tags for k in ["work", "meeting", "deliverable", "project", "sprint"]):
        return {
            "type_name": "Work & Project",
            "icon": "💼",
            "badge_bg": "rgba(16, 185, 129, 0.18)",
            "badge_color": "#34D399",
            "badge_border": "rgba(16, 185, 129, 0.45)",
            "card_border_left": "#10B981",
            "card_bg": "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%)",
            "icon_bg": "rgba(16, 185, 129, 0.22)",
            "icon_color": "#34D399"
        }
    else:
        return {
            "type_name": "Text Note",
            "icon": "📝",
            "badge_bg": "rgba(59, 130, 246, 0.18)",
            "badge_color": "#60A5FA",
            "badge_border": "rgba(59, 130, 246, 0.45)",
            "card_border_left": "#3B82F6",
            "card_bg": "linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%)",
            "icon_bg": "rgba(59, 130, 246, 0.22)",
            "icon_color": "#60A5FA"
        }



# -----------------------------------------------------------------------------
# 3. Sample Data Seeder (Matching Mockup Screens)
# -----------------------------------------------------------------------------
SAMPLE_BLUEPRINT_MEMORIES = [
    {
        "title": "Python Project Report",
        "description": "This project is a Loan Management System built using Python. It contains features like add loan, view loan, repay loan and generate report. Also integrated Student Management System modules.",
        "category": "Work",
        "summary": "Loan and Student Management System built using Python with loan repayment, tracking, and report generation features.",
        "importance": 5,
        "tags": ["python", "project", "oop", "filehandling", "flask"],
        "doc_type": "Document (PDF)",
        "file_size": "2.4 MB",
        "created_at": "2026-09-01"
    },
    {
        "title": "Resume.pdf",
        "description": "Updated resume highlighting Python, SQL, REST APIs, Streamlit, NLP, and full-stack software development experience with major accomplishments.",
        "category": "Work",
        "summary": "Professional resume documenting Python software engineering and NLP expertise.",
        "importance": 4,
        "tags": ["career", "resume", "skills", "python"],
        "doc_type": "Document (PDF)",
        "file_size": "1.1 MB",
        "created_at": "2026-08-30"
    },
    {
        "title": "Interview Notes",
        "description": "Key preparation questions for technical interview: Data structures, OOP principles, System Design, SQL indexes, and Python memory management tips.",
        "category": "Study",
        "summary": "Comprehensive preparation notes covering algorithms, OOP, and system design.",
        "importance": 4,
        "tags": ["interview", "preparation", "study", "oop"],
        "doc_type": "Note",
        "file_size": "12 KB",
        "created_at": "2026-08-29"
    },
    {
        "title": "Flask Notes",
        "description": "Notes on building lightweight REST APIs with Flask: Blueprints, SQLAlchemy ORM, JWT authentication, and CORS configuration.",
        "category": "Study",
        "summary": "Technical guide on Flask REST architecture, ORM integration, and auth tokens.",
        "importance": 3,
        "tags": ["flask", "python", "web", "notes"],
        "doc_type": "Voice Note",
        "file_size": "450 KB",
        "created_at": "2026-08-28"
    },
    {
        "title": "Certificate - Python",
        "description": "Advanced Python Programming and Data Structures certification awarded upon course completion.",
        "category": "Study",
        "summary": "Official certificate of completion in Advanced Python and Data Structures.",
        "importance": 3,
        "tags": ["certificate", "python", "education"],
        "doc_type": "Document (PDF)",
        "file_size": "1.8 MB",
        "created_at": "2026-08-25"
    }
]

def seed_sample_data(user_id: int):
    """Populates user account with mockup memories if empty or requested."""
    for item in SAMPLE_BLUEPRINT_MEMORIES:
        MemoryRepository.create_memory(
            user_id=user_id,
            title=item["title"],
            description=item["description"],
            category=item["category"],
            summary=item["summary"],
            importance=item["importance"],
            tags=item["tags"]
        )


# -----------------------------------------------------------------------------
# 4. Authentication View (Login / Register / Demo User)
# -----------------------------------------------------------------------------
def render_auth_view():
    col_left, col_right = st.columns([1.15, 0.85], gap="large")

    with col_left:
        hero_left_html = """
            <div style="padding: 10px 0 20px 0;">
                <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.18); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 9999px; padding: 6px 16px; font-size: 0.84rem; font-weight: 700; color: #A5B4FC; margin-bottom: 16px;">
                    ✨ AI-Powered Neural Second Brain
                </div>
                <h1 style="font-size: 2.7rem; font-weight: 800; line-height: 1.15; color: #FFFFFF; margin: 0 0 14px 0; letter-spacing: -0.02em;">
                    Never Forget.<br>
                    <span style="background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Instant AI Intelligence</span> Across All Your Knowledge.
                </h1>
                <p style="font-size: 1.02rem; color: #94A3B8; line-height: 1.55; margin-bottom: 22px;">
                    Effortlessly capture voice notes, PDFs, YouTube transcripts, OCR whiteboard photos, and study materials. Smart Memory Vault auto-summarizes, categorizes, tags, and lets you chat with your entire knowledge universe.
                </p>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px;">
                    <div style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(17, 24, 39, 0.9) 100%); border: 1px solid rgba(168, 85, 247, 0.35); border-left: 4px solid #A855F7; border-radius: 10px; padding: 12px 14px;">
                        <div style="font-size: 0.95rem; font-weight: 700; color: #F8FAFC; margin-bottom: 3px;">🎙️ Live Voice Recording</div>
                        <div style="font-size: 0.78rem; color: #94A3B8; line-height: 1.35;">Direct mic dictation with instant speech-to-text intelligence</div>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(17, 24, 39, 0.9) 100%); border: 1px solid rgba(239, 68, 68, 0.35); border-left: 4px solid #EF4444; border-radius: 10px; padding: 12px 14px;">
                        <div style="font-size: 0.95rem; font-weight: 700; color: #F8FAFC; margin-bottom: 3px;">🎬 YouTube Ingestion</div>
                        <div style="font-size: 0.78rem; color: #94A3B8; line-height: 1.35;">Auto-extract video transcripts, timestamps & key takeaways</div>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(17, 24, 39, 0.9) 100%); border: 1px solid rgba(6, 182, 212, 0.35); border-left: 4px solid #06B6D4; border-radius: 10px; padding: 12px 14px;">
                        <div style="font-size: 0.95rem; font-weight: 700; color: #F8FAFC; margin-bottom: 3px;">🖼️ Image & OCR Scanner</div>
                        <div style="font-size: 0.78rem; color: #94A3B8; line-height: 1.35;">Extract text from handwritten study notes & whiteboard photos</div>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(17, 24, 39, 0.9) 100%); border: 1px solid rgba(99, 102, 241, 0.35); border-left: 4px solid #6366F1; border-radius: 10px; padding: 12px 14px;">
                        <div style="font-size: 0.95rem; font-weight: 700; color: #F8FAFC; margin-bottom: 3px;">🤖 Conversational RAG</div>
                        <div style="font-size: 0.78rem; color: #94A3B8; line-height: 1.35;">Semantic chat assistant with verified citation sources</div>
                    </div>
                </div>
            </div>
        """
        render_html(hero_left_html)

    with col_right:
        render_html("""
            <div style="text-align: center; margin-bottom: 12px; padding: 10px 0;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 54px; height: 54px; background: linear-gradient(135deg, #6366F1, #A855F7); border-radius: 16px; font-size: 1.8rem; margin-bottom: 10px; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);">🧠</div>
                <h2 style="font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 0 0 4px 0;">Access Your Vault</h2>
                <p style="font-size: 0.88rem; color: #94A3B8; margin: 0;">Sign in to continue or launch the instant demo</p>
            </div>
        """)

        tab_login, tab_register, tab_demo = st.tabs(["🔑 Sign In", "📝 Create Account", "⚡ Instant Demo"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="user@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Sign In to Vault", use_container_width=True, type="primary")

                if submit_login:
                    if not email or not password:
                        st.error("Please provide both email and password.")
                    else:
                        user = login_user(email, password)
                        if user:
                            st.session_state["user"] = user
                            st.success(f"Welcome back, {user['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password. Please verify credentials.")

        with tab_register:
            with st.form("register_form"):
                reg_username = st.text_input("Username", placeholder="e.g. reena_vault")
                reg_email = st.text_input("Email Address", placeholder="reena@example.com")
                reg_pass = st.text_input("Password (min 6 chars)", type="password")
                reg_pass_conf = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submit_reg:
                    if reg_pass != reg_pass_conf:
                        st.error("Passwords do not match.")
                    else:
                        res = register_user(reg_username, reg_email, reg_pass)
                        if res.get("success"):
                            st.success("Account created successfully! You can now sign in.")
                        else:
                            st.error(res.get("error", "Registration failed."))

        with tab_demo:
            st.markdown(textwrap.dedent("""
                <div style="background: rgba(99, 102, 241, 0.1); border: 1px dashed rgba(99, 102, 241, 0.4); border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #A5B4FC; font-size: 0.88rem; margin-bottom: 2px;">⚡ One-Click Instant Access</div>
                    <div style="font-size: 0.78rem; color: #94A3B8;">Jump directly into the live Vault preloaded with sample study notes, PDFs, voice recordings, and analytics.</div>
                </div>
            """), unsafe_allow_html=True)
            if st.button("🚀 Launch Instant Demo Mode", use_container_width=True, type="primary"):
                demo_email = "demo@vault.ai"
                demo_user = UserRepository.get_by_email(demo_email)
                if not demo_user:
                    reg_res = register_user("Demo Explorer", demo_email, "demo123456")
                    new_demo = reg_res.get("user", {})
                    demo_id = new_demo.get("id")
                    if demo_id:
                        seed_sample_data(demo_id)
                    demo_name = new_demo.get("username", "Demo Explorer")
                    demo_mail = new_demo.get("email", demo_email)
                else:
                    demo_id = demo_user.id
                    demo_name = demo_user.username
                    demo_mail = demo_user.email
                    mems = MemoryRepository.get_user_memories(demo_id)
                    if len(mems) == 0:
                        seed_sample_data(demo_id)

                st.session_state["user"] = {
                    "id": demo_id,
                    "username": demo_name,
                    "email": demo_mail
                }
                st.rerun()


# -----------------------------------------------------------------------------
# 5. Shared Component: Visual Flow Infographic
# -----------------------------------------------------------------------------
def render_visual_flow_infographic():
    pass


# -----------------------------------------------------------------------------
# 6. Shared Component: Key Features Strip
# -----------------------------------------------------------------------------
def render_key_features_strip():
    pass


# -----------------------------------------------------------------------------
# 7. Sidebar Navigation Component
# -----------------------------------------------------------------------------
def render_sidebar(user: dict, memories: list[dict]):
    with st.sidebar:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <div style="background: linear-gradient(135deg, #6366F1, #8B5CF6); width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.35rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);">🧠</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.18rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">Memory Vault</h3>
                    <p style="margin: 0; font-size: 0.74rem; color: #94A3B8;">Intelligent Knowledge OS</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(71, 85, 105, 0.7); border-radius: 10px; padding: 10px 12px; margin-bottom: 16px; backdrop-filter: blur(8px);">
                <div style="font-size: 0.88rem; font-weight: 700; color: #F1F5F9;">👤 {user['username']}</div>
                <div style="font-size: 0.74rem; color: #94A3B8;">{user['email']}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.72rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 6px;'>Main Navigation</p>", unsafe_allow_html=True)

        nav_items = [
            ("🏠 Dashboard", "Dashboard"),
            ("📑 All Memories", "All Memories"),
            ("➕ Add Memory", "Add Memory"),
            ("🧠 Study & Quiz", "Study & Quiz"),
            ("🕸️ Knowledge Graph", "Knowledge Graph"),
            ("🏷️ Tags", "Tags"),
            ("🕒 Timeline", "Timeline"),
            ("🤖 Ask My Memory", "Ask My Memory"),
            ("⏰ Reminders", "Reminders"),
            ("⚙️ Settings", "Settings")
        ]

        current_nav = st.session_state.get("current_nav", "Dashboard")
        current_idx = 0
        for i, (_, route) in enumerate(nav_items):
            if current_nav == route:
                current_idx = i
                break

        selected_label = st.selectbox(
            "Navigation Menu",
            options=[label for label, _ in nav_items],
            index=current_idx,
            label_visibility="collapsed"
        )
        for label, route in nav_items:
            if selected_label == label and st.session_state.get("current_nav") != route:
                st.session_state["current_nav"] = route
                st.rerun()

        st.divider()

        stats = get_activity_summary(memories)
        streak_data = calculate_user_streaks(memories)
        badges_list = calculate_achievement_badges(memories, streak_data)
        unlocked_count = sum(1 for b in badges_list if b["unlocked"])

        st.markdown("<p style='font-size: 0.72rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 6px;'>Vault Intelligence</p>", unsafe_allow_html=True)
        st.markdown(f"• Total Records: **{stats['total_count']}**")
        st.markdown(f"• High Priority: **{stats['high_priority_count']}**")
        st.markdown(f"• Primary Focus: **{stats['top_category']}**")
        st.markdown(f"• Habit Streak: **🔥 {streak_data['current_streak']} Days**")
        st.markdown(f"• Badges: **🎖️ {unlocked_count}/{len(badges_list)} Unlocked**")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["current_nav"] = "Dashboard"
            st.session_state["selected_memory_id"] = None
            st.rerun()


# -----------------------------------------------------------------------------
# Reusable Top Navigation Bar with Back to Dashboard Button
# -----------------------------------------------------------------------------
def render_section_header(title: str, subtitle: str = "", icon: str = "📌"):
    """Renders a clean top navigation bar with a 1-click Back to Dashboard button."""
    col_b1, col_b2 = st.columns([1.2, 5.8])
    with col_b1:
        if st.button("⬅️ Dashboard", key=f"btn_back_{title.lower().replace(' ', '_').replace('&', 'and')}", use_container_width=True):
            st.session_state["current_nav"] = "Dashboard"
            st.rerun()
    with col_b2:
        st.markdown(f"<h3 style='margin:0; padding-top:2px; font-weight: 800;'>{icon} {title}</h3>", unsafe_allow_html=True)
        if subtitle:
            st.caption(subtitle)
    st.markdown("<hr style='margin: 8px 0 16px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 8. View: Dashboard (Executive Modern AI Hub)
# -----------------------------------------------------------------------------
def render_dashboard(user: dict, memories: list[dict]):
    stats = get_activity_summary(memories)
    doc_count = sum(1 for m in memories if any(kw in (m.get("title", "") + m.get("category", "")).lower() for kw in ["pdf", "doc", "report", "resume", "cert"]))
    note_count = max(0, len(memories) - doc_count)

    # 1. Clean, Minimalist Executive Top Bar - Modern Glass Hero
    st.markdown(f"""
        <div class="dash-hero-glass">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div class="hero-avatar-ring">⚡</div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h2 style="margin: 0; color: #FFFFFF; font-size: 1.32rem; font-weight: 800; letter-spacing: -0.01em;">Welcome, {user["username"]}</h2>
                        <span style="font-size: 1.15rem;">👋</span>
                    </div>
                    <p style="margin: 2px 0 0 0; color: #94A3B8; font-size: 0.82rem;">Autonomous Memory Vault & Intelligence Hub • <strong style="color: #CBD5E1;">{stats['total_count']} items indexed</strong></p>
                </div>
            </div>
            <div class="sync-status-badge">
                <span class="pulse-dot"></span> Vault Synced
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Modern Glass KPI Cards Row
    unique_cat_count = len(set(m.get('category','General') for m in memories)) if memories else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''
            <div class="kpi-card purple">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div class="kpi-label">Total Memories</div>
                    <div class="kpi-icon-pill" style="background: rgba(168, 85, 247, 0.18); color: #C084FC;">🧠</div>
                </div>
                <div class="kpi-val">{stats["total_count"]}</div>
                <div class="kpi-sub">Across {unique_cat_count} categories</div>
            </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
            <div class="kpi-card blue">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div class="kpi-label">Documents & OCR</div>
                    <div class="kpi-icon-pill" style="background: rgba(56, 189, 248, 0.18); color: #38BDF8;">📄</div>
                </div>
                <div class="kpi-val">{doc_count}</div>
                <div class="kpi-sub">Indexed files</div>
            </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''
            <div class="kpi-card emerald">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div class="kpi-label">Notes & Media</div>
                    <div class="kpi-icon-pill" style="background: rgba(16, 185, 129, 0.18); color: #34D399;">🎙️</div>
                </div>
                <div class="kpi-val">{note_count}</div>
                <div class="kpi-sub">Text & voice logs</div>
            </div>
        ''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''
            <div class="kpi-card amber">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div class="kpi-label">High Priority</div>
                    <div class="kpi-icon-pill" style="background: rgba(245, 158, 11, 0.18); color: #FBBF24;">⭐</div>
                </div>
                <div class="kpi-val">{stats["high_priority_count"]}</div>
                <div class="kpi-sub">Critical action items</div>
            </div>
        ''', unsafe_allow_html=True)

    # 3. Clean Quick Action Row
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("➕ Add Memory", use_container_width=True, type="primary"):
            st.session_state["current_nav"] = "Add Memory"
            st.rerun()
    with q2:
        if st.button("🤖 Ask Copilot", use_container_width=True):
            st.session_state["current_nav"] = "Ask My Memory"
            st.rerun()
    with q3:
        if st.button("🧠 Study & Quiz", use_container_width=True):
            st.session_state["current_nav"] = "Study & Quiz"
            st.rerun()
    with q4:
        if st.button("📑 All Memories", use_container_width=True):
            st.session_state["current_nav"] = "All Memories"
            st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Clean Organized Tabs
    tab_recent, tab_streaks, tab_analytics = st.tabs([
        "📂 Recent Knowledge",
        "🔥 Study Streaks & Badges",
        "📊 Analytics"
    ])

    with tab_recent:
        if not memories:
            st.info("Your vault is empty. Click '➕ Add Memory' to add your first note or document.")
        else:
            for mem in memories[:6]:
                vmeta = get_memory_visual_meta(mem)
                cat = mem.get("category", "General")
                cat_color = get_color_for_category(cat)
                imp_stars = "⭐" * int(mem.get("importance", 1))
                tags = mem.get("tags") or []
                tags_html = " ".join([f"<span class='mem-tag-chip'>#{t}</span>" for t in tags[:3]])

                raw_text = mem.get("summary") or mem.get("description", "")
                clean_snippet = (raw_text.replace("\n", " ").strip()[:110] + "...") if len(raw_text) > 110 else raw_text

                card_html = f"""
                    <div class="mem-card" style="border-left: 4px solid {vmeta['card_border_left']}; background: {vmeta['card_bg']}; padding: 14px 18px; margin-bottom: 12px; border-radius: 12px; box-shadow: 0 4px 14px -3px rgba(0,0,0,0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="background: {vmeta['icon_bg']}; color: {vmeta['badge_color']}; border: 1px solid {vmeta['badge_border']}; padding: 3px 9px; border-radius: 6px; font-size: 0.76rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;">
                                    {vmeta['icon']} {vmeta['type_name']}
                                </span>
                                <span class="mem-cat-badge" style="background-color: {cat_color}; font-size: 0.72rem; padding: 2px 8px;">{cat}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span style="font-size: 0.8rem; letter-spacing: 1px;">{imp_stars}</span>
                            </div>
                        </div>
                        <div style="font-weight: 700; color: #F8FAFC; font-size: 1.02rem; margin-bottom: 4px; line-height: 1.35;">{mem.get('title')}</div>
                        <div style="color: #94A3B8; font-size: 0.84rem; margin-bottom: 8px; line-height: 1.45;">{clean_snippet}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.74rem; color: #64748B; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;">
                            <div>{tags_html}</div>
                            <div style="color: #94A3B8;">📅 {mem.get('created_at')}</div>
                        </div>
                    </div>
                """
                render_html(card_html)

            if st.button("🔍 Explore All Memories in Detail ➔", use_container_width=True):
                st.session_state["current_nav"] = "All Memories"
                st.rerun()

    with tab_streaks:
        streak_data = calculate_user_streaks(memories)
        badges_list = calculate_achievement_badges(memories, streak_data)
        unlocked_count = sum(1 for b in badges_list if b["unlocked"])

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("🔥 Current Streak", f"{streak_data['current_streak']} Days")
        with col_s2:
            st.metric("🏆 Longest Record", f"{streak_data['longest_streak']} Days")
        with col_s3:
            st.metric("📅 Total Active Days", f"{streak_data['total_active_days']} Days")
        with col_s4:
            st.metric("🎖️ Badges Unlocked", f"{unlocked_count} / {len(badges_list)}")

        w_days = streak_data.get("weekly_activity", {})
        day_chips = []
        for d, count in w_days.items():
            if count > 0:
                day_chips.append(f"<span style='background: #059669; color: #FFFFFF; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin: 2px;'>{d}: {count} ✓</span>")
            else:
                day_chips.append(f"<span style='background: #1E293B; color: #64748B; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin: 2px;'>{d}: 0</span>")
        
        st.markdown(f"<div style='background: #111827; border: 1px solid #1F2937; border-radius: 8px; padding: 8px 12px; margin: 10px 0 16px 0;'><span style='font-size: 0.8rem; font-weight: 600; color: #94A3B8; margin-right: 8px;'>Past 7-Day Activity:</span> {' '.join(day_chips)}</div>", unsafe_allow_html=True)

        st.markdown("##### 🎖️ Achievement Badges")
        b_cols = st.columns(4)
        for idx, badge in enumerate(badges_list):
            with b_cols[idx % 4]:
                border_style = "1px solid #10B981" if badge["unlocked"] else "1px solid #334155"
                bg_style = "rgba(16, 185, 129, 0.08)" if badge["unlocked"] else "rgba(17, 24, 39, 0.7)"
                status_text = "<span style='color: #10B981; font-weight: 700;'>✅ Unlocked</span>" if badge["unlocked"] else f"<span style='color: #94A3B8;'>{badge['progress']}/{badge['target']}</span>"

                st.markdown(f"""
                    <div style="border: {border_style}; background: {bg_style}; border-radius: 10px; padding: 10px; margin-bottom: 8px; min-height: 105px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 1.3rem;">{badge['icon']}</span>
                            <span style="font-size: 0.7rem;">{status_text}</span>
                        </div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #FFFFFF;">{badge['title']}</div>
                        <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px; line-height: 1.25;">{badge['description']}</div>
                    </div>
                """, unsafe_allow_html=True)

    with tab_analytics:
        if memories:
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                st.markdown("##### 📊 Category Breakdown")
                fig_cat = create_category_distribution_chart(memories)
                st.plotly_chart(fig_cat, use_container_width=True)
            with c_a2:
                st.markdown("##### 📈 Priority Levels")
                fig_imp = create_importance_histogram(memories)
                st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.info("No memories to display analytics for yet.")


# -----------------------------------------------------------------------------
# 8b. View: AI Study Flashcards & Interactive Quiz Generator
# -----------------------------------------------------------------------------
def render_study_quiz(user: dict, memories: list[dict]):
    render_section_header("AI Study & Quiz Mode", "Turn your notes, documents, and uploaded PDFs into interactive flashcards and active-recall quizzes.", "🧠")

    if not memories:
        st.info("No memories found. Add some notes or PDFs first to generate study materials.")
        return

    # Memory selection with option for All Vault Knowledge
    study_options = ["📚 Entire Vault (All Notes, PDFs & Knowledge Combined)"] + [f"{m.get('title')} ({m.get('category')})" for m in memories]

    col_sel1, col_sel2, col_sel3 = st.columns([2.5, 1.2, 1.3])
    with col_sel1:
        selected_key = st.selectbox("🎯 Select Study Topic / Document:", options=study_options, key="study_topic_selector")
    with col_sel2:
        num_items = st.selectbox("Set Size", options=[4, 6, 8, 10], index=1, key="study_num_items")
    with col_sel3:
        st.write("")
        st.write("")
        if st.button("⚡ New Question Set", use_container_width=True, help="Synthesize fresh dynamic questions from this content"):
            st.session_state["study_seed"] = st.session_state.get("study_seed", 0) + 1
            st.session_state["fc_index"] = 0
            st.session_state["fc_flipped"] = False
            st.session_state["mastered_cards"] = set()
            st.rerun()

    seed = st.session_state.get("study_seed", 0)
    if selected_key == "📚 Entire Vault (All Notes, PDFs & Knowledge Combined)":
        content_text = "\n\n".join([f"{m.get('title')}\n{m.get('description')}\n{m.get('summary', '')}" for m in memories])
        study_title = "Vault Master Deck"
        study_id = f"all_vault_{seed}_{num_items}"
        target_memories = memories
    else:
        mem_options = {f"{m.get('title')} ({m.get('category')})": m for m in memories}
        selected_mem = mem_options[selected_key]
        content_text = f"{selected_mem.get('title')}\n{selected_mem.get('description')}\n{selected_mem.get('summary', '')}"
        study_title = selected_mem.get("title", "")
        study_id = f"{selected_mem.get('id')}_{seed}_{num_items}"
        target_memories = [selected_mem]

    # Initialize cache dictionaries
    if "cached_flashcards" not in st.session_state:
        st.session_state["cached_flashcards"] = {}
    if "cached_quiz_questions" not in st.session_state:
        st.session_state["cached_quiz_questions"] = {}

    # Reset flashcard position when switching topics
    if st.session_state.get("active_study_id") != study_id:
        st.session_state["active_study_id"] = study_id
        st.session_state["fc_index"] = 0
        st.session_state["fc_flipped"] = False
        st.session_state["mastered_cards"] = set()

    study_tab1, study_tab2 = st.tabs(["🎴 Smart Flashcards", "📝 AI Multiple-Choice Quiz"])

    # ---------------------------------------------------------
    # TAB 1: SMART FLASHCARDS
    # ---------------------------------------------------------
    with study_tab1:
        st.markdown("#### 🎴 Active Recall Flashcards")
        
        # Load or generate flashcards
        if study_id not in st.session_state["cached_flashcards"]:
            st.session_state["cached_flashcards"][study_id] = quiz_engine.generate_flashcards(
                content_text, title=study_title, memories=target_memories, num_cards=num_items
            )
        all_cards = st.session_state["cached_flashcards"][study_id]

        if not all_cards:
            st.warning("Not enough text in this memory to generate flashcards. Try adding more detailed notes.")
        else:
            fc_filter_col1, fc_filter_col2 = st.columns([2, 1])
            with fc_filter_col1:
                study_filter = st.radio(
                    "Study Mode:",
                    ["All Cards", "Unmastered Cards Only"],
                    horizontal=True,
                    key=f"fc_filter_{study_id}"
                )

            # Determine active card pool
            if study_filter == "Unmastered Cards Only":
                cards = [c for idx, c in enumerate(all_cards) if idx not in st.session_state.get("mastered_cards", set())]
                if not cards:
                    st.success("🎉 You have mastered all flashcards in this deck! Switch back to 'All Cards' to review.")
                    cards = all_cards
            else:
                cards = all_cards

            if "fc_index" not in st.session_state:
                st.session_state["fc_index"] = 0
            if "fc_flipped" not in st.session_state:
                st.session_state["fc_flipped"] = False
            if "mastered_cards" not in st.session_state:
                st.session_state["mastered_cards"] = set()

            idx = st.session_state["fc_index"] % len(cards)
            card = cards[idx]
            original_idx = all_cards.index(card) if card in all_cards else idx
            is_mastered = original_idx in st.session_state["mastered_cards"]

            st.progress(
                (idx + 1) / len(cards),
                text=f"Card {idx + 1} of {len(cards)} | Mastered: {len(st.session_state['mastered_cards'])}/{len(all_cards)}"
            )

            # Flashcard Display
            is_flipped = st.session_state["fc_flipped"]
            card_title = "💡 EXPLANATION & CONTEXT" if is_flipped else f"❓ {card.get('topic', 'Concept')}: {card['concept']}"
            card_text = card["back"] if is_flipped else card["front"]
            card_hint = "Click 'Flip Card' to reveal the explanation" if not is_flipped else "Click 'Flip Card' to view question again"

            mastered_indicator = ' <span style="color: #4ADE80; font-size: 0.8rem; margin-left: 8px;">★ MASTERED</span>' if is_mastered else ''
            fc_html = f"""
                <div class="flashcard-frame">
                    <div class="flashcard-topic-badge">{card_title}{mastered_indicator}</div>
                    <div class="flashcard-main-text">{card_text}</div>
                    <div class="flashcard-hint">{card_hint}</div>
                </div>
            """
            render_html(fc_html)

            fc1, fc2, fc3, fc4, fc5 = st.columns(5)
            with fc1:
                if st.button("⏮️ Previous", use_container_width=True):
                    st.session_state["fc_index"] = (idx - 1) % len(cards)
                    st.session_state["fc_flipped"] = False
                    st.rerun()
            with fc2:
                if st.button("🔄 Flip Card", use_container_width=True, type="primary"):
                    st.session_state["fc_flipped"] = not st.session_state["fc_flipped"]
                    st.rerun()
            with fc3:
                if st.button("⏭️ Next", use_container_width=True):
                    st.session_state["fc_index"] = (idx + 1) % len(cards)
                    st.session_state["fc_flipped"] = False
                    st.rerun()
            with fc4:
                btn_label = "✅ Mastered" if not is_mastered else "↩️ Unmark"
                if st.button(btn_label, use_container_width=True):
                    if is_mastered:
                        st.session_state["mastered_cards"].remove(original_idx)
                    else:
                        st.session_state["mastered_cards"].add(original_idx)
                    st.rerun()
            with fc5:
                if st.button("🔀 Reset All", use_container_width=True):
                    st.session_state["fc_index"] = 0
                    st.session_state["fc_flipped"] = False
                    st.session_state["mastered_cards"] = set()
                    st.rerun()

    # ---------------------------------------------------------
    # TAB 2: DYNAMIC AI QUIZ
    # ---------------------------------------------------------
    with study_tab2:
        st.markdown("#### 📝 AI Multiple-Choice Knowledge Quiz")
        st.caption("Test your comprehension with questions dynamically generated from your notes, PDFs, and knowledge vault.")

        # Load or generate stable quiz questions
        if study_id not in st.session_state["cached_quiz_questions"]:
            st.session_state["cached_quiz_questions"][study_id] = quiz_engine.generate_quiz(
                content_text, title=study_title, memories=target_memories, num_questions=num_items
            )
        quiz_questions = st.session_state["cached_quiz_questions"][study_id]

        if not quiz_questions:
            st.warning("Not enough context to construct a quiz. Add more details or upload a PDF document!")
        else:
            with st.form(f"study_quiz_form_{study_id}"):
                user_answers = {}
                for q in quiz_questions:
                    q_type = q.get("type", "Multiple Choice")
                    q_html = f"""
                        <div class="quiz-question-card">
                            <span class="quiz-num">Question {q['id']}</span>
                            <span class="quiz-type-badge">{q_type}</span>
                            <div class="quiz-q-text">{q['question']}</div>
                        </div>
                    """
                    render_html(q_html)
                    user_answers[q["id"]] = st.radio(
                        f"Select answer for Question {q['id']}:",
                        options=q["options"],
                        key=f"quiz_q_{q['id']}_{study_id}",
                        label_visibility="collapsed",
                        index=None
                    )

                submit_quiz = st.form_submit_button("🎯 Submit Quiz for Grading", type="primary", use_container_width=True)

            if submit_quiz:
                correct_count = 0
                st.markdown("---")
                st.markdown("### 📊 Quiz Results & Explanations")

                for q in quiz_questions:
                    u_ans = user_answers.get(q["id"])
                    if u_ans is None:
                        st.warning(f"⚠️ **Question {q['id']} Unanswered.** Correct Answer: *{q['correct_answer']}*")
                    elif u_ans == q["correct_answer"]:
                        correct_count += 1
                        st.success(f"✅ **Question {q['id']} Correct!** Your answer: *{u_ans}*")
                    else:
                        st.error(f"❌ **Question {q['id']} Incorrect.** Your answer: *{u_ans}* | **Correct Answer:** *{q['correct_answer']}*")
                    st.caption(f"💡 {q['explanation']}")

                score_pct = int((correct_count / len(quiz_questions)) * 100)
                if score_pct >= 80:
                    trigger_celebration_blast()
                    st.success(f"🏆 Outstanding! You scored **{correct_count}/{len(quiz_questions)} ({score_pct}%)**! Knowledge mastered.")
                elif score_pct >= 50:
                    st.info(f"👍 Good effort! You scored **{correct_count}/{len(quiz_questions)} ({score_pct}%)**. Review the cards and test again!")
                else:
                    st.warning(f"📚 You scored **{correct_count}/{len(quiz_questions)} ({score_pct}%)**. Check your flashcards and give it another try!")


# -----------------------------------------------------------------------------
# 8c. View: Interactive Knowledge Mind Map Graph
# -----------------------------------------------------------------------------
def render_knowledge_graph_view(user: dict, memories: list[dict]):
    render_section_header("Interactive Knowledge Mind Map", "Explore relationships between your memories, categories, and keyword tags as an interactive neural network.", "🕸️")

    if not memories:
        st.info("No memories in your vault to visualize.")
        return

    col_g_cat, col_g_stats = st.columns([2, 2])
    with col_g_cat:
        all_cats = ["All"] + sorted(list({m.get("category", "General") for m in memories}))
        sel_cat = st.selectbox("Filter Graph by Category", options=all_cats)
    with col_g_stats:
        filtered_count = len(memories) if sel_cat == "All" else sum(1 for m in memories if m.get("category") == sel_cat)
        st.metric("Connected Nodes", f"{filtered_count} Memories", delta=f"{len(all_cats)-1} Categories Active")

    fig_graph = create_interactive_knowledge_graph(memories, category_filter=sel_cat)
    st.plotly_chart(fig_graph, use_container_width=True)

    st.markdown("💡 *Tip: Hover over any node in the graph to preview memory details, categories, importance stars, and summaries!*")



# -----------------------------------------------------------------------------
# 9. View: All Memories & Memory Details Inspector
# -----------------------------------------------------------------------------
def render_all_memories(user: dict, memories: list[dict]):
    render_section_header("All Memories Repository", "Browse, filter, and inspect your stored knowledge items, documents, and notes.", "📑")

    if not memories:
        st.info("Your vault is currently empty.")
        if st.button("✨ Load Sample Memories", type="primary"):
            seed_sample_data(user["id"])
            st.rerun()
        return

    s_col, c_col, p_col, o_col = st.columns([3, 1.5, 1.5, 1.5])
    with s_col:
        search_kw = st.text_input("🔍 Search memories...", value=st.session_state.get("search_query", ""), placeholder="e.g. Python, Loan Management, interview...")
    with c_col:
        cats = ["All"] + sorted(list({m.get("category", "General") for m in memories}))
        sel_cat = st.selectbox("Category", options=cats)
    with p_col:
        min_imp = st.selectbox("Min Priority", options=[1, 2, 3, 4, 5], format_func=lambda x: f"{x} ⭐" if x > 1 else "All Ratings")
    with o_col:
        sort_by = st.selectbox("Sort Order", options=["Newest First", "Oldest First", "Highest Priority"])

    filtered = memories.copy()
    if search_kw.strip():
        searchable_list = []
        for m in filtered:
            m_copy = m.copy()
            m_copy["content"] = m.get("description", "")
            searchable_list.append(m_copy)
        filtered = search_engine.search(search_kw.strip(), searchable_list, top_k=50)

    if sel_cat != "All":
        filtered = [m for m in filtered if m.get("category") == sel_cat]

    if min_imp > 1:
        filtered = [m for m in filtered if int(m.get("importance", 1)) >= min_imp]

    if sort_by == "Newest First":
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort_by == "Oldest First":
        filtered.sort(key=lambda x: x.get("created_at", ""))
    elif sort_by == "Highest Priority":
        filtered.sort(key=lambda x: int(x.get("importance", 1)), reverse=True)

    col_list, col_detail = st.columns([1.6, 1.4])

    with col_list:
        st.markdown(f"**Showing {len(filtered)} Memories**")
        if not filtered:
            st.warning("No memories match your search and filter criteria.")

        for mem in filtered:
            mem_id = mem.get("id")
            vmeta = get_memory_visual_meta(mem)
            cat = mem.get("category", "General")
            cat_color = get_color_for_category(cat)
            imp_stars = "⭐" * int(mem.get("importance", 1))
            tags = mem.get("tags") or []
            tags_html = " ".join([f"<span class='mem-tag-chip'>#{t}</span>" for t in tags[:4]])

            is_selected = (st.session_state.get("selected_memory_id") == mem_id)
            selected_border = "border: 2px solid #6366F1;" if is_selected else f"border-left: 4px solid {vmeta['card_border_left']};"

            with st.container():
                card_html = f"""
                    <div class="mem-card" style="{selected_border} background: {vmeta['card_bg']}; padding: 14px 18px; margin-bottom: 12px; border-radius: 12px; box-shadow: 0 4px 14px -3px rgba(0,0,0,0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="background: {vmeta['icon_bg']}; color: {vmeta['badge_color']}; border: 1px solid {vmeta['badge_border']}; padding: 3px 9px; border-radius: 6px; font-size: 0.76rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;">
                                    {vmeta['icon']} {vmeta['type_name']}
                                </span>
                                <span class="mem-cat-badge" style="background-color: {cat_color}; font-size: 0.72rem; padding: 2px 8px;">{cat}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span style="font-size: 0.8rem; letter-spacing: 1px;">{imp_stars}</span>
                            </div>
                        </div>
                        <div style="font-weight: 700; color: #F8FAFC; font-size: 1.02rem; margin-bottom: 4px; line-height: 1.35;">{mem.get('title')}</div>
                        <p style="color: #94A3B8; font-size: 0.84rem; margin: 4px 0 8px 0; line-height: 1.45;">
                            {mem.get('summary') or mem.get('description', '')[:100] + '...'}
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.74rem; color: #64748B; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;">
                            <div>{tags_html}</div>
                            <div style="color: #94A3B8;">📅 {mem.get('created_at')}</div>
                        </div>
                    </div>
                """
                render_html(card_html)

                btn_col1, btn_col2 = st.columns([3, 1])
                with btn_col1:
                    if st.button(f"👁️ View Details", key=f"sel_{mem_id}", use_container_width=True):
                        st.session_state["selected_memory_id"] = mem_id
                        st.rerun()
                with btn_col2:
                    if st.button(f"🗑️", key=f"del_{mem_id}", help="Delete Memory"):
                        MemoryRepository.delete_memory(mem_id, user["id"])
                        if st.session_state.get("selected_memory_id") == mem_id:
                            st.session_state["selected_memory_id"] = None
                        st.success(f"Memory #{mem_id} removed.")
                        st.rerun()

    with col_detail:
        st.markdown("#### 🔍 Memory Details Inspector")
        sel_id = st.session_state.get("selected_memory_id")
        selected_mem = next((m for m in memories if m.get("id") == sel_id), None) if sel_id else (filtered[0] if filtered else None)

        if selected_mem:
            vmeta = get_memory_visual_meta(selected_mem)
            cat = selected_mem.get("category", "General")
            cat_color = get_color_for_category(cat)
            tags = selected_mem.get("tags") or []
            tags_html = " ".join([f"<span class='mem-tag-chip' style='font-size: 0.82rem;'>#{t}</span>" for t in tags])

            inspector_html = f"""
                <div class="detail-inspector" style="border-top: 4px solid {vmeta['card_border_left']};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: {vmeta['icon_bg']}; color: {vmeta['badge_color']}; border: 1px solid {vmeta['badge_border']}; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;">
                                {vmeta['icon']} {vmeta['type_name']}
                            </span>
                            <span class="mem-cat-badge" style="background-color: {cat_color}; font-size: 0.8rem; padding: 3px 10px;">{cat}</span>
                        </div>
                        <span style="font-size: 0.95rem;">{'⭐' * int(selected_mem.get('importance', 1))}</span>
                    </div>
                    <h3 style="margin-bottom: 8px; color: #FFFFFF;">{selected_mem.get('title')}</h3>
                    <div style="margin-bottom: 16px;">{tags_html}</div>
                    <div class="detail-field">
                        <div class="detail-field-label">Content Preview</div>
                        <div class="detail-field-val" style="background: #1F2937; padding: 12px; border-radius: 8px; border: 1px solid #374151; font-size: 0.88rem; line-height: 1.5; color: #E5E7EB;">
                            {selected_mem.get('description')}
                        </div>
                    </div>
                    <div class="detail-field" style="margin-top: 14px;">
                        <div class="detail-field-label">AI Generated Summary</div>
                        <div class="detail-field-val" style="color: #A5B4FC; font-style: italic; font-size: 0.88rem; background: rgba(99, 102, 241, 0.08); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.25);">
                            "{selected_mem.get('summary')}"
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; border-top: 1px solid #1F2937; padding-top: 14px;">
                        <div class="detail-field">
                            <div class="detail-field-label">Format Type</div>
                            <div class="detail-field-val"><b>{vmeta['icon']} {vmeta['type_name']}</b></div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-field-label">Date Added</div>
                            <div class="detail-field-val">{selected_mem.get('created_at')}</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-field-label">Character Count</div>
                            <div class="detail-field-val">{len(selected_mem.get('description', ''))} chars</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-field-label">Memory ID</div>
                            <div class="detail-field-val">#{selected_mem.get('id')}</div>
                        </div>
                    </div>
                </div>
            """
            render_html(inspector_html)
        else:
            st.info("Select any memory on the left to view its complete properties.")


# -----------------------------------------------------------------------------
# 10. View: Add Memory Hub (Text, Document, Voice, Image, Web & YouTube)
# -----------------------------------------------------------------------------
def render_add_memory(user: dict):
    render_section_header(
        title="Add New Memory Hub",
        subtitle="Capture knowledge through text, docs, voice, images (OCR), or YouTube & web scraping.",
        icon="➕"
    )

    tab_text, tab_doc, tab_voice, tab_img, tab_url = st.tabs([
        "📝 Text Note",
        "📄 PDF / Document",
        "🎙️ Voice Note Recording",
        "🖼️ Image & OCR",
        "🌐 Web & YouTube Ingestion"
    ])

    with tab_text:
        st.markdown("#### Capture Text Note")
        with st.form("add_note_form"):
            note_title = st.text_input("Memory Title", placeholder="e.g. Python Project Report, Interview Prep...")
            note_desc = st.text_area("Note Content & Details", height=160, placeholder="Type or paste your notes, code snippets, project highlights, or meeting minutes...")

            col_cat, col_imp = st.columns(2)
            with col_cat:
                cat_choice = st.selectbox("Category", options=["Auto-Detect (AI)", "Work", "Study", "Health", "Finance", "Personal", "General"])
            with col_imp:
                imp_level = st.slider("Importance Level", 1, 5, 3)

            custom_tags = st.text_input("Custom Tags (comma-separated, or leave blank for AI)", placeholder="e.g. python, oop, project")
            submit_note = st.form_submit_button("🚀 Process & Save Memory", type="primary", use_container_width=True)

        if submit_note:
            if not note_title.strip() or not note_desc.strip():
                st.error("Please provide both a title and content.")
            else:
                with st.spinner("AI Engine is analyzing, tagging, and summarizing..."):
                    ai_res = process_memory(note_desc, title=note_title)
                    final_cat = ai_res["category"] if cat_choice == "Auto-Detect (AI)" else cat_choice
                    if custom_tags.strip():
                        final_tags = [t.strip().lower() for t in custom_tags.split(",") if t.strip()]
                    else:
                        final_tags = ai_res["tags"]

                    MemoryRepository.create_memory(
                        user_id=user["id"],
                        title=note_title.strip(),
                        description=note_desc.strip(),
                        category=final_cat,
                        summary=ai_res["summary"],
                        importance=imp_level,
                        tags=final_tags
                    )
                st.success(f"🎉 Memory '{note_title}' saved to Vault successfully!")
                trigger_celebration_blast()

    with tab_doc:
        st.markdown("#### Ingest PDF, Word (.docx), TXT or Markdown Document")
        uploaded_doc = st.file_uploader("Upload File", type=["pdf", "docx", "txt", "md"], help="Max file size: 100MB")

        if uploaded_doc is not None:
            file_bytes = uploaded_doc.getvalue()
            filename = uploaded_doc.name
            st.info(f"📁 **{filename}** ({len(file_bytes)/1024:.1f} KB)")

            col_d_title, col_d_cat = st.columns(2)
            with col_d_title:
                custom_doc_title = st.text_input("Memory Title (Optional)", value=f"Doc: {filename}", placeholder=f"Doc: {filename}")
            with col_d_cat:
                doc_cat_choice = st.selectbox("Category", options=["Auto-Detect (AI)", "Work", "Study", "Health", "Finance", "Personal", "General"], key="doc_cat_sel")

            col_d_imp, col_d_tags = st.columns(2)
            with col_d_imp:
                doc_imp_level = st.slider("Importance Level", 1, 5, 3, key="doc_imp_slider")
            with col_d_tags:
                doc_custom_tags = st.text_input("Custom Tags (comma-separated, or leave blank for AI)", placeholder="e.g. report, notes, 2026", key="doc_tags_input")

            if st.button("🚀 Ingest, Parse & Save Document to Vault", type="primary", use_container_width=True):
                with st.spinner("Executing document extraction & regex entity cleaner..."):
                    doc_res = process_document(file_bytes, filename, user["id"])

                if doc_res.get("status") == "error":
                    st.error(f"Extraction failed: {doc_res.get('error_message')}")
                else:
                    meta = doc_res.get("metadata", {})
                    cleaned_txt = doc_res.get("cleaned_text", "")
                    entities = doc_res.get("extracted_entities", {})
                    content_for_ai = cleaned_txt[:4000] if cleaned_txt.strip() else filename

                    with st.spinner("Generating AI Summary and Tags..."):
                        ai_doc = process_memory(content_for_ai, title=custom_doc_title or filename)

                    final_cat = ai_doc["category"] if doc_cat_choice == "Auto-Detect (AI)" else doc_cat_choice
                    
                    if doc_custom_tags.strip():
                        user_tags = [t.strip().lower() for t in doc_custom_tags.split(",") if t.strip()]
                        final_tags = user_tags
                    else:
                        final_tags = ai_doc["tags"]

                    saved_mem = MemoryRepository.create_memory(
                        user_id=user["id"],
                        title=custom_doc_title.strip() or f"Doc: {filename}",
                        description=cleaned_txt[:5000] if cleaned_txt.strip() else f"Document: {filename}",
                        category=final_cat,
                        summary=ai_doc["summary"],
                        importance=doc_imp_level,
                        tags=final_tags
                    )

                    st.session_state["last_added_doc"] = {
                        "filename": filename,
                        "meta": meta,
                        "cleaned_txt": cleaned_txt,
                        "entities": entities,
                        "ai_doc": ai_doc,
                        "category": final_cat,
                        "memory_id": saved_mem.get("id") if saved_mem else None
                    }

                    st.success(f"🎉 Document '{filename}' parsed and saved to Vault successfully!")
                    trigger_celebration_blast()

        # Display last added document stats and entities if available
        if st.session_state.get("last_added_doc"):
            last_doc = st.session_state["last_added_doc"]
            st.markdown("---")
            st.markdown(f"#### 📄 Last Ingested Document: `{last_doc['filename']}`")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Pages", last_doc["meta"].get("page_count", 1))
            m2.metric("Words", last_doc["meta"].get("word_count", len(last_doc["cleaned_txt"].split())))
            m3.metric("Duplicate?", "Yes" if last_doc["meta"].get("is_duplicate") else "No")
            m4.metric("Category", last_doc["category"])

            entities = last_doc.get("entities", {})
            st.markdown("##### 🔍 Discovered Regex Entities")
            ent_cols = st.columns(4)
            with ent_cols[0]:
                st.markdown(f"**📅 Dates ({len(entities.get('dates', []))}):**")
                for d in entities.get("dates", [])[:4]:
                    st.markdown(f"<span class='entity-tag'>{d}</span>", unsafe_allow_html=True)
            with ent_cols[1]:
                st.markdown(f"**✉️ Emails ({len(entities.get('emails', []))}):**")
                for e in entities.get("emails", [])[:3]:
                    st.markdown(f"<span class='entity-tag'>{e}</span>", unsafe_allow_html=True)
            with ent_cols[2]:
                st.markdown(f"**📞 Phones ({len(entities.get('phone_numbers', []))}):**")
                for p in entities.get("phone_numbers", [])[:3]:
                    st.markdown(f"<span class='entity-tag'>{p}</span>", unsafe_allow_html=True)
            with ent_cols[3]:
                st.markdown(f"**💵 Amounts ({len(entities.get('amounts', []))}):**")
                for a in entities.get("amounts", [])[:3]:
                    st.markdown(f"<span class='entity-tag'>{a}</span>", unsafe_allow_html=True)

            st.markdown("##### 🧠 AI Enrichment")
            st.markdown(f"**Summary:** {last_doc['ai_doc']['summary']}")
            st.markdown(f"**Auto Category:** `{last_doc['category']}` | **Priority:** `{last_doc['ai_doc']['importance']}/5`")

    with tab_voice:
        st.markdown("#### 🎙️ Voice Based Memory Recording")
        st.caption("Click the microphone button below to record your voice note. Your speech will be transcribed and automatically indexed into your Vault.")

        mic_audio = st.audio_input("🔴 Click the red microphone button to speak:", key="voice_mic_recorder")

        if mic_audio is not None:
            audio_bytes = mic_audio.getvalue()
            audio_hash = hash(audio_bytes)

            # Auto-transcribe recording if not already cached
            if st.session_state.get("last_voice_audio_hash") != audio_hash:
                with st.spinner("🎧 Transcribing your voice in real-time..."):
                    t_res = voice_transcriber.transcribe(audio_bytes)
                    if t_res["success"] and t_res["text"]:
                        st.session_state["active_voice_text"] = t_res["text"]
                        st.session_state["active_voice_status"] = "success"
                    else:
                        # Fallback descriptive text so saving is never blocked
                        st.session_state["active_voice_text"] = f"Voice note recording captured on {datetime.utcnow().strftime('%b %d, %Y at %H:%M UTC')}"
                        st.session_state["active_voice_status"] = "fallback"
                    st.session_state["last_voice_audio_hash"] = audio_hash

            voice_content = st.session_state.get("active_voice_text", "").strip()

            st.markdown("---")
            st.markdown("##### 🎙️ Recorded Voice Note")
            
            # Show audio player
            st.audio(mic_audio)

            if st.session_state.get("active_voice_status") == "success":
                st.success(f"✨ **Transcribed Text:** \"{voice_content}\"")
            else:
                st.info(f"🎙️ **Recorded Audio Note:** \"{voice_content}\"")

            # Metadata settings
            col_vmeta1, col_vmeta2 = st.columns([2, 1])
            with col_vmeta1:
                default_voice_title = f"Voice Note - {datetime.utcnow().strftime('%b %d, %Y %H:%M')}"
                if voice_content and not voice_content.startswith("Voice note recording"):
                    words = voice_content.split()
                    default_voice_title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
                
                voice_title = st.text_input(
                    "Memory Title",
                    value=default_voice_title,
                    key="voice_direct_title_input"
                )
            with col_vmeta2:
                voice_cat = st.selectbox(
                    "Category",
                    options=["Auto-Detect (AI)", "Work", "Study", "Personal", "Health", "Finance", "General"],
                    key="voice_direct_cat_select"
                )

            col_vmeta3, col_vmeta4 = st.columns([1, 2])
            with col_vmeta3:
                voice_imp = st.slider("Importance Level", 1, 5, 3, key="voice_direct_imp_slider")
            with col_vmeta4:
                voice_tags = st.text_input(
                    "Custom Tags (optional, comma-separated)",
                    placeholder="e.g. voice-memo, meeting, ideas",
                    key="voice_direct_tags_input"
                )

            submit_voice = st.button("💾 Save Voice Memory to Vault", type="primary", use_container_width=True, key="save_voice_memory_btn")

            if submit_voice:
                with st.spinner("🧠 Analyzing, tagging, and indexing voice memory into your Vault..."):
                    ai_voice = process_memory(voice_content, title=voice_title)
                    final_cat = ai_voice["category"] if voice_cat == "Auto-Detect (AI)" else voice_cat

                    user_tags = [t.strip() for t in voice_tags.split(",") if t.strip()] if voice_tags else []
                    final_tags = list(set(ai_voice["tags"] + user_tags + ["voice", "audio"]))

                    MemoryRepository.create_memory(
                        user_id=user["id"],
                        title=voice_title.strip() or f"Voice Note - {datetime.utcnow().strftime('%b %d')}",
                        description=voice_content,
                        category=final_cat,
                        summary=ai_voice["summary"],
                        importance=voice_imp,
                        tags=final_tags
                    )

                st.session_state["active_voice_text"] = ""
                st.session_state["last_voice_audio_hash"] = None
                st.success("🎉 Voice memory recorded, transcribed, and saved to your Vault!")
                trigger_celebration_blast()
                st.rerun()
        else:
            st.info("👆 Click the red microphone button above, speak your memory, and click stop when you're done.")

    with tab_img:
        st.markdown("#### 🖼️ Image & Handwriting OCR Ingestion")
        st.caption("Upload whiteboards, handwritten study notes, certificates, or book page photos to extract text via OCR.")

        img_file = st.file_uploader("Upload Image (.png, .jpg, .jpeg, .webp)", type=["png", "jpg", "jpeg", "webp", "bmp"])
        
        if img_file is not None:
            img_bytes = img_file.getvalue()
            col_i_preview, col_i_meta = st.columns([1, 1])
            with col_i_preview:
                st.image(img_file, caption=f"Preview: {img_file.name}", use_container_width=True)
            
            with col_i_meta:
                img_title = st.text_input("Image Memory Title (Optional)", value=f"Image: {img_file.name}", placeholder="e.g. Whiteboard Architecture, Certificate...")
                col_ic1, col_ic2 = st.columns(2)
                with col_ic1:
                    img_cat_choice = st.selectbox("Category", options=["Auto-Detect (AI)", "Study", "Work", "Personal", "Health", "Finance", "General"], key="img_cat_sel")
                with col_ic2:
                    img_imp_level = st.slider("Importance", 1, 5, 3, key="img_imp_slider")
                img_custom_tags = st.text_input("Custom Tags (comma-separated, optional)", placeholder="e.g. diagram, lecture, python", key="img_tags_input")

            if st.button("🔍 Extract Text (OCR) & Save to Vault", type="primary", use_container_width=True):
                with st.spinner("Executing Optical Character Recognition (OCR) & Regex entity parser..."):
                    img_res = process_document(img_bytes, img_file.name, user["id"])

                if img_res.get("status") == "error":
                    st.error(f"OCR Extraction failed: {img_res.get('error_message')}")
                else:
                    meta = img_res.get("metadata", {})
                    extracted_txt = img_res.get("cleaned_text", "")
                    entities = img_res.get("extracted_entities", {})
                    content_for_ai = extracted_txt if len(extracted_txt.strip()) > 10 else f"{img_title or img_file.name}\nVisual Image Capture"

                    with st.spinner("Generating AI Summary and Domain Tags..."):
                        ai_img = process_memory(content_for_ai, title=img_title or img_file.name)

                    final_cat = ai_img["category"] if img_cat_choice == "Auto-Detect (AI)" else img_cat_choice
                    base_tags = [t.strip().lower() for t in img_custom_tags.split(",") if t.strip()] if img_custom_tags.strip() else ai_img["tags"]
                    final_tags = list(set(base_tags + ["image", "ocr"]))

                    saved_mem = MemoryRepository.create_memory(
                        user_id=user["id"],
                        title=img_title.strip() or f"Image: {img_file.name}",
                        description=extracted_txt[:5000] if extracted_txt.strip() else f"Image OCR: {img_file.name}",
                        category=final_cat,
                        summary=ai_img["summary"],
                        importance=img_imp_level,
                        tags=final_tags
                    )

                    st.success(f"🎉 OCR Completed! Memory '{img_title or img_file.name}' saved to Vault.")
                    
                    with st.expander("👁️ View Extracted OCR Text & Entities", expanded=True):
                        st.markdown(f"**OCR Engine Used:** `{meta.get('engine_used', 'OCR Engine')}` | **Dimensions:** `{meta.get('dimensions', 'N/A')}`")
                        st.text_area("Extracted Text Content", value=extracted_txt or "(No text detected in image)", height=140, disabled=True)
                        if any(entities.values()):
                            st.markdown("**Discovered Entities:**")
                            e_cols = st.columns(4)
                            with e_cols[0]: st.write("Dates:", entities.get("dates", []))
                            with e_cols[1]: st.write("Emails:", entities.get("emails", []))
                            with e_cols[2]: st.write("Phones:", entities.get("phone_numbers", []))
                            with e_cols[3]: st.write("Amounts:", entities.get("amounts", []))
                    st.balloons()
                    trigger_celebration_blast(balloons=False)

    with tab_url:
        st.markdown("#### 🌐 Web Article & YouTube Video Ingestion")
        st.caption("Paste any YouTube video link to extract its transcript, or a blog/webpage URL to scrape clean article text.")

        url_input = st.text_input("Website or YouTube URL", placeholder="e.g. https://www.youtube.com/watch?v=kqtD5dpn9C8 or https://en.wikipedia.org/wiki/Artificial_intelligence")

        if url_input.strip():
            is_yt = ("youtube.com" in url_input) or ("youtu.be" in url_input)
            col_u_title, col_u_cat = st.columns(2)
            with col_u_title:
                custom_url_title = st.text_input("Custom Memory Title (Optional)", placeholder="Leave blank to auto-detect title from page/video")
            with col_u_cat:
                url_cat_choice = st.selectbox("Category", options=["Auto-Detect (AI)", "Study", "Work", "Personal", "Health", "Finance", "General"], key="url_cat_sel")

            col_u_imp, col_u_tags = st.columns(2)
            with col_u_imp:
                url_imp_level = st.slider("Importance Level", 1, 5, 3, key="url_imp_slider")
            with col_u_tags:
                url_custom_tags = st.text_input("Custom Tags (comma-separated, optional)", placeholder="e.g. tutorial, python, youtube", key="url_tags_input")

            btn_label = "📺 Extract YouTube Transcript & Ingest" if is_yt else "🌐 Scrape Web Article & Ingest"
            if st.button(btn_label, type="primary", use_container_width=True):
                with st.spinner("Fetching content, parsing HTML / transcript & running AI pipeline..."):
                    url_res = process_url(url_input.strip(), user["id"])

                if url_res.get("status") == "error":
                    st.error(f"Failed to fetch content: {url_res.get('error_message')}")
                else:
                    meta = url_res.get("metadata", {})
                    cleaned_txt = url_res.get("cleaned_text", "")
                    entities = url_res.get("extracted_entities", {})
                    detected_title = meta.get("title") or ("YouTube Video" if is_yt else "Web Article")
                    final_title = custom_url_title.strip() or detected_title

                    with st.spinner("Generating AI Summary and Domain Tags..."):
                        ai_url = process_memory(cleaned_txt[:4000], title=final_title)

                    final_cat = ai_url["category"] if url_cat_choice == "Auto-Detect (AI)" else url_cat_choice
                    base_tags = [t.strip().lower() for t in url_custom_tags.split(",") if t.strip()] if url_custom_tags.strip() else ai_url["tags"]
                    source_tag = "youtube" if is_yt else "web_article"
                    final_tags = list(set(base_tags + [source_tag, "url_ingestion"]))

                    # Prepend source link to description for reference
                    full_desc = f"Source URL: {url_input.strip()}\nAuthor/Channel: {meta.get('author', 'N/A')}\n\n{cleaned_txt}"

                    saved_mem = MemoryRepository.create_memory(
                        user_id=user["id"],
                        title=final_title,
                        description=full_desc[:6000],
                        category=final_cat,
                        summary=ai_url["summary"],
                        importance=url_imp_level,
                        tags=final_tags
                    )

                    st.success(f"🎉 Successfully ingested '{final_title}' into your Vault!")
                    
                    if meta.get("thumbnail_url") and is_yt:
                        st.image(meta["thumbnail_url"], caption=final_title, width=320)

                    with st.expander("📄 View Extracted Content & AI Summary", expanded=True):
                        st.markdown(f"**Source:** [{url_input.strip()}]({url_input.strip()}) | **Word Count:** `{meta.get('word_count', 0)} words`")
                        st.markdown(f"**AI Summary:** {ai_url['summary']}")
                        st.text_area("Extracted Body / Transcript", value=cleaned_txt[:2000] + ("..." if len(cleaned_txt) > 2000 else ""), height=150, disabled=True)
                        if any(entities.values()):
                            st.markdown("**Discovered Entities:**")
                            e_cols = st.columns(4)
                            with e_cols[0]: st.write("Dates:", entities.get("dates", []))
                            with e_cols[1]: st.write("Emails:", entities.get("emails", []))
                            with e_cols[2]: st.write("Phones:", entities.get("phone_numbers", []))
                            with e_cols[3]: st.write("Amounts:", entities.get("amounts", []))
                    trigger_celebration_blast()


# -----------------------------------------------------------------------------
# 11. View: Ask My Memory (Conversational RAG Copilot)
# -----------------------------------------------------------------------------
def render_ask_memory(user: dict, memories: list[dict]):
    render_section_header(
        title="Ask My Memory & Intelligence Hub",
        subtitle="Conversational RAG copilot, multi-document comparative analysis, and synthesized audio voice briefings.",
        icon="🤖"
    )

    tab_chat, tab_compare, tab_podcast = st.tabs([
        "💬 Conversational RAG Copilot",
        "⚖️ Multi-Doc Comparative Analyzer",
        "🎙️ AI Audio Briefing & Podcast"
    ])

    # ---------------------------------------------------------
    # TAB 1: CONVERSATIONAL RAG COPILOT
    # ---------------------------------------------------------
    with tab_chat:
        col_filter1, col_filter2 = st.columns([3, 1])
        with col_filter1:
            scope_choice = st.selectbox(
                "🎯 Retrieval Scope",
                options=["All Categories", "Study", "Work", "Health", "Finance", "Personal", "General"],
                help="Filter knowledge retrieval to a specific memory domain."
            )
        with col_filter2:
            st.write("")
            st.write("")
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state["chat_messages"] = [
                    {"role": "assistant", "content": "Hello! I am your **Smart Memory Vault Copilot**. Ask me anything about your uploaded documents, study notes, YouTube videos, or projects!"}
                ]
                st.rerun()

        st.markdown("<p style='font-size: 0.8rem; color: #9CA3AF; margin-bottom: 6px;'>💡 Quick questions to try:</p>", unsafe_allow_html=True)
        q_col1, q_col2, q_col3 = st.columns(3)
        sample_to_run = None
        with q_col1:
            if st.button("💬 Summarize my latest project notes", use_container_width=True):
                sample_to_run = "Summarize my latest project notes"
        with q_col2:
            if st.button("💬 What key skills and technologies did I use?", use_container_width=True):
                sample_to_run = "What key skills and technologies did I use?"
        with q_col3:
            if st.button("💬 What are my key study concepts or formulas?", use_container_width=True):
                sample_to_run = "What are my key study concepts or formulas?"

        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("citations"):
                    with st.expander(f"📚 Verified Sources & Citations ({len(msg['citations'])})", expanded=False):
                        for cit in msg["citations"]:
                            st.markdown(f"**[{cit['citation_id']}] {cit['title']}** (`{cit['category']}`) — *Match: {cit['confidence']}*")
                            st.caption(f"> \"{cit['excerpt']}\"")

        chat_input = st.chat_input("Ask anything across your entire Vault...") or sample_to_run

        if chat_input:
            st.session_state["chat_messages"].append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            with st.chat_message("assistant"):
                with st.spinner("🧠 Performing semantic retrieval across vault chunks & synthesizing answer..."):
                    rag_res = rag_engine.chat(
                        query=chat_input,
                        memories=memories,
                        scope_category=None if scope_choice == "All Categories" else scope_choice
                    )

                    answer_text = rag_res["answer"]
                    citations = rag_res.get("citations", [])
                    conf = rag_res.get("confidence", 0)

                    st.markdown(answer_text)

                    if citations:
                        with st.expander(f"📚 Verified Sources & Citations ({len(citations)})", expanded=True):
                            st.markdown(f"**Overall Retrieval Confidence:** `{conf}% Match` | **Category Scope:** `{scope_choice}`")
                            for cit in citations:
                                st.markdown(f"**[{cit['citation_id']}] {cit['title']}** (`{cit['category']}`) — *Confidence: {cit['confidence']}*")
                                st.caption(f"> \"{cit['excerpt']}\"")

                    st.session_state["chat_messages"].append({
                        "role": "assistant",
                        "content": answer_text,
                        "citations": citations
                    })

    # ---------------------------------------------------------
    # TAB 2: MULTI-DOC COMPARATIVE ANALYZER
    # ---------------------------------------------------------
    with tab_compare:
        st.markdown("#### ⚖️ Cross-Document & Multi-Note Comparative Analysis")
        st.caption("Select any two documents or notes to generate an instant comparative synthesis matrix, shared concepts, and key distinctions.")

        if len(memories) < 2:
            st.info("You need at least 2 memories in your vault to perform comparative analysis.")
        else:
            doc_choices = {f"{m.get('title')} ({m.get('category')})": m for m in memories}
            keys = list(doc_choices.keys())

            col_doc_a, col_doc_b = st.columns(2)
            with col_doc_a:
                selected_a = st.selectbox("📄 Document / Memory A:", options=keys, index=0, key="comp_doc_a")
            with col_doc_b:
                selected_b = st.selectbox("📄 Document / Memory B:", options=keys, index=min(1, len(keys)-1), key="comp_doc_b")

            if st.button("⚡ Run Comparative Synthesis", type="primary", use_container_width=True):
                doc_a = doc_choices[selected_a]
                doc_b = doc_choices[selected_b]

                if doc_a.get("id") == doc_b.get("id"):
                    st.warning("Please choose two different memories or documents to compare.")
                else:
                    tags_a = set(t.lower() for t in (doc_a.get("tags") or []))
                    tags_b = set(t.lower() for t in (doc_b.get("tags") or []))
                    shared_tags = tags_a.intersection(tags_b)

                    words_a = set(re.findall(r'\b[a-zA-Z]{4,}\b', (doc_a.get("description", "") + " " + doc_a.get("summary", "")).lower()))
                    words_b = set(re.findall(r'\b[a-zA-Z]{4,}\b', (doc_b.get("description", "") + " " + doc_b.get("summary", "")).lower()))
                    shared_words = [w.title() for w in list(words_a.intersection(words_b)) if w not in quiz_engine.stop_words][:8]

                    st.markdown("---")
                    st.markdown("### 📊 Comparative Analysis Matrix")

                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.markdown(f"#### 📘 {doc_a.get('title')}")
                        st.markdown(f"**Category:** `{doc_a.get('category')}` | **Priority:** `{'⭐' * int(doc_a.get('importance', 1))}`")
                        st.markdown(f"**Summary:** {doc_a.get('summary') or doc_a.get('description', '')[:200]}")
                        st.markdown(f"**Unique Tags:** {', '.join(list(tags_a - tags_b)) or 'None'}")

                    with col_m2:
                        st.markdown(f"#### 📙 {doc_b.get('title')}")
                        st.markdown(f"**Category:** `{doc_b.get('category')}` | **Priority:** `{'⭐' * int(doc_b.get('importance', 1))}`")
                        st.markdown(f"**Summary:** {doc_b.get('summary') or doc_b.get('description', '')[:200]}")
                        st.markdown(f"**Unique Tags:** {', '.join(list(tags_b - tags_a)) or 'None'}")

                    st.markdown("#### 🔗 Synergies & Cross-Connections")
                    if shared_tags:
                        st.success(f"**Shared Knowledge Tags:** {', '.join(['#' + t for t in shared_tags])}")
                    if shared_words:
                        st.info(f"**Overlapping Domain Concepts:** {', '.join(shared_words)}")

                    st.markdown(f"""
                        <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 14px 18px; margin-top: 12px;">
                            <div style="font-weight: 700; color: #C7D2FE; margin-bottom: 4px;">🧠 AI Comparative Synthesis Takeaway:</div>
                            <div style="font-size: 0.9rem; color: #F1F5F9; line-height: 1.45;">
                                Combining <strong>{doc_a.get('title')}</strong> with <strong>{doc_b.get('title')}</strong> creates a comprehensive knowledge link bridging 
                                <em>{doc_a.get('category')}</em> and <em>{doc_b.get('category')}</em>.
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: AI AUDIO VOICE BRIEFING & PODCAST
    # ---------------------------------------------------------
    with tab_podcast:
        st.markdown("#### 🎙️ AI Voice Audio Briefing & Daily Podcast")
        st.caption("Generate and listen to real AI-narrated audio briefings of your vault notes, summaries, and key concepts.")

        if not memories:
            st.info("Add some notes to your vault to generate an audio briefing.")
        else:
            briefing_sources = ["⚡ Entire Vault Executive Digest"] + [f"{m.get('title')} ({m.get('category')})" for m in memories[:10]]
            selected_source = st.selectbox("Select Audio Topic:", options=briefing_sources, key="podcast_source_sel")

            if selected_source == "⚡ Entire Vault Executive Digest":
                briefing_script = f"Welcome back to your Smart Memory Vault executive audio briefing. You currently have {len(memories)} indexed records. "
                for idx, m in enumerate(memories[:4], 1):
                    summ = m.get("summary") or m.get("description", "")[:100]
                    briefing_script += f"Item {idx}: {m.get('title')}, classified under {m.get('category')}. Key takeaway: {summ}. "
                briefing_script += "Keep up your daily active recall and consistency streak!"
            else:
                mem_map = {f"{m.get('title')} ({m.get('category')})": m for m in memories}
                target_mem = mem_map.get(selected_source, memories[0])
                briefing_script = f"Audio briefing for {target_mem.get('title')}. Category: {target_mem.get('category')}. "
                briefing_script += f"Summary: {target_mem.get('summary') or target_mem.get('description', '')[:350]}. "

            st.text_area("🎙️ Spoken Script Preview:", value=briefing_script, height=110, disabled=True)

            col_btn1, col_btn2 = st.columns([1.5, 3.5])
            with col_btn1:
                gen_audio_btn = st.button("🎧 Synthesize Audio Podcast", type="primary", use_container_width=True)

            if gen_audio_btn or st.session_state.get(f"audio_ready_{selected_source}"):
                with st.spinner("🎙️ Synthesizing crystal-clear AI narration voice track..."):
                    try:
                        from gtts import gTTS
                        tts = gTTS(text=briefing_script, lang='en', slow=False)
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        audio_fp.seek(0)
                        audio_bytes = audio_fp.read()
                        st.session_state[f"audio_ready_{selected_source}"] = audio_bytes

                        st.success("✅ Audio Briefing ready! Hit Play below:")
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    except Exception as e:
                        st.warning(f"Using browser speech engine fallback...")
                        safe_script = briefing_script.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
                        tts_player_html = f"""
                            <div style="background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 14px; margin-top: 10px;">
                                <button onclick="window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance('{safe_script}'); window.speechSynthesis.speak(u);" style="background: #6366F1; color: white; border: none; padding: 8px 18px; border-radius: 8px; font-weight: 700; cursor: pointer;">
                                    ▶️ Play Browser Narration
                                </button>
                            </div>
                        """
                        components.html(tts_player_html, height=70)


# -----------------------------------------------------------------------------
# 12. View: Timeline View
# -----------------------------------------------------------------------------
def render_timeline(user: dict, memories: list[dict]):
    render_section_header(
        title="Chronological Timeline",
        subtitle="Visual progression of all memories, documents, and notes logged over time.",
        icon="🕒"
    )

    if not memories:
        st.info("No timeline data found. Create some memories to see the timeline.")
        return

    tab_vis, tab_graph = st.tabs(["📜 Visual Timeline Stream", "📈 Interactive Plotly Timeline"])

    with tab_vis:
        t_col1, _ = st.columns([2, 3])
        with t_col1:
            all_cats = ["All"] + sorted(list({m.get("category", "General") for m in memories}))
            sel_timeline_cat = st.selectbox("Filter Timeline Category", options=all_cats)

        t_mems = [m for m in memories if sel_timeline_cat == "All" or m.get("category") == sel_timeline_cat]
        t_mems.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        st.markdown('<div class="timeline-wrapper">', unsafe_allow_html=True)
        for m in t_mems:
            cat = m.get("category", "General")
            cat_color = get_color_for_category(cat)
            tags = m.get("tags") or []
            tags_html = " ".join([f"<span class='mem-tag-chip'>#{t}</span>" for t in tags[:3]])

            st.markdown(f"""
                <div class="timeline-node">
                    <div class="timeline-date-badge">📅 {m.get('created_at')}</div>
                    <div class="mem-card" style="margin-bottom: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #FFFFFF; font-size: 1.05rem;">{m.get('title')}</h4>
                            <span class="mem-cat-badge" style="background-color: {cat_color}; font-size: 0.75rem;">{cat}</span>
                        </div>
                        <div style="margin-top: 6px;">{tags_html}</div>
                        <p style="color: #9CA3AF; font-size: 0.85rem; margin: 6px 0 0 0;">
                            {m.get('summary')}
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_graph:
        fig_t = create_timeline_chart(memories)
        st.plotly_chart(fig_t, use_container_width=True)


# -----------------------------------------------------------------------------
# 13. View: Tags & Categorization
# -----------------------------------------------------------------------------
def render_tags(user: dict, memories: list[dict]):
    render_section_header(
        title="Tags & Topic Intelligence",
        subtitle="Explore memories organized by auto-extracted and custom topic tags.",
        icon="🏷️"
    )

    if not memories:
        st.info("No tags found.")
        return

    tag_counts = {}
    for m in memories:
        for t in m.get("tags", []):
            t_clean = t.strip().lower()
            if t_clean:
                tag_counts[t_clean] = tag_counts.get(t_clean, 0) + 1

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    c_chart, c_cloud = st.columns([1.2, 1.8])

    with c_chart:
        st.markdown("#### Top Keyword Tags")
        fig_tags = create_top_tags_chart(memories, top_n=8)
        st.plotly_chart(fig_tags, use_container_width=True)

    with c_cloud:
        st.markdown("#### Interactive Tag Directory")
        st.caption("Click any tag to filter memories below:")

        tag_cols = st.columns(4)
        for i, (t, count) in enumerate(sorted_tags):
            with tag_cols[i % 4]:
                if st.button(f"#{t} ({count})", key=f"tbtn_{t}", use_container_width=True):
                    st.session_state["filter_tag"] = t

        if st.session_state.get("filter_tag") != "All":
            active_t = st.session_state["filter_tag"]
            st.info(f"Filtering memories by tag: **#{active_t}**")
            if st.button("Reset Tag Filter"):
                st.session_state["filter_tag"] = "All"
                st.rerun()

            tagged_mems = [m for m in memories if active_t in [x.lower() for x in m.get("tags", [])]]
            for tm in tagged_mems:
                st.markdown(f"• **{tm.get('title')}** ({tm.get('category')}): {tm.get('summary')}")


# -----------------------------------------------------------------------------
# 14. View: Reminders & Priorities
# -----------------------------------------------------------------------------
def render_reminders(user: dict, memories: list[dict]):
    render_section_header(
        title="Reminders & Priority Alerts",
        subtitle="Track critical, high-priority, and time-sensitive knowledge items.",
        icon="⏰"
    )

    high_pri = [m for m in memories if int(m.get("importance", 1)) >= 4]

    st.markdown(f"#### 🚨 Critical & Urgent Memories ({len(high_pri)})")
    if not high_pri:
        st.success("✨ All clear! You have no urgent or critical priority memories flagged.")
    else:
        for m in high_pri:
            cat = m.get("category", "General")
            cat_color = get_color_for_category(cat)
            st.markdown(f"""
                <div class="mem-card" style="border-left: 4px solid #EF4444;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #FFFFFF;">{m.get('title')}</h4>
                        <div>
                            <span class="mem-cat-badge" style="background-color: {cat_color};">{cat}</span>
                            <span style="font-size: 0.9rem;">{'⭐' * int(m.get('importance', 1))}</span>
                        </div>
                    </div>
                    <p style="color: #E5E7EB; font-size: 0.9rem; margin: 8px 0;">{m.get('description')}</p>
                    <small style="color: #9CA3AF;">📅 Logged: {m.get('created_at')}</small>
                </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 15. View: Settings & Data Export Center
# -----------------------------------------------------------------------------
def render_settings(user: dict, memories: list[dict]):
    render_section_header(
        title="Vault Settings & Data Export Center",
        subtitle="Manage your security, download backups in multiple formats, or load demonstration data.",
        icon="⚙️"
    )

    stats = get_activity_summary(memories)

    tab_exp, tab_demo, tab_sec = st.tabs(["📄 Export Backups", "✨ Demo & Sample Data", "🔒 Security & Profile"])

    with tab_exp:
        st.markdown("#### Export Your Personal Knowledge Base")
        ec1, ec2, ec3 = st.columns(3)

        with ec1:
            st.markdown("##### 📄 PDF Executive Report")
            st.caption("Download formatted printable dossier with tables and stats.")
            pdf_bytes = generate_pdf_report(user, memories, stats)
            st.download_button(
                label="📥 Download PDF Dossier",
                data=pdf_bytes,
                file_name=f"vault_report_{user['username']}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        with ec2:
            st.markdown("##### 📊 CSV Spreadsheet")
            st.caption("Excel-compatible tabular export with all memory attributes.")
            csv_data = export_to_csv(memories)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"memories_{user['username']}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with ec3:
            st.markdown("##### 🗄️ JSON Archive")
            st.caption("Full machine-readable metadata archive for backup/restoration.")
            json_data = export_to_json(memories)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"memories_{user['username']}.json",
                mime="application/json",
                use_container_width=True
            )

    with tab_demo:
        st.markdown("#### Vault Data Management")
        st.caption("Manage demonstration data or completely wipe your vault to start 100% fresh.")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("🌟 Seed Blueprint Mockup Memories", use_container_width=True):
                seed_sample_data(user["id"])
                st.success("Blueprint sample memories loaded!")
                st.rerun()
        with col_d2:
            if st.button("🗑️ Wipe All Vault Memories", use_container_width=True, type="secondary"):
                MemoryRepository.delete_all_user_memories(user["id"])
                st.session_state["selected_memory_id"] = None
                st.warning("All memories have been wiped from your vault. You have a completely clean workspace!")
                st.rerun()

    with tab_sec:
        st.markdown("#### Security & Encryption Status")
        st.info("🔐 **Encryption Status**: Active. Passwords hashed using bcrypt. Database sanitized against SQL injection.")
        st.markdown(f"• **Active User:** `{user['username']}`")
        st.markdown(f"• **Email:** `{user['email']}`")
        st.markdown(f"• **Total Stored Records:** `{len(memories)}`")


# -----------------------------------------------------------------------------
# 16. Main Application Controller
# -----------------------------------------------------------------------------
def main():
    user = st.session_state.get("user")

    if not user:
        render_auth_view()
        return

    # Fetch fresh user memories from repository
    memories = MemoryRepository.get_user_memories(user["id"])

    # Render Sidebar
    render_sidebar(user, memories)

    # Route navigation
    nav = st.session_state.get("current_nav", "Dashboard")

    if nav == "Dashboard":
        render_dashboard(user, memories)
    elif nav == "All Memories":
        render_all_memories(user, memories)
    elif nav == "Add Memory":
        render_add_memory(user)
    elif nav == "Study & Quiz":
        render_study_quiz(user, memories)
    elif nav == "Knowledge Graph":
        render_knowledge_graph_view(user, memories)
    elif nav == "Tags":
        render_tags(user, memories)
    elif nav == "Timeline":
        render_timeline(user, memories)
    elif nav == "Ask My Memory":
        render_ask_memory(user, memories)
    elif nav == "Reminders":
        render_reminders(user, memories)
    elif nav == "Settings":
        render_settings(user, memories)
    else:
        render_dashboard(user, memories)


if __name__ == "__main__":
    main()
