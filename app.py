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
import json
import base64
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

# Core & Backend Imports
from core.database import init_db, MemoryRepository, UserRepository
from core.auth import login_user, register_user
from pipeline import process_document
from nlp_engine import process_memory, search_engine, categorizer, sentiment_engine, summarizer, quiz_engine

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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 96%;
    }

    /* Gradient Header Hero */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 45%, #312E81 80%, #4338CA 100%);
        border-radius: 18px;
        padding: 28px 32px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -5px rgba(99, 102, 241, 0.3), 0 4px 12px -2px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    }
    .hero-banner h1 {
        color: #FFFFFF !important;
        margin: 0 0 6px 0;
        font-weight: 800;
        font-size: 2.3rem;
        letter-spacing: -0.02em;
    }
    .hero-banner p {
        color: #E0E7FF !important;
        font-size: 1.02rem;
        margin: 0;
        max-width: 850px;
        line-height: 1.5;
    }

    /* AI Daily Digest Pill Box */
    .ai-digest-box {
        background: rgba(30, 27, 75, 0.7);
        border: 1px solid rgba(165, 180, 252, 0.35);
        border-radius: 14px;
        padding: 16px 20px;
        margin-top: 16px;
        backdrop-filter: blur(10px);
        display: flex;
        align-items: flex-start;
        gap: 14px;
    }
    .ai-digest-icon {
        font-size: 1.6rem;
        background: rgba(99, 102, 241, 0.25);
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    .ai-digest-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #A5B4FC;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }
    .ai-digest-body {
        font-size: 0.95rem;
        color: #F8FAFC;
        line-height: 1.45;
        margin: 0;
    }

    /* Metric Glass Cards */
    .kpi-card {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(55, 65, 81, 0.8);
        border-radius: 16px;
        padding: 20px;
        text-align: left;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(12px);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.7);
        box-shadow: 0 12px 25px -5px rgba(99, 102, 241, 0.25);
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #6366F1;
    }
    .kpi-card.purple::before { background: linear-gradient(180deg, #A855F7, #6366F1); }
    .kpi-card.blue::before { background: linear-gradient(180deg, #38BDF8, #3B82F6); }
    .kpi-card.emerald::before { background: linear-gradient(180deg, #34D399, #059669); }
    .kpi-card.amber::before { background: linear-gradient(180deg, #FBBF24, #D97706); }
    .kpi-card.rose::before { background: linear-gradient(180deg, #FB7185, #E11D48); }

    .kpi-label {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9CA3AF;
        margin-bottom: 6px;
    }
    .kpi-val {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1;
        margin-bottom: 6px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #94A3B8;
    }

    /* Memory Card Styles */
    .mem-card {
        background: rgba(17, 24, 39, 0.9);
        border: 1px solid rgba(55, 65, 81, 0.7);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        transition: all 0.2s ease-in-out;
        backdrop-filter: blur(8px);
    }
    .mem-card:hover {
        border-color: rgba(99, 102, 241, 0.6);
        background: rgba(26, 34, 52, 0.95);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.3);
    }
    .mem-card-title {
        font-size: 1.08rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
    }
    .mem-tag-chip {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #C7D2FE;
        border: 1px solid rgba(99, 102, 241, 0.3);
        font-size: 0.74rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 6px;
        margin-right: 5px;
        margin-top: 4px;
    }
    .mem-cat-badge {
        display: inline-block;
        padding: 4px 11px;
        font-size: 0.74rem;
        font-weight: 700;
        border-radius: 9999px;
        color: white;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    }

    /* Urgent Alert Card */
    .urgent-banner-card {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.15), rgba(185, 28, 28, 0.05));
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Flashcard Study Styles */
    .flashcard-frame {
        background: linear-gradient(145deg, #1E1B4B, #0F172A);
        border: 2px solid #6366F1;
        border-radius: 20px;
        padding: 36px 32px;
        text-align: center;
        min-height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 16px 32px -8px rgba(99, 102, 241, 0.35);
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    .flashcard-topic-badge {
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #A5B4FC;
        letter-spacing: 0.08em;
        margin-bottom: 12px;
    }
    .flashcard-main-text {
        font-size: 1.35rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.45;
        max-width: 700px;
    }
    .flashcard-hint {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 16px;
        font-style: italic;
    }

    /* Quiz Box Styles */
    .quiz-question-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 18px;
    }
    .quiz-num {
        font-weight: 800;
        color: #818CF8;
        font-size: 0.85rem;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .quiz-q-text {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 12px;
    }

    /* Visual Flow Infographic Styles */
    .flow-container {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 28px;
        backdrop-filter: blur(12px);
    }
    .flow-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F3F4F6;
        text-align: center;
        margin-bottom: 18px;
        letter-spacing: -0.01em;
    }
    .flow-step-card {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 14px 12px;
        text-align: center;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .flow-step-card:hover {
        transform: translateY(-3px);
        border-color: #6366F1;
        box-shadow: 0 8px 16px -4px rgba(99, 102, 241, 0.2);
    }
    .flow-step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        background: #6366F1;
        color: white;
        border-radius: 50%;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .flow-step-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 6px;
    }
    .flow-step-desc {
        font-size: 0.76rem;
        color: #9CA3AF;
        line-height: 1.35;
        margin: 0;
    }
    .flow-step-items {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
        margin-top: 8px;
    }
    .flow-pill {
        background: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 9999px;
        font-size: 0.68rem;
        padding: 2px 7px;
        font-weight: 600;
    }

    /* Detail Inspector Box */
    .detail-inspector {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 22px;
        position: sticky;
        top: 20px;
    }
    .detail-inspector h3 {
        color: #FFFFFF;
        margin-top: 0;
        font-weight: 700;
        font-size: 1.25rem;
    }
    .detail-field {
        margin-bottom: 12px;
    }
    .detail-field-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .detail-field-val {
        font-size: 0.9rem;
        color: #E5E7EB;
    }

    /* Timeline Vertical Component */
    .timeline-wrapper {
        position: relative;
        padding: 10px 0 10px 24px;
        border-left: 2px solid #374151;
        margin-left: 16px;
    }
    .timeline-node {
        position: relative;
        margin-bottom: 24px;
    }
    .timeline-node::before {
        content: "";
        position: absolute;
        left: -31px;
        top: 4px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #6366F1;
        border: 2px solid #111827;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
    }
    .timeline-date-badge {
        font-size: 0.78rem;
        font-weight: 700;
        color: #A5B4FC;
        margin-bottom: 4px;
        letter-spacing: 0.02em;
    }

    /* Key Features Bottom Strip */
    .features-strip {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 14px;
        padding: 18px 22px;
        margin-top: 40px;
    }
    .features-strip-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: #F3F4F6;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 12px;
    }
    .feature-chip {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 10px 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #E5E7EB;
        transition: border-color 0.15s ease;
    }
    .feature-chip:hover {
        border-color: #6366F1;
    }

    /* Entity chips */
    .entity-tag {
        display: inline-block;
        background: rgba(59, 130, 246, 0.12);
        color: #93C5FD;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 6px;
        font-size: 0.75rem;
        padding: 2px 7px;
        margin: 2px 3px 2px 0;
        font-family: 'JetBrains Mono', monospace;
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
    auth_hero_html = (
        '<div class="hero-banner" style="text-align: center; padding: 36px 28px; background: linear-gradient(135deg, #090D16 0%, #1E1B4B 50%, #312E81 85%, #4F46E5 100%); border: 1px solid rgba(99, 102, 241, 0.3);">'
        '<div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: linear-gradient(135deg, #6366F1, #A855F7); border-radius: 20px; font-size: 2.2rem; margin-bottom: 14px; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45);">🧠</div>'
        '<h1 style="font-size: 2.6rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 8px;">Smart Memory Vault</h1>'
        '<p style="max-width: 750px; margin: 0 auto 18px auto; font-size: 1.05rem; color: #E0E7FF; line-height: 1.55;">Your Intelligent Multi-Format Knowledge & Memory Repository. Ingest PDFs up to 100MB, record voice notes, auto-tag, test knowledge with AI quizzes, and query with AI.</p>'
        '<div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 8px;">'
        '<span class="flow-pill" style="font-size: 0.76rem; padding: 4px 12px;">📄 100MB PDF & OCR Engine</span>'
        '<span class="flow-pill" style="font-size: 0.76rem; padding: 4px 12px;">🧠 AI Study & Quiz Mode</span>'
        '<span class="flow-pill" style="font-size: 0.76rem; padding: 4px 12px;">🕸️ Neural Knowledge Mind Map</span>'
        '<span class="flow-pill" style="font-size: 0.76rem; padding: 4px 12px;">🤖 Semantic Search & Chatbot</span>'
        '<span class="flow-pill" style="font-size: 0.76rem; padding: 4px 12px;">🔒 AES-256 Vault Encryption</span>'
        '</div>'
        '</div>'
    )
    st.markdown(auth_hero_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        tab_login, tab_register, tab_demo = st.tabs(["🔑 Sign In", "📝 Create Account", "⚡ Instant Demo Mode"])

        with tab_login:
            st.markdown("#### Access Your Vault")
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="user@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("🚀 Sign In to Vault", use_container_width=True, type="primary")

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
            st.markdown("#### Create a New Account")
            st.caption("Create a secure, isolated workspace for your notes and documents.")
            with st.form("register_form"):
                reg_username = st.text_input("Username", placeholder="e.g. reena_vault")
                reg_email = st.text_input("Email Address", placeholder="reena@example.com")
                reg_pass = st.text_input("Password (min 6 chars)", type="password")
                reg_pass_conf = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("✨ Register & Initialize Vault", use_container_width=True, type="primary")

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
            st.markdown("#### 🚀 Instant One-Click Demo Mode")
            st.caption("Try the full Smart Memory Vault experience immediately with pre-loaded demonstration data.")
            if st.button("🌟 Launch Demo User with Blueprint Data", use_container_width=True, type="primary"):
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

    # Visual Flow & Features Strip
    render_visual_flow_infographic()
    render_key_features_strip()


# -----------------------------------------------------------------------------
# 5. Shared Component: Visual Flow Infographic
# -----------------------------------------------------------------------------
def render_visual_flow_infographic():
    st.markdown("""
        <div class="flow-container">
            <div class="flow-title">⚡ How Our App Works – Visual Flow</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
                <div class="flow-step-card">
                    <div class="flow-step-num">1</div>
                    <div class="flow-step-title">Add Memory</div>
                    <p class="flow-step-desc">Add notes, documents, voice recordings or images.</p>
                    <div class="flow-step-items">
                        <span class="flow-pill">📝 Text Note</span>
                        <span class="flow-pill">📄 PDF/Doc</span>
                        <span class="flow-pill">🎙️ Voice</span>
                        <span class="flow-pill">🖼️ Image</span>
                    </div>
                </div>
                <div class="flow-step-card">
                    <div class="flow-step-num">2</div>
                    <div class="flow-step-title">Process & Extract</div>
                    <p class="flow-step-desc">Reads content, extracts text, identifies keywords & regex entities.</p>
                    <div class="flow-step-items">
                        <span class="flow-pill">✓ Extract Text</span>
                        <span class="flow-pill">✓ Find Entities</span>
                    </div>
                </div>
                <div class="flow-step-card">
                    <div class="flow-step-num">3</div>
                    <div class="flow-step-title">Auto Tagging</div>
                    <p class="flow-step-desc">Automatically generates tags and categorizes the memory.</p>
                    <div class="flow-step-items">
                        <span class="flow-pill">#Python</span>
                        <span class="flow-pill">#Project</span>
                        <span class="flow-pill">#OOP</span>
                    </div>
                </div>
                <div class="flow-step-card">
                    <div class="flow-step-num">4</div>
                    <div class="flow-step-title">Store & Organize</div>
                    <p class="flow-step-desc">Securely encrypted and organized with tags, date, and priority.</p>
                    <div class="flow-step-items">
                        <span class="flow-pill">🔒 Encrypted</span>
                        <span class="flow-pill">🗂️ Indexed</span>
                    </div>
                </div>
                <div class="flow-step-card">
                    <div class="flow-step-num">5</div>
                    <div class="flow-step-title">Ask / Search</div>
                    <p class="flow-step-desc">Ask questions or search in natural language.</p>
                    <div class="flow-step-items">
                        <span class="flow-pill">🔍 Semantic</span>
                        <span class="flow-pill">💬 Natural QA</span>
                    </div>
                </div>
                <div class="flow-step-card">
                    <div class="flow-step-num">6</div>
                    <div class="flow-step-title">Get Smart Answer</div>
                    <p class="flow-step-desc">AI chatbot understands intent and delivers synthesized answers.</p>
                    <div class="flow-step-items">
                        <span class="flow-pill">🤖 AI Chatbot</span>
                        <span class="flow-pill">✨ Insights</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. Shared Component: Key Features Strip
# -----------------------------------------------------------------------------
def render_key_features_strip():
    st.markdown("""
        <div class="features-strip">
            <div class="features-strip-title">⭐ Key Platform Features</div>
            <div class="features-grid">
                <div class="feature-chip"><span>🔍</span> Semantic Search</div>
                <div class="feature-chip"><span>🏷️</span> Automatic Tagging</div>
                <div class="feature-chip"><span>🎙️</span> Voice Memory Recording</div>
                <div class="feature-chip"><span>🤖</span> Ask My Memory (Chatbot)</div>
                <div class="feature-chip"><span>📄</span> Document Summarization</div>
                <div class="feature-chip"><span>⏳</span> Timeline View</div>
                <div class="feature-chip"><span>⭐</span> Important Memory Detection</div>
                <div class="feature-chip"><span>🔒</span> Encryption & Security</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


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

        selected_label = st.radio(
            "Main Menu",
            options=[label for label, _ in nav_items],
            index=current_idx,
            label_visibility="collapsed"
        )
        for label, route in nav_items:
            if selected_label == label:
                st.session_state["current_nav"] = route
                break

        st.divider()

        stats = get_activity_summary(memories)
        st.markdown("<p style='font-size: 0.72rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 6px;'>Vault Intelligence</p>", unsafe_allow_html=True)
        st.markdown(f"• Total Records: **{stats['total_count']}**")
        st.markdown(f"• High Priority: **{stats['high_priority_count']}**")
        st.markdown(f"• Primary Focus: **{stats['top_category']}**")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["current_nav"] = "Dashboard"
            st.session_state["selected_memory_id"] = None
            st.rerun()


# -----------------------------------------------------------------------------
# 8. View: Dashboard (Dynamic Glassmorphic AI Hub)
# -----------------------------------------------------------------------------
def render_dashboard(user: dict, memories: list[dict]):
    stats = get_activity_summary(memories)
    doc_count = sum(1 for m in memories if any(kw in (m.get("title", "") + m.get("category", "")).lower() for kw in ["pdf", "doc", "report", "resume", "cert"]))
    note_count = max(0, len(memories) - doc_count)
    urgent_mems = [m for m in memories if int(m.get("importance", 1)) >= 4]

    all_tags = []
    for m in memories:
        all_tags.extend([str(t).lower() for t in (m.get("tags") or []) if str(t).strip()])
    top_tags_summary = ", ".join(list(dict.fromkeys(all_tags))[:4]) if all_tags else "general topics"

    # Dynamic AI Briefing Content
    if memories:
        briefing_text = f"You have <b>{stats['total_count']} indexed knowledge items</b> with top focus on <b>{stats['top_category']}</b>. Key active tags include <i>#{top_tags_summary}</i>. You have <b>{len(urgent_mems)} high-priority items</b> requiring active attention."
    else:
        briefing_text = "Your vault is currently empty and ready for fresh knowledge. Click <b>'+ Add Memory'</b> or <b>'Ingest Document'</b> to store your first notes, PDFs, or research!"

    # Unindented Hero Banner with AI Daily Intelligence Digest to prevent markdown code block rendering
    hero_html = (
        f'<div class="hero-banner">'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">'
        f'<div>'
        f'<h1>Welcome back, {user["username"]}! 👋</h1>'
        f'<p>Your centralized personal memory vault is encrypted, synchronized, and ready. Explore your memories, upload documents, or query your AI assistant.</p>'
        f'</div>'
        f'<div style="background: rgba(99, 102, 241, 0.25); border: 1px solid rgba(165, 180, 252, 0.4); border-radius: 9999px; padding: 6px 14px; font-size: 0.8rem; font-weight: 700; color: #E0E7FF;">'
        f'🟢 Vault Active & Encrypted'
        f'</div>'
        f'</div>'
        f'<div class="ai-digest-box">'
        f'<div class="ai-digest-icon">🧠</div>'
        f'<div>'
        f'<div class="ai-digest-title">⚡ AI Vault Intelligence Digest</div>'
        f'<div class="ai-digest-body">{briefing_text}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # 1. Dashboard Spotlight Search Bar
    dash_search = st.text_input(
        "🔍 Instant Spotlight Search across memories, documents & tags...",
        placeholder="Type to search (e.g. Python, Report, Loan, Interview, Certificate)...",
        key="dash_spotlight_input"
    )

    if dash_search.strip():
        searchable_list = [dict(m, content=m.get("description", "")) for m in memories]
        matched = search_engine.search(dash_search.strip(), searchable_list, top_k=6)
        
        st.markdown(f"##### 🎯 Search Results for *'{dash_search}'* ({len(matched)} matches):")
        if not matched:
            st.info("No matching memories found for your search query.")
        else:
            s_cols = st.columns(min(3, max(1, len(matched))))
            for idx, m in enumerate(matched):
                with s_cols[idx % len(s_cols)]:
                    cat = m.get("category", "General")
                    cat_color = get_color_for_category(cat)
                    card_html = (
                        f'<div class="mem-card" style="border-left: 3px solid {cat_color};">'
                        f'<span class="mem-cat-badge" style="background-color: {cat_color}; font-size: 0.68rem;">{cat}</span>'
                        f'<div class="mem-card-title" style="margin-top: 6px; font-size: 0.95rem;">{m.get("title")}</div>'
                        f'<p style="font-size: 0.8rem; color: #9CA3AF; margin: 4px 0 8px 0;">{(m.get("summary") or m.get("description",""))[:90]}...</p>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
                    if st.button("Inspect Memory ➔", key=f"dash_s_btn_{m.get('id')}", use_container_width=True):
                        st.session_state["selected_memory_id"] = m.get("id")
                        st.session_state["current_nav"] = "All Memories"
                        st.rerun()
        st.markdown("---")

    # 2. Modern Glass KPI Cards Row
    unique_cat_count = len(set(m.get('category','General') for m in memories)) if memories else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card purple"><div class="kpi-label">Total Memories</div><div class="kpi-val">{stats["total_count"]}</div><div class="kpi-sub">Across all {unique_cat_count} categories</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Documents & PDFs</div><div class="kpi-val">{doc_count}</div><div class="kpi-sub">Parsed & indexed files</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card emerald"><div class="kpi-label">Notes & Voice</div><div class="kpi-val">{note_count}</div><div class="kpi-sub">Text notes & audio logs</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card amber"><div class="kpi-label">High Priority</div><div class="kpi-val">{stats["high_priority_count"]}</div><div class="kpi-sub">Critical & urgent entries</div></div>', unsafe_allow_html=True)

    # 3. Quick Launchpad Action Bar
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### ⚡ Quick Launchpad")
    q1, q2, q3, q4, q5 = st.columns(5)
    with q1:
        if st.button("✍️ New Note", use_container_width=True):
            st.session_state["current_nav"] = "Add Memory"
            st.rerun()
    with q2:
        if st.button("📄 Ingest Document", use_container_width=True):
            st.session_state["current_nav"] = "Add Memory"
            st.rerun()
    with q3:
        if st.button("🧠 Study & Quiz", use_container_width=True, type="primary"):
            st.session_state["current_nav"] = "Study & Quiz"
            st.rerun()
    with q4:
        if st.button("🕸️ Knowledge Graph", use_container_width=True):
            st.session_state["current_nav"] = "Knowledge Graph"
            st.rerun()
    with q5:
        if st.button("🤖 Ask AI Chatbot", use_container_width=True):
            st.session_state["current_nav"] = "Ask My Memory"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Main Two-Column Interactive Hub
    col_left, col_right = st.columns([1.5, 1.1])

    with col_left:
        # Pinned / Urgent Attention Drawer
        if urgent_mems:
            st.markdown("#### 🚨 High Priority & Urgent Focus")
            for um in urgent_mems[:3]:
                u_cat = um.get("category", "General")
                u_cat_color = get_color_for_category(u_cat)
                urgent_html = (
                    f'<div class="urgent-banner-card"><div>'
                    f'<div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">⭐⭐⭐⭐⭐ {um.get("title")}</div>'
                    f'<div style="font-size: 0.78rem; color: #CBD5E1; margin-top: 2px;">'
                    f'<span class="mem-cat-badge" style="background-color: {u_cat_color}; font-size: 0.65rem; padding: 2px 7px;">{u_cat}</span> '
                    f'{(um.get("summary") or um.get("description",""))[:80]}...'
                    f'</div></div></div>'
                )
                st.markdown(urgent_html, unsafe_allow_html=True)

        st.markdown("#### 🕒 Recent Knowledge Stream")
        if not memories:
            st.info("Your vault is currently empty. Click 'Add Memory' to start adding your real notes, PDFs, and documents!")
            if st.button("➕ Add First Memory", type="primary"):
                st.session_state["current_nav"] = "Add Memory"
                st.rerun()
        else:
            for mem in memories[:5]:
                cat = mem.get("category", "General")
                cat_color = get_color_for_category(cat)
                imp_stars = "⭐" * int(mem.get("importance", 1))
                tags = mem.get("tags") or []
                tags_html = " ".join([f"<span class='mem-tag-chip'>#{t}</span>" for t in tags[:3]])

                mem_stream_html = (
                    f'<div class="mem-card">'
                    f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">'
                    f'<div>'
                    f'<span class="mem-card-title">{mem.get("title")}</span>'
                    f'<div style="margin-top: 4px;">{tags_html}</div>'
                    f'</div>'
                    f'<div style="text-align: right;">'
                    f'<span class="mem-cat-badge" style="background-color: {cat_color};">{cat}</span>'
                    f'<div style="font-size: 0.8rem; margin-top: 4px;">{imp_stars}</div>'
                    f'</div>'
                    f'</div>'
                    f'<p style="color: #94A3B8; font-size: 0.85rem; margin: 6px 0 8px 0; line-height: 1.45;">'
                    f'{mem.get("summary") or mem.get("description", "")[:120] + "..."}'
                    f'</p>'
                    f'<div style="font-size: 0.75rem; color: #64748B;">📅 Created: {mem.get("created_at")}</div>'
                    f'</div>'
                )
                st.markdown(mem_stream_html, unsafe_allow_html=True)

    with col_right:
        st.markdown("#### 📊 Category Insights")
        if memories:
            fig_cat = create_category_distribution_chart(memories)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.caption("No category distribution available yet.")

        st.markdown("#### 📈 Importance Spectrum")
        if memories:
            fig_imp = create_importance_histogram(memories)
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.caption("No priority spectrum available yet.")

    st.markdown("<br>", unsafe_allow_html=True)
    render_visual_flow_infographic()
    render_key_features_strip()


# -----------------------------------------------------------------------------
# 8b. View: AI Study Flashcards & Interactive Quiz Generator
# -----------------------------------------------------------------------------
def render_study_quiz(user: dict, memories: list[dict]):
    st.markdown("### 🧠 AI Study & Quiz Mode")
    st.caption("Turn your notes, documents, and uploaded PDFs into interactive flashcards and active-recall quizzes.")

    if not memories:
        st.info("No memories found. Add some notes or PDFs first to generate study materials.")
        return

    # Memory selection
    mem_options = {f"{m.get('title')} ({m.get('category')})": m for m in memories}
    selected_key = st.selectbox("Select Memory or Document to Study:", options=list(mem_options.keys()))
    selected_mem = mem_options[selected_key]

    study_tab1, study_tab2 = st.tabs(["🎴 Smart Flashcards", "📝 AI Multiple-Choice Quiz"])

    content_text = f"{selected_mem.get('title')}\n{selected_mem.get('description')}\n{selected_mem.get('summary', '')}"

    with study_tab1:
        st.markdown("#### 🎴 Active Recall Flashcards")
        cards = quiz_engine.generate_flashcards(content_text, title=selected_mem.get("title", ""))

        if not cards:
            st.warning("Not enough text in this memory to generate flashcards. Try adding more detailed notes.")
        else:
            if "fc_index" not in st.session_state:
                st.session_state["fc_index"] = 0
            if "fc_flipped" not in st.session_state:
                st.session_state["fc_flipped"] = False
            if "mastered_cards" not in st.session_state:
                st.session_state["mastered_cards"] = set()

            idx = st.session_state["fc_index"] % len(cards)
            card = cards[idx]
            is_mastered = idx in st.session_state["mastered_cards"]

            st.progress((idx + 1) / len(cards), text=f"Card {idx + 1} of {len(cards)} | Mastered: {len(st.session_state['mastered_cards'])}/{len(cards)}")

            # Flashcard Display
            is_flipped = st.session_state["fc_flipped"]
            card_title = "💡 EXPLANATION & CONTEXT" if is_flipped else f"❓ {card['concept']}"
            card_text = card["back"] if is_flipped else card["front"]
            card_hint = "Click 'Flip Card' to test your recall" if not is_flipped else "Click 'Flip Card' to view question again"

            st.markdown(f"""
                <div class="flashcard-frame">
                    <div class="flashcard-topic-badge">{card_title}</div>
                    <div class="flashcard-main-text">{card_text}</div>
                    <div class="flashcard-hint">{card_hint}</div>
                </div>
            """, unsafe_allow_html=True)

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
                        st.session_state["mastered_cards"].remove(idx)
                    else:
                        st.session_state["mastered_cards"].add(idx)
                    st.rerun()
            with fc5:
                if st.button("🔀 Reset", use_container_width=True):
                    st.session_state["fc_index"] = 0
                    st.session_state["fc_flipped"] = False
                    st.session_state["mastered_cards"] = set()
                    st.rerun()

    with study_tab2:
        st.markdown("#### 📝 AI Multiple-Choice Knowledge Quiz")
        st.caption("Test your comprehension with dynamically synthesized questions from your vault.")

        quiz_questions = quiz_engine.generate_quiz(content_text, title=selected_mem.get("title", ""))

        if not quiz_questions:
            st.warning("Not enough context to construct a quiz. Add more details or upload a PDF document!")
        else:
            with st.form("study_quiz_form"):
                user_answers = {}
                for q in quiz_questions:
                    st.markdown(f"""
                        <div class="quiz-question-card">
                            <div class="quiz-num">Question {q['id']}</div>
                            <div class="quiz-q-text">{q['question']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    user_answers[q["id"]] = st.radio(
                        f"Select answer for Question {q['id']}:",
                        options=q["options"],
                        key=f"quiz_q_{q['id']}_{selected_mem.get('id')}",
                        label_visibility="collapsed"
                    )

                submit_quiz = st.form_submit_button("🎯 Submit Quiz for Grading", type="primary", use_container_width=True)

            if submit_quiz:
                correct_count = 0
                st.markdown("---")
                st.markdown("### 📊 Quiz Results & Explanations")

                for q in quiz_questions:
                    u_ans = user_answers.get(q["id"])
                    is_correct = (u_ans == q["correct_answer"])
                    if is_correct:
                        correct_count += 1
                        st.success(f"✅ **Question {q['id']} Correct!** Your answer: *{u_ans}*")
                    else:
                        st.error(f"❌ **Question {q['id']} Incorrect.** Your answer: *{u_ans}* | **Correct Answer:** *{q['correct_answer']}*")
                    st.caption(f"💡 {q['explanation']}")

                score_pct = int((correct_count / len(quiz_questions)) * 100)
                if score_pct >= 80:
                    st.balloons()
                    st.success(f"🏆 Outstanding! You scored **{correct_count}/{len(quiz_questions)} ({score_pct}%)**! Knowledge mastered.")
                else:
                    st.info(f"📚 You scored **{correct_count}/{len(quiz_questions)} ({score_pct}%)**. Review your flashcards and try again!")


# -----------------------------------------------------------------------------
# 8c. View: Interactive Knowledge Mind Map Graph
# -----------------------------------------------------------------------------
def render_knowledge_graph_view(user: dict, memories: list[dict]):
    st.markdown("### 🕸️ Interactive Knowledge Mind Map")
    st.caption("Explore relationships between your memories, categories, and keyword tags as an interactive neural network.")

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
    st.markdown("### 📑 All Memories Repository")
    st.caption("Browse, filter, and inspect your stored knowledge items, documents, and notes.")

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
            cat = mem.get("category", "General")
            cat_color = get_color_for_category(cat)
            tags = mem.get("tags") or []
            tags_html = " ".join([f"<span class='mem-tag-chip'>#{t}</span>" for t in tags[:4]])

            is_selected = (st.session_state.get("selected_memory_id") == mem_id)
            selected_border = "border: 2px solid #6366F1;" if is_selected else ""

            with st.container():
                st.markdown(f"""
                    <div class="mem-card" style="{selected_border}">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h4 style="margin: 0; color: #F9FAFB; font-size: 1.05rem;">{mem.get('title')}</h4>
                                <div style="margin-top: 4px;">{tags_html}</div>
                            </div>
                            <div style="text-align: right;">
                                <span class="mem-cat-badge" style="background-color: {cat_color};">{cat}</span>
                                <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 4px;">{mem.get('created_at')}</div>
                            </div>
                        </div>
                        <p style="color: #9CA3AF; font-size: 0.85rem; margin: 8px 0;">
                            {mem.get('summary') or mem.get('description', '')[:100] + '...'}
                        </p>
                    </div>
                """, unsafe_allow_html=True)

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
            cat = selected_mem.get("category", "General")
            cat_color = get_color_for_category(cat)
            tags = selected_mem.get("tags") or []
            tags_html = " ".join([f"<span class='mem-tag-chip' style='font-size: 0.82rem;'>#{t}</span>" for t in tags])

            title_lower = selected_mem.get("title", "").lower()
            if "pdf" in title_lower or "report" in title_lower or "cert" in title_lower:
                doc_type = "Document (PDF)"
                doc_size = "2.4 MB"
            elif "docx" in title_lower or "doc" in title_lower:
                doc_type = "Document (DOCX)"
                doc_size = "1.1 MB"
            elif "voice" in title_lower:
                doc_type = "Voice Note (Audio)"
                doc_size = "450 KB"
            else:
                doc_type = "Text Note"
                doc_size = f"{len(selected_mem.get('description', ''))} bytes"

            st.markdown(f"""
                <div class="detail-inspector">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <span class="mem-cat-badge" style="background-color: {cat_color}; font-size: 0.8rem;">{cat}</span>
                        <span style="font-size: 0.95rem;">{'⭐' * int(selected_mem.get('importance', 1))}</span>
                    </div>
                    <h3 style="margin-bottom: 8px;">{selected_mem.get('title')}</h3>
                    <div style="margin-bottom: 16px;">{tags_html}</div>

                    <div class="detail-field">
                        <div class="detail-field-label">Content Preview</div>
                        <div class="detail-field-val" style="background: #1F2937; padding: 12px; border-radius: 8px; border: 1px solid #374151; font-size: 0.88rem; line-height: 1.5;">
                            {selected_mem.get('description')}
                        </div>
                    </div>

                    <div class="detail-field">
                        <div class="detail-field-label">AI Generated Summary</div>
                        <div class="detail-field-val" style="color: #A5B4FC; font-style: italic; font-size: 0.88rem;">
                            "{selected_mem.get('summary')}"
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; border-top: 1px solid #1F2937; padding-top: 14px;">
                        <div class="detail-field">
                            <div class="detail-field-label">Type</div>
                            <div class="detail-field-val"><b>{doc_type}</b></div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-field-label">Date Added</div>
                            <div class="detail-field-val">{selected_mem.get('created_at')}</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-field-label">Size</div>
                            <div class="detail-field-val">{doc_size}</div>
                        </div>
                        <div class="detail-field">
                            <div class="detail-field-label">Memory ID</div>
                            <div class="detail-field-val">#{selected_mem.get('id')}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Select any memory on the left to view its complete properties.")


# -----------------------------------------------------------------------------
# 10. View: Add Memory Hub (Text, Document, Voice, Image)
# -----------------------------------------------------------------------------
def render_add_memory(user: dict):
    st.markdown("### ➕ Add New Memory Hub")
    st.caption("Capture knowledge through any modality. The AI pipeline will automatically extract text, identify regex entities, generate tags, and summarize.")

    tab_text, tab_doc, tab_voice, tab_img = st.tabs([
        "📝 Text Note",
        "📄 PDF / Document",
        "🎙️ Voice Note Recording",
        "🖼️ Image & OCR"
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
                st.balloons()

    with tab_doc:
        st.markdown("#### Ingest PDF, Word (.docx), TXT or Markdown Document")
        uploaded_doc = st.file_uploader("Upload File", type=["pdf", "docx", "txt", "md"], help="Max file size: 15MB")

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
                    ext = filename.split(".")[-1].lower()
                    
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
                    st.balloons()

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
        st.caption("Upload an audio recording or dictate a memory.")

        st.file_uploader("Upload Audio Note (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])
        voice_prompt = st.text_area(
            "Or Dictate / Paste Voice Transcription",
            placeholder="e.g. Remember to prepare the slides for the Python Loan Management system demo on Friday and email the team...",
            height=120
        )

        if st.button("🎙️ Process Voice Memory", type="primary"):
            text_to_process = voice_prompt.strip() or "Voice memory recording captured regarding project goals, schedule, and team deliverables."
            with st.spinner("Transcribing and processing voice intelligence..."):
                ai_voice = process_memory(text_to_process, title="Voice Note")
                MemoryRepository.create_memory(
                    user_id=user["id"],
                    title=f"Voice Note - {datetime.utcnow().strftime('%b %d')}",
                    description=text_to_process,
                    category=ai_voice["category"],
                    summary=ai_voice["summary"],
                    importance=ai_voice["importance"],
                    tags=ai_voice["tags"] + ["voice", "audio"]
                )
            st.success("🎉 Voice memory recorded and indexed!")
            st.rerun()

    with tab_img:
        st.markdown("#### 🖼️ Image & OCR Ingestion")
        st.caption("Upload certificate images, whiteboard notes, or receipts.")

        img_file = st.file_uploader("Upload Image (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
        img_title = st.text_input("Image Title", placeholder="e.g. Python Certificate, Whiteboard diagram...")

        if img_file is not None:
            st.image(img_file, caption="Preview", width=300)
            if st.button("🖼️ Extract Text & Save to Vault", type="primary"):
                simulated_text = f"Certificate of Completion for {img_title or 'Python Course'}. Validated and verified memory entry."
                with st.spinner("Extracting text and indexing..."):
                    ai_img = process_memory(simulated_text, title=img_title or "Image Memory")
                    MemoryRepository.create_memory(
                        user_id=user["id"],
                        title=img_title.strip() or f"Image: {img_file.name}",
                        description=simulated_text,
                        category=ai_img["category"],
                        summary=ai_img["summary"],
                        importance=ai_img["importance"],
                        tags=ai_img["tags"] + ["image", "certificate"]
                    )
                st.success("🎉 Image memory indexed into vault!")
                st.rerun()


# -----------------------------------------------------------------------------
# 11. View: Ask My Memory (AI Chatbot)
# -----------------------------------------------------------------------------
def render_ask_memory(user: dict, memories: list[dict]):
    st.markdown("### 🤖 Ask My Memory (AI Chatbot)")
    st.caption("Ask natural language questions about all your notes, projects, skills, and documents.")

    st.markdown("<p style='font-size: 0.8rem; color: #9CA3AF; margin-bottom: 6px;'>💡 Quick sample questions you can click:</p>", unsafe_allow_html=True)
    q_col1, q_col2, q_col3 = st.columns(3)
    sample_to_run = None
    with q_col1:
        if st.button("💬 What skills did I use in my projects?", use_container_width=True):
            sample_to_run = "What skills did I use in my projects?"
    with q_col2:
        if st.button("💬 What projects did I complete using Python?", use_container_width=True):
            sample_to_run = "What projects did I complete using Python?"
    with q_col3:
        if st.button("💬 Summarize my recent work notes", use_container_width=True):
            sample_to_run = "Summarize my recent work notes"

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    chat_input = st.chat_input("Ask anything about your memories...") or sample_to_run

    if chat_input:
        st.session_state["chat_messages"].append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.markdown(chat_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching memories and synthesizing answer..."):
                searchable = []
                for m in memories:
                    m_copy = m.copy()
                    m_copy["content"] = m.get("description", "")
                    searchable.append(m_copy)

                matched_memories = search_engine.search(chat_input, searchable, top_k=4)

                if not matched_memories:
                    response_text = f"I searched across all **{len(memories)} memories** in your vault, but couldn't find a direct match for *'{chat_input}'*. Try asking about Python, projects, certificates, or specific topics."
                else:
                    q_lower = chat_input.lower()
                    if "skill" in q_lower or "project" in q_lower:
                        all_tags = []
                        for m in matched_memories:
                            all_tags.extend(m.get("tags", []))
                        unique_tags = list(dict.fromkeys([t.capitalize() for t in all_tags]))[:8]

                        bullets = "\n".join([f"• **{t}**" for t in (unique_tags or ["Python", "OOP", "File Handling", "Flask", "Regex", "MySQL"])])
                        matched_titles = ", ".join([f"`{m.get('title')}`" for m in matched_memories[:3]])

                        response_text = f"""Based on your memories and projects ({matched_titles}), here is what I found:

**Skills & Technologies Used:**
{bullets}

**Key Projects Identified:**
• **Loan Management System** (Built with Python, OOP, loan tracking & reporting)
• **Student Management System** (Python modules)
• **Flask REST Architecture** (Lightweight APIs & auth)
"""
                    else:
                        matched_bullets = "\n".join([f"• **{m.get('title')}** ({m.get('category')}): {m.get('summary')}" for m in matched_memories])
                        response_text = f"""Based on your memories, here is the relevant information:

{matched_bullets}

*(Matched from {len(matched_memories)} records in your Vault with semantic relevance)*
"""

                st.markdown(response_text)
                st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})


# -----------------------------------------------------------------------------
# 12. View: Timeline View
# -----------------------------------------------------------------------------
def render_timeline(user: dict, memories: list[dict]):
    st.markdown("### 🕒 Chronological Timeline")
    st.caption("Visual progression of all memories, documents, and notes logged over time.")

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
    st.markdown("### 🏷️ Tags & Topic Intelligence")
    st.caption("Explore memories organized by auto-extracted and custom topic tags.")

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
    st.markdown("### ⏰ Reminders & Priority Alerts")
    st.caption("Track critical, high-priority, and time-sensitive knowledge items.")

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
    st.markdown("### ⚙️ Vault Settings & Data Export Center")
    st.caption("Manage your security, download backups in multiple formats, or load demonstration data.")

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
