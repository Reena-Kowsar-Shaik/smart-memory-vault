"""
nlp_engine/rag_engine.py
Conversational Retrieval-Augmented Generation (RAG) Engine with Direct Source Citations.
Enables 'Chat with Your Vault' across all documents, notes, image OCR, and YouTube transcripts.
"""

import re
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize

from .search_engine import INTENT_EXPANSIONS
from .summarizer import TextSummarizer, clean_sentence


class VaultRAGEngine:
    """
    Production-grade RAG engine for knowledge vaults:
    1. Semantic Chunking of long documents/transcripts.
    2. Hybrid Retrieval (TF-IDF + Cosine Similarity + Intent Expansion + Temporal & Category Priority).
    3. Comprehensive Answer & Detailed Multi-Point Summarization Synthesis.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.summarizer = TextSummarizer()

    def chunk_memory(self, memory: Dict[str, Any], chunk_size: int = 500, overlap: int = 80) -> List[Dict[str, Any]]:
        """
        Splits a single memory/document into semantic text chunks while preserving metadata.
        """
        mem_id = memory.get("id")
        title = memory.get("title", "Untitled Memory")
        category = memory.get("category", "General")
        tags = memory.get("tags", [])
        content = memory.get("description", "") or memory.get("content", "") or memory.get("summary", "")
        created_at = memory.get("created_at", "")

        if not content.strip():
            return []

        # Short content fits in single chunk
        if len(content) <= chunk_size:
            return [{
                "memory_id": mem_id,
                "title": title,
                "category": category,
                "tags": tags,
                "created_at": created_at,
                "chunk_index": 0,
                "text": content.strip()
            }]

        try:
            sentences = sent_tokenize(content)
        except Exception:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if s.strip()]

        chunks = []
        current_sentences = []
        current_len = 0
        chunk_idx = 0

        for sentence in sentences:
            sentence_len = len(sentence)
            if current_len + sentence_len > chunk_size and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append({
                    "memory_id": mem_id,
                    "title": title,
                    "category": category,
                    "tags": tags,
                    "created_at": created_at,
                    "chunk_index": chunk_idx,
                    "text": chunk_text
                })
                chunk_idx += 1
                if len(current_sentences) > 1:
                    current_sentences = [current_sentences[-1], sentence]
                    current_len = len(current_sentences[0]) + sentence_len
                else:
                    current_sentences = [sentence]
                    current_len = sentence_len
            else:
                current_sentences.append(sentence)
                current_len += sentence_len

        if current_sentences:
            chunks.append({
                "memory_id": mem_id,
                "title": title,
                "category": category,
                "tags": tags,
                "created_at": created_at,
                "chunk_index": chunk_idx,
                "text": " ".join(current_sentences)
            })

        return chunks

    def build_chunk_corpus(self, memories: List[Dict[str, Any]], scope_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generates all searchable chunks across all memories, optionally filtered by category."""
        all_chunks = []
        for mem in memories:
            if scope_category and scope_category != "All Categories":
                if mem.get("category", "").lower() != scope_category.lower():
                    continue
            chunks = self.chunk_memory(mem)
            all_chunks.extend(chunks)
        return all_chunks

    def retrieve_relevant_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 6) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant chunks using TF-IDF + query expansion + cosine similarity + intent weighting.
        """
        if not query or not query.strip() or not chunks:
            return []

        q_lower = query.lower().strip()

        # Check if query requests broad summary
        is_summary_query = any(w in q_lower for w in ["summarize", "summary", "overview", "recap", "briefing", "notes", "all", "latest", "project"])
        actual_k = max(top_k, 8) if is_summary_query else top_k

        # Extract meaningful query keywords (excluding stopwords)
        STOPWORDS_SET = {"what", "are", "and", "the", "for", "with", "how", "why", "who", "all", "can", "you", "tell", "show", "give", "from", "your", "about"}
        query_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', q_lower) if w not in STOPWORDS_SET]
        expanded = [query]
        for w in query_words:
            if w in INTENT_EXPANSIONS:
                expanded.extend(INTENT_EXPANSIONS[w])
        enriched_query = " ".join(expanded)

        corpus_texts = [
            f"{c.get('title', '')} {c.get('category', '')} {' '.join(c.get('tags', []))} {c.get('text', '')}"
            for c in chunks
        ]

        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus_texts)
            query_vec = vectorizer.transform([enriched_query])
            similarities = cosine_similarity(query_vec, tfidf_matrix)[0]

            scored_chunks = []
            for idx, score in enumerate(similarities):
                chunk_copy = chunks[idx].copy()
                base_score = float(score)

                # Intent Boosters:
                chunk_cat = chunk_copy.get("category", "").lower()
                chunk_title = chunk_copy.get("title", "").lower()

                # Boost if category mentioned in query
                if chunk_cat and re.search(r'\b' + re.escape(chunk_cat) + r'\b', q_lower):
                    base_score += 0.35

                # Exact topic keyword match in title using word boundary
                for qw in query_words:
                    if len(qw) >= 3 and re.search(r'\b' + re.escape(qw) + r'\b', chunk_title):
                        base_score += 0.45

                # Project / Work boost if user asked for "project"
                if ("project" in q_lower or "work" in q_lower) and chunk_cat in ["work", "project", "projects"]:
                    base_score += 0.25

                # Latest / Recent boost
                if "latest" in q_lower or "recent" in q_lower:
                    base_score += 0.15

                if base_score > 0.005 or is_summary_query:
                    chunk_copy["similarity_score"] = round(base_score, 4)
                    chunk_copy["confidence_pct"] = min(99, int(base_score * 100) + 35)
                    scored_chunks.append(chunk_copy)

            # Sort descending by relevance score
            scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)

            if not scored_chunks and is_summary_query and chunks:
                return chunks[:actual_k]

            return scored_chunks[:actual_k]

        except Exception:
            return chunks[:actual_k] if chunks else []

    def _extract_definition_or_best_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Identifies full conceptual definitions or comprehensive answering sentences.
        """
        q_lower = query.lower().strip()
        query_keywords = [
            w for w in re.findall(r'\b[a-zA-Z]{3,}\b', q_lower)
            if w not in {"what", "how", "why", "who", "when", "where", "the", "and", "for", "with", "summarize", "tell", "show"}
        ]

        target_subject = query_keywords[0] if query_keywords else ""

        all_text = "\n\n".join([c.get("text", "") for c in chunks])
        concept_sents = self.summarizer.extract_clean_concept_sentences(all_text)

        if not concept_sents:
            return "No detailed notes found for this topic."

        # Find best definition sentence
        scored_candidates = []
        for s in concept_sents:
            s_lower = s.lower()
            score = 0

            # Direct definition pattern (e.g. "A string is a sequence...", "Control statements are used to...")
            if target_subject and re.search(r'\b' + re.escape(target_subject) + r'\b\s+(?:is|are|refers to|means|represents|defined as)\b', s_lower):
                score += 80

            # General definition indicators
            if re.search(r'\b(is a|is an|are used to|refers to|process of|smallest individual|defined as|meaning)\b', s_lower):
                score += 40

            # Query keyword matches
            matched_kws = sum(1 for kw in query_keywords if kw in s_lower)
            score += (matched_kws * 15)

            # Skip questions or short fragments
            if s.endswith("?") or len(s.split()) < 5:
                score -= 30

            if score > 0:
                scored_candidates.append((score, s))

        if scored_candidates:
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            top_sent = scored_candidates[0][1]
            if len(scored_candidates) > 1:
                second_sent = scored_candidates[1][1]
                if target_subject and target_subject in second_sent.lower() and len(top_sent.split()) < 25:
                    if second_sent.lower() not in top_sent.lower() and top_sent.lower() not in second_sent.lower():
                        return f"{top_sent} {second_sent}"
            return top_sent

        # Fallback to summarizer
        return self.summarizer.summarize(all_text, max_sentences=2)

    def synthesize_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes a structured, highly detailed yet concise conversational answer
        with comprehensive key points covering the entire relevant content.
        """
        if not retrieved_chunks:
            return {
                "answer": f"I searched across your vault, but could not find relevant notes or documents answering **'{query}'**.\n\n*Tip: Try asking about your uploaded PDFs, YouTube transcripts, projects, or specific tags.*",
                "citations": [],
                "confidence": 0,
                "sources_count": 0
            }

        top_chunk = retrieved_chunks[0]
        avg_conf = int(sum(c.get("confidence_pct", 75) for c in retrieved_chunks) / len(retrieved_chunks))

        # Aggregate full text from all retrieved chunks for deep synthesis
        full_corpus = "\n\n".join([c.get("text", "") for c in retrieved_chunks])

        # 1. Direct answer / Executive summary
        core_summary = self._extract_definition_or_best_answer(query, retrieved_chunks)

        # 2. Extract detailed structured bullet points (covering the entire content)
        bullet_points = self.summarizer.generate_bullets(full_corpus, max_points=5)

        # 3. Build Citations & Source Excerpts
        citations = []
        seen_titles = set()
        for idx, c in enumerate(retrieved_chunks, 1):
            if c["title"] not in seen_titles:
                seen_titles.add(c["title"])
                c_sents = self.summarizer.extract_clean_concept_sentences(c["text"])
                valid_sents = [s for s in c_sents if len(s) >= 28 and not re.search(r'^(python!|hello world|print)', s, re.I)]
                if valid_sents:
                    clean_snippet = valid_sents[0][:180] + ("..." if len(valid_sents[0]) > 180 else "")
                else:
                    clean_snippet = core_summary[:180] + ("..." if len(core_summary) > 180 else "")

                citations.append({
                    "citation_id": idx,
                    "title": c["title"],
                    "category": c["category"],
                    "tags": c.get("tags", []),
                    "confidence": f"{c.get('confidence_pct', 85)}%",
                    "excerpt": clean_snippet
                })

        # 4. Format Output Markdown with distinct bullet spacing
        bullets_formatted = "\n\n".join(bullet_points) if bullet_points else f"• {core_summary}"

        answer_markdown = f"""### 🎯 Core Overview & Summary
{core_summary}

