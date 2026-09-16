import streamlit as st
from pipeline import process_document

st.set_page_config(page_title="Member 2 Pipeline Tester", page_icon="📄", layout="wide")

st.title("📄 Document Processing & Ingestion (Member 2 Test)")
st.write("Upload a real PDF, Word doc, or Text file to test extraction and regex cleaning.")

# Simulated User ID
user_id = st.sidebar.number_input("Simulated User ID", min_value=1, value=1)

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "md"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name

    with st.spinner("Processing through Member 2 pipeline..."):
        result = process_document(file_bytes, filename, user_id)

    if result.get("status") == "error":
        st.error(f"❌ Extraction Failed: {result.get('error_message')}")
    else:
        meta = result["metadata"]
        st.success(f"✅ Success! File stored at: `{meta['stored_path']}`")

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Pages", meta["page_count"])
        col2.metric("Word Count", meta["word_count"])
        col3.metric("File Size", f"{meta['file_size'] / 1024:.1f} KB")
        col4.metric("Is Duplicate?", "⚠️ Yes (Cached)" if meta["is_duplicate"] else "✨ No (New)")

        # Regex extracted entities
        st.subheader("🔍 Auto-Extracted Regex Entities")
        st.json(result["extracted_entities"])

        # Extracted text preview
        st.subheader("📝 Cleaned Text Preview")
        st.text_area("Extracted Content", result["cleaned_text"], height=300)
