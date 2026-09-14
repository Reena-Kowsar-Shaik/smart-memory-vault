# 🧠 Smart Memory Vault (AI-Powered Multimodal Knowledge & Life Log)

An intelligent, multi-user personal knowledge vault, study companion, and multimodal memory assistant. Automatically parses, categorizes, and summarizes notes, documents (PDF, DOCX, TXT), images (OCR), YouTube video transcripts, and web articles with NLP-driven semantic search, interactive neural knowledge graphs, study flashcards, and automated multiple-choice quiz generation.

---

## 🚀 Teammate Quickstart Guide (Run Locally)

Follow these steps to clone, set up, and run the project on your machine:

### 1. Clone the Repository
```bash
git clone <YOUR_REPOSITORY_URL>
cd smart-memory-vault
```

### 2. Create and Activate a Python Virtual Environment
* **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```
The app will automatically start and open in your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Unit Tests
To verify all database, NLP, analytics, and multimodal ingestion modules:
```bash
python -m unittest discover -s . -p "test_*.py"
```

---

## 🌟 Key Features

1. **Dashboard & Analytics:**
   - Real-time memory counters, category breakdown, sentiment analysis, and priority breakdown.
   - One-click executive PDF report export.
2. **Multimodal Ingestion Hub:**
   - **Documents:** PDF, DOCX, TXT, MD up to 100MB with automated metadata and regex entity extraction.
   - **📸 Image & Handwriting OCR:** Ingest whiteboards, study diagrams, book pages, and certificates with multi-engine OCR (`pytesseract`, `easyocr`, PIL).
   - **🌐 Web & YouTube Ingestion:** Paste YouTube video links to extract full transcripts or web URLs to scrape clean article text.
   - **🎙️ Voice Note Recording:** Dictate or upload audio notes with automatic AI processing.
3. **Interactive Knowledge Mind Map:**
   - Plotly-powered radial network graph connecting vault categories, tags, and individual memory nodes.
4. **Study Flashcards & Interactive Quiz Engine:**
   - Automatically extracts Q&A pairs, definition structures, and technical concepts from uploaded notes and documents.
   - Interactive flip cards with Mastery tracking.
   - Self-grading multiple choice quizzes with context explanations.
5. **Hybrid Semantic & Keyword Search:**
   - Fast keyword matching and TF-IDF semantic vector similarity search with category filters.
6. **Robust Multi-user Authentication:**
   - Secure bcrypt password hashing and user-isolated SQLite/PostgreSQL storage.

---

## 📁 Project Structure

```text
smart-memory-vault/
├── app.py                      # Main Streamlit web application & UI
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide and documentation
│
├── core/
│   ├── auth.py                 # User authentication & session management
│   ├── database.py             # Database schemas & CRUD repositories
│   └── logger.py               # Centralized logging engine
│
├── pipeline/
│   ├── uploader.py             # File upload handler (PDF, DOCX, TXT, Images up to 100MB)
│   ├── extractor.py            # Text & metadata extraction router
│   ├── ocr_extractor.py        # Multi-engine Optical Character Recognition (OCR)
│   ├── web_extractor.py        # YouTube transcript & web article scraper
│   └── regex_cleaner.py        # PII & regex entity extraction (dates, emails, phones, amounts)
│
├── nlp_engine/
│   ├── categorizer.py          # Auto-categorization & CS domain tag extraction
│   ├── summarizer.py           # Extractive text summarization
│   ├── sentiment.py            # Sentiment analysis & mood scoring
│   ├── search_engine.py        # Semantic & TF-IDF search engine
│   └── quiz_generator.py       # Study flashcards & AI quiz generation
│
└── analytics/
    ├── charts.py               # Plotly visual analytics & charts
    ├── knowledge_graph.py      # Interactive mind map network graph
    └── reporter.py             # PDF executive report exporter
```
