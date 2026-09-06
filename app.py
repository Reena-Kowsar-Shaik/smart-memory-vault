"""
Smart Memory Vault - Main Streamlit Application
Role: Member 4 (UI / UX / Analytics & Reporting)
Integrates:
- Member 1: Database & Authentication (SQLAlchemy, bcrypt, SQLite/PostgreSQL)
- Member 2: Document Processing Pipeline (PDF/DOCX/TXT/MD extraction & Regex entities)
- Member 3: AI & NLP Intelligence Engine (Categorization, Summarization, Sentiment, Semantic Search)
- Member 4: Streamlit UI/UX, Plotly Visualizations, Timeline & PDF/CSV Reporting
"""

import os
import json
from datetime import datetime
import streamlit as st
import pandas as pd

# Core & Backend Imports
from core.database import init_db, MemoryRepository
from core.auth import login_user, register_user
from pipeline import process_document
from nlp_engine import process_memory, search_engine, categorizer

# Member 4 Analytics & Reporting Imports
from analytics.charts import (
    CATEGORY_COLORS,
    get_color_for_category,
    create_category_distribution_chart,
    create_importance_histogram,
    create_sentiment_chart,
    create_top_tags_chart
)
from analytics.timeline import create_timeline_chart, get_activity_summary
from analytics.reporter import export_to_csv, export_to_json, generate_pdf_report

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
    /* Global Typography & Background adjustments */
    .main {
        padding-top: 1rem;
    }
    
    /* Header hero styling */
    .hero-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #60A5FA 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-banner h1 {
        color: #FFFFFF !important;
        margin-bottom: 6px;
        font-weight: 700;
        font-size: 2.1rem;
    }
    .hero-banner p {
        color: #E0E7FF !important;
        font-size: 1.05rem;
        margin: 0;
    }

    /* Metric card design */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.15s ease-in-out;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    .kpi-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
        font-weight: 600;
    }

    /* Memory Card styling */
    .memory-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    .memory-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        color: white;
        margin-right: 6px;
    }
    .tag-chip {
        display: inline-block;
        background-color: #F3F4F6;
        color: #4B5563;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 6px;
        margin-right: 4px;
        margin-top: 4px;
        border: 1px solid #E5E7EB;
    }
    .entity-chip {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1E40AF;
        font-size: 0.8rem;
        padding: 2px 8px;
        border-radius: 4px;
        margin: 2px;
        border: 1px solid #BFDBFE;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Database Initialization & Session Management
# -----------------------------------------------------------------------------
@st.cache_resource
def bootstrap_database():
    """Initializes tables on startup."""
    init_db()
    return True

bootstrap_database()

if "user" not in st.session_state:
    st.session_state["user"] = None

if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "Dashboard"

if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""


# -----------------------------------------------------------------------------
# 3. Authentication Module (Login / Register)
# -----------------------------------------------------------------------------
def render_auth_view():
    st.markdown("""
        <div class="hero-banner" style="text-align: center;">
            <h1>🧠 Smart Memory Vault</h1>
            <p>Your Intelligent Multi-Format Knowledge & Memory Repository</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with tab_login:
            st.markdown("### Access Your Vault")
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="e.g. user@example.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
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

            st.caption("💡 Tip: If you don't have an account yet, switch to the 'Create Account' tab.")

        with tab_register:
            st.markdown("### Register New Account")
            with st.form("register_form"):
                username = st.text_input("Username", placeholder="e.g. alex_rivera")
                reg_email = st.text_input("Email Address", placeholder="e.g. alex@example.com")
                reg_pass = st.text_input("Password (min 6 chars)", type="password")
                reg_pass_conf = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("Register Account", use_container_width=True, type="primary")

                if submit_reg:
                    if reg_pass != reg_pass_conf:
                        st.error("Passwords do not match.")
                    else:
                        res = register_user(username, reg_email, reg_pass)
                        if res.get("success"):
                            st.success("Account created successfully! You can now sign in.")
                        else:
                            st.error(res.get("error", "Registration failed."))


# -----------------------------------------------------------------------------
# 4. Authenticated Navigation & Main Sidebar
# -----------------------------------------------------------------------------
def render_sidebar(user: dict, memories: list[dict]):
    with st.sidebar:
        st.markdown(f"### 🧠 Smart Vault")
        st.markdown(f"👤 **{user['username']}**  \n*{user['email']}*")
        st.divider()

        nav_options = [
            "📊 Dashboard",
            "✍️ Capture Note",
            "📄 Document Ingestion",
            "🔍 Smart Vault & Search",
            "📈 Analytics & Reports"
        ]

        current_idx = 0
        for i, opt in enumerate(nav_options):
            if st.session_state["current_nav"] in opt:
                current_idx = i
                break

        selected_nav = st.radio(
            "Navigation",
            options=nav_options,
            index=current_idx,
            label_visibility="collapsed"
        )
        st.session_state["current_nav"] = selected_nav.split(" ")[1]

        st.divider()
        st.markdown(f"**Quick Stats**")
        st.markdown(f"• Total Memories: **{len(memories)}**")
        high_pri = sum(1 for m in memories if m.get("importance", 1) >= 4)
        st.markdown(f"• Urgent/High Priority: **{high_pri}**")

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["current_nav"] = "Dashboard"
            st.rerun()


# -----------------------------------------------------------------------------
# 5. View: Dashboard
# -----------------------------------------------------------------------------
def render_dashboard(user: dict, memories: list[dict]):
    st.markdown(f"""
        <div class="hero-banner">
            <h1>Welcome back, {user['username']}! 👋</h1>
            <p>Your centralized knowledge repository is synchronized and protected.</p>
        </div>
    """, unsafe_allow_html=True)

    stats = get_activity_summary(memories)

    # 4 Executive KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{stats['total_count']}</div>
                <div class="kpi-label">Total Memories</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #EF4444;">{stats['high_priority_count']}</div>
                <div class="kpi-label">Urgent / Critical</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #3B82F6;">{stats['top_category']}</div>
                <div class="kpi-label">Top Category</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #10B981;">{stats['avg_importance']}/5</div>
                <div class="kpi-label">Avg Priority</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Dashboard Body
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("⚡ Quick Shortcuts")
        q1, q2, q3 = st.columns(3)
        with q1:
            if st.button("✍️ New Note", use_container_width=True):
                st.session_state["current_nav"] = "Capture"
                st.rerun()
        with q2:
            if st.button("📄 Upload Doc", use_container_width=True):
                st.session_state["current_nav"] = "Document"
                st.rerun()
        with q3:
            if st.button("🔍 Explore Vault", use_container_width=True):
                st.session_state["current_nav"] = "Smart"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🕒 Recent Memories")
        if not memories:
            st.info("No memories found. Start by creating a note or uploading a document!")
        else:
            for mem in memories[:3]:
                cat = mem.get("category", "General")
                cat_color = get_color_for_category(cat)
                imp_stars = "⭐" * int(mem.get("importance", 1))

                with st.container():
                    st.markdown(f"""
                        <div class="memory-card">
                            <div class="memory-header">
                                <h4 style="margin: 0; color: #111827;">{mem.get('title')}</h4>
                                <div>
                                    <span class="badge-pill" style="background-color: {cat_color};">{cat}</span>
                                    <span style="font-size: 0.9rem;">{imp_stars}</span>
                                </div>
                            </div>
                            <p style="color: #4B5563; font-size: 0.95rem; margin-bottom: 8px;">
                                {mem.get('summary') or mem.get('description', '')[:120] + '...'}
                            </p>
                            <small style="color: #9CA3AF;">Created: {mem.get('created_at')}</small>
                        </div>
                    """, unsafe_allow_html=True)

    with col_right:
        st.subheader("📊 Category Distribution")
        fig_cat = create_category_distribution_chart(memories)
        st.plotly_chart(fig_cat, use_container_width=True)


# -----------------------------------------------------------------------------
# 6. View: Quick Capture Note (with AI Assistance)
# -----------------------------------------------------------------------------
def render_capture_note(user: dict):
    st.subheader("✍️ Capture New Memory Note")
    st.caption("Enter your note or thoughts. The AI Intelligence Engine will automatically detect the category, extract tags, generate a concise summary, and assign priority.")

    with st.form("note_form"):
        title = st.text_input("Memory Title", placeholder="e.g. Doctor appointment notes, Sprint planning...")
        description = st.text_area("Content / Note Details", height=180, placeholder="Write your notes, decisions, reminders, or insights here...")
        
        col_cat, col_imp = st.columns(2)
        with col_cat:
            category_override = st.selectbox(
                "Category (Leave as 'Auto-Detect' for AI classification)",
                options=["Auto-Detect", "Work", "Health", "Finance", "Study", "Personal", "General"]
            )
        with col_imp:
            importance_override = st.slider("Importance Level", min_value=1, max_value=5, value=3, help="1 is low priority, 5 is critical/urgent")

        tags_input = st.text_input("Tags (comma-separated, or leave blank for AI extraction)", placeholder="e.g. health, clinic, blood-test")

        submit_note = st.form_submit_button("🚀 Process & Save to Vault", type="primary", use_container_width=True)

    if submit_note:
        if not title.strip() or not description.strip():
            st.error("Please provide both a title and content for your memory.")
            return

        with st.spinner("AI Engine is analyzing, categorizing, and summarizing..."):
            # Call Member 3 NLP Engine
            ai_data = process_memory(description, title=title)

            # Determine final category
            final_category = ai_data["category"] if category_override == "Auto-Detect" else category_override

            # Determine final tags
            if tags_input.strip():
                final_tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()]
            else:
                final_tags = ai_data["tags"]

            # Save via Member 1 Repository
            new_mem = MemoryRepository.create_memory(
                user_id=user["id"],
                title=title.strip(),
                description=description.strip(),
                category=final_category,
                summary=ai_data["summary"],
                importance=importance_override,
                tags=final_tags
            )

        st.success(f"🎉 Memory '{title}' successfully saved to your Vault!")

        # Preview AI Enrichment Results
        with st.expander("✨ View AI Intelligence Metadata", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"**Predicted Category:** `{final_category}`")
                st.markdown(f"**Sentiment:** `{ai_data['sentiment']}`")
            with col_b:
                st.markdown(f"**Suggested Priority:** `{ai_data['importance']}/5`")
                st.markdown(f"**Sentiment Polarity:** `{ai_data['polarity_score']}`")
            with col_c:
                st.markdown(f"**Generated Tags:** {', '.join([f'`{t}`' for t in final_tags])}")

            st.markdown(f"**Generated Summary:**  \n> {ai_data['summary']}")


# -----------------------------------------------------------------------------
# 7. View: Document Ingestion Hub
# -----------------------------------------------------------------------------
def render_document_ingestion(user: dict):
    st.subheader("📄 Document Ingestion Hub")
    st.caption("Upload PDFs, Word documents (.docx), Markdown, or Text files. The system validates, extracts text, identifies regex entities (dates, emails, phone numbers, currencies), and enriches it with AI.")

    uploaded_file = st.file_uploader(
        "Choose a document to ingest",
        type=["pdf", "docx", "txt", "md"],
        help="Supported: PDF, DOCX, TXT, MD up to 15MB"
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name

        st.info(f"📁 Selected: **{filename}** ({len(file_bytes) / 1024:.1f} KB)")

        if st.button("⚡ Run Pipeline & Ingest Document", type="primary"):
            with st.spinner("Executing extraction and regex cleaning pipeline..."):
                # Call Member 2 Document Pipeline
                doc_result = process_document(file_bytes, filename, user["id"])

            if doc_result.get("status") == "error":
                st.error(f"Extraction failed: {doc_result.get('error_message')}")
                return

            metadata = doc_result.get("metadata", {})
            cleaned_text = doc_result.get("cleaned_text", "")
            entities = doc_result.get("extracted_entities", {})

            st.success("✅ Document processed successfully!")

            # Document Metadata Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Pages", metadata.get("page_count", 1))
            m2.metric("Word Count", metadata.get("word_count", 0))
            m3.metric("Duplicate File?", "Yes" if metadata.get("is_duplicate") else "No")
            m4.metric("Scanned/Image?", "Yes" if metadata.get("is_scanned") else "No")

            # Entity Highlights
            st.markdown("#### 🔍 Discovered Entities (Regex Extractor)")
            ent_tabs = st.tabs(["📅 Dates", "✉️ Emails", "📞 Phone Numbers", "💵 Financial Amounts", "🌐 URLs"])

            with ent_tabs[0]:
                dates = entities.get("dates", [])
                if dates:
                    st.write(" ".join([f"<span class='entity-chip'>{d}</span>" for d in dates]), unsafe_allow_html=True)
                else:
                    st.caption("No dates identified.")

            with ent_tabs[1]:
                emails = entities.get("emails", [])
                if emails:
                    st.write(" ".join([f"<span class='entity-chip'>{e}</span>" for e in emails]), unsafe_allow_html=True)
                else:
                    st.caption("No emails identified.")

            with ent_tabs[2]:
                phones = entities.get("phone_numbers", [])
                if phones:
                    st.write(" ".join([f"<span class='entity-chip'>{p}</span>" for p in phones]), unsafe_allow_html=True)
                else:
                    st.caption("No phone numbers identified.")

            with ent_tabs[3]:
                amounts = entities.get("amounts", [])
                if amounts:
                    st.write(" ".join([f"<span class='entity-chip'>{a}</span>" for a in amounts]), unsafe_allow_html=True)
                else:
                    st.caption("No financial amounts identified.")

            with ent_tabs[4]:
                urls = entities.get("urls", [])
                if urls:
                    st.write(" ".join([f"<span class='entity-chip'>{u}</span>" for u in urls]), unsafe_allow_html=True)
                else:
                    st.caption("No URLs identified.")

            st.markdown("<br>", unsafe_allow_html=True)

            # AI Processing Preview
            with st.spinner("Passing cleaned text through AI Categorizer & Summarizer..."):
                ai_doc = process_memory(cleaned_text[:4000], title=filename)

            st.markdown("#### 🧠 AI Summary & Classification")
            col_x, col_y = st.columns([3, 1])
            with col_x:
                st.markdown(f"**AI Summary:**  \n{ai_doc['summary']}")
            with col_y:
                st.markdown(f"**Category:** `{ai_doc['category']}`")
                st.markdown(f"**Sentiment:** `{ai_doc['sentiment']}`")
                st.markdown(f"**Priority:** `{ai_doc['importance']}/5`")

            st.markdown("<br>", unsafe_allow_html=True)

            # Button to save directly into Memory Vault
            if st.button("💾 Save Ingested Document as Vault Memory", type="secondary"):
                new_mem = MemoryRepository.create_memory(
                    user_id=user["id"],
                    title=f"Doc: {filename}",
                    description=cleaned_text[:5000],
                    category=ai_doc["category"],
                    summary=ai_doc["summary"],
                    importance=ai_doc["importance"],
                    tags=ai_doc["tags"] + [filename.split(".")[-1].lower()]
                )
                st.success(f"Document memory saved with ID #{new_mem.get('id')}!")
                st.balloons()


# -----------------------------------------------------------------------------
# 8. View: Smart Vault & Semantic Search
# -----------------------------------------------------------------------------
def render_smart_vault(user: dict, memories: list[dict]):
    st.subheader("🔍 Smart Vault Explorer & Semantic Search")
    st.caption("Search across memories using natural language intent (e.g. 'hospital visit' will intelligently match doctor appointments).")

    # Search Bar
    search_col, btn_col = st.columns([4, 1])
    with search_col:
        query = st.text_input("Semantic Search Query", value=st.session_state["search_query"], placeholder="e.g. tax filing, medical prescriptions, team standup...")
    with btn_col:
        st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_clicked = st.button("Search", use_container_width=True, type="primary")

    # Filter Bar
    f1, f2, f3 = st.columns(3)
    categories = ["All"] + sorted(list({m.get("category", "General") for m in memories}))
    with f1:
        sel_category = st.selectbox("Filter by Category", options=categories)
    with f2:
        min_importance = st.select_slider("Minimum Priority", options=[1, 2, 3, 4, 5], value=1)
    with f3:
        sort_order = st.selectbox("Sort Order", options=["Newest First", "Oldest First", "Highest Priority"])

    # Search Execution
    active_memories = memories.copy()
    if query.strip():
        # Ensure memory format compatibility for search engine
        searchable_list = []
        for m in active_memories:
            m_copy = m.copy()
            m_copy["content"] = m.get("description", "")
            searchable_list.append(m_copy)

        active_memories = search_engine.search(query.strip(), searchable_list, top_k=20)
        st.info(f"Semantic search returned {len(active_memories)} matching results.")

    # Category and Importance Filtering
    if sel_category != "All":
        active_memories = [m for m in active_memories if m.get("category") == sel_category]
    active_memories = [m for m in active_memories if int(m.get("importance", 1)) >= min_importance]

    # Sorting
    if sort_order == "Newest First":
        active_memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort_order == "Oldest First":
        active_memories.sort(key=lambda x: x.get("created_at", ""))
    elif sort_order == "Highest Priority":
        active_memories.sort(key=lambda x: int(x.get("importance", 1)), reverse=True)

    st.markdown(f"**Displaying {len(active_memories)} memories**")
    st.divider()

    if not active_memories:
        st.warning("No memories match your query and filter criteria.")
        return

    # Render Memory Cards
    for mem in active_memories:
        mem_id = mem.get("id")
        cat = mem.get("category", "General")
        cat_color = get_color_for_category(cat)
        imp = int(mem.get("importance", 1))
        sim_score = mem.get("similarity_score")

        with st.container():
            col_head_left, col_head_right = st.columns([4, 1])
            with col_head_left:
                st.markdown(f"### {mem.get('title')}")
            with col_head_right:
                st.markdown(f"<div style='text-align: right;'><span class='badge-pill' style='background-color: {cat_color};'>{cat}</span> {'⭐' * imp}</div>", unsafe_allow_html=True)

            if sim_score:
                st.caption(f"🎯 Semantic Intent Match Score: `{sim_score}`")

            st.markdown(f"**Summary:** {mem.get('summary')}")

            # Expandable Full Note & Actions
            with st.expander("📖 View Full Content & Manage"):
                st.markdown(f"**Full Content:**")
                st.text(mem.get("description", ""))

                tags = mem.get("tags") or []
                if tags:
                    tags_html = " ".join([f"<span class='tag-chip'>#{t}</span>" for t in tags])
                    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)

                st.caption(f"Entry ID: #{mem_id} | Date: {mem.get('created_at')}")

                # Delete Action
                col_del, _ = st.columns([1, 4])
                with col_del:
                    if st.button(f"🗑️ Delete Memory", key=f"del_{mem_id}"):
                        MemoryRepository.delete_memory(mem_id, user["id"])
                        st.success(f"Memory #{mem_id} removed.")
                        st.rerun()

            st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 9. View: Analytics & Reports
# -----------------------------------------------------------------------------
def render_analytics(user: dict, memories: list[dict]):
    st.subheader("📈 Analytics & Insights Dashboard")
    st.caption("Deep-dive visualizations of your personal knowledge vault, timeline activity, and report export center.")

    tab_visuals, tab_timeline, tab_exports = st.tabs(["📊 Charts & Distributions", "🕒 Chronological Timeline", "📄 Export Reports"])

    stats = get_activity_summary(memories)

    with tab_visuals:
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            fig_cats = create_category_distribution_chart(memories)
            st.plotly_chart(fig_cats, use_container_width=True)
        with row1_col2:
            fig_imp = create_importance_histogram(memories)
            st.plotly_chart(fig_imp, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            fig_sent = create_sentiment_chart(memories)
            st.plotly_chart(fig_sent, use_container_width=True)
        with row2_col2:
            fig_tags = create_top_tags_chart(memories, top_n=8)
            st.plotly_chart(fig_tags, use_container_width=True)

    with tab_timeline:
        st.markdown("#### Interactive Memory Timeline")
        st.caption("Memories plotted across dates. Size represents importance rating; color denotes category.")
        fig_time = create_timeline_chart(memories)
        st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("#### Temporal Metrics")
        t1, t2, t3 = st.columns(3)
        t1.metric("Logged Past 7 Days", f"{stats['this_week']} memories")
        t2.metric("Logged Past 30 Days", f"{stats['this_month']} memories")
        t3.metric("Most Active Domain", stats['top_category'])

    with tab_exports:
        st.markdown("#### Export & Data Backup Center")
        st.caption("Download your personal knowledge repository in PDF dossier, CSV spreadsheet, or JSON backup formats.")

        exp_c1, exp_c2, exp_c3 = st.columns(3)

        with exp_c1:
            st.markdown("##### 📄 PDF Executive Dossier")
            st.write("Generates a formatted, printable PDF summary report of all memories, priorities, and statistics.")
            pdf_bytes = generate_pdf_report(user, memories, stats)
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"vault_report_{user['username']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with exp_c2:
            st.markdown("##### 📊 CSV Spreadsheet")
            st.write("Tabular format compatible with Microsoft Excel, Google Sheets, or data analysis pipelines.")
            csv_data = export_to_csv(memories)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"memories_{user['username']}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with exp_c3:
            st.markdown("##### 🗄️ JSON Archive")
            st.write("Complete structured metadata archive for migrations or machine-readable backups.")
            json_data = export_to_json(memories)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"memories_{user['username']}.json",
                mime="application/json",
                use_container_width=True
            )


# -----------------------------------------------------------------------------
# 10. Main Routing Logic
# -----------------------------------------------------------------------------
def main():
    user = st.session_state.get("user")

    if not user:
        render_auth_view()
        return

    # Fetch latest user memories from Member 1 Repository
    memories = MemoryRepository.get_user_memories(user["id"])

    # Render Sidebar navigation
    render_sidebar(user, memories)

    nav = st.session_state.get("current_nav", "Dashboard")

    if nav == "Dashboard":
        render_dashboard(user, memories)
    elif nav == "Capture":
        render_capture_note(user)
    elif nav == "Document":
        render_document_ingestion(user)
    elif nav == "Smart":
        render_smart_vault(user, memories)
    elif nav == "Analytics":
        render_analytics(user, memories)
    else:
        render_dashboard(user, memories)


if __name__ == "__main__":
    main()