---

### 💡 Key Concepts & Core Takeaways
{bullets_formatted}

---

### 📚 Sources & Verified Citations
"""

        for cit in citations:
            answer_markdown += f"- **[{cit['citation_id']}] {cit['title']}** (`{cit['category']}`) — *Confidence: {cit['confidence']}*\n  > \"{cit['excerpt']}\"\n\n"

        return {
            "answer": answer_markdown,
            "citations": citations,
            "confidence": avg_conf,
            "sources_count": len(citations),
            "top_source": top_chunk["title"]
        }

    def chat(self, query: str, memories: List[Dict[str, Any]], scope_category: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for 'Chat with Your Vault'.
        Handles conceptual Q&A, broad summaries, skill discovery, and knowledge inventory.
        """
        if not memories:
            return {
                "answer": f"I searched across your vault, but could not find relevant notes or documents answering **'{query}'** because your Vault is currently empty.\n\n*Tip: Upload documents (PDFs), notes, voice recordings, or YouTube links to start asking questions!*",
                "citations": [],
                "confidence": 0,
                "sources_count": 0,
                "top_source": "None"
            }

        q_lower = query.lower().strip()
        
        # Check for broad inventory / overview requests
        is_inventory = any(kw in q_lower for kw in [
            "what is in my vault", "what do i have in my vault", "what memories", "what documents", 
            "list my notes", "list all documents", "show my memories", "show vault", "everything in vault", 
            "all notes", "all documents", "what is stored"
        ])
        if is_inventory:
            cat_groups = {}
            for m in memories:
                c = m.get("category", "General")
                cat_groups.setdefault(c, []).append(m)
            
            lines = [f"Your Vault contains **{len(memories)} indexed knowledge items** across **{len(cat_groups)} categories**:"]
            for cat, mem_list in cat_groups.items():
                items_str = ", ".join([f"*{m.get('title')}*" for m in mem_list[:5]])
                lines.append(f"• **{cat} ({len(mem_list)}):** {items_str}")
            
            bullets = "\n".join(lines)
            ans = f"""### 🎯 Core Overview & Summary
{bullets}

---

### 💡 Key Concepts & Core Takeaways
• You can ask specific questions about any of the items above (e.g. *"What were the key takeaways from my Python Project?"*).
• Filter your retrieval scope using the category dropdown to target specific domains like Study or Work.

---

### 📚 Sources & Verified Citations
- **[1] Entire Knowledge Vault** (`All`) — *Confidence: 100%*
  > "Indexed {len(memories)} documents, notes, and records."
"""
            return {
                "answer": ans,
                "citations": [{
                    "citation_id": 1,
                    "title": "Entire Knowledge Vault",
                    "category": "All",
                    "tags": ["vault", "inventory"],
                    "confidence": "100%",
                    "excerpt": f"Indexed {len(memories)} documents, notes, and records."
                }],
                "confidence": 99,
                "sources_count": len(memories),
                "top_source": "Entire Knowledge Vault"
            }

        chunks = self.build_chunk_corpus(memories, scope_category=scope_category)
        retrieved = self.retrieve_relevant_chunks(query, chunks, top_k=6)
        return self.synthesize_answer(query, retrieved)
