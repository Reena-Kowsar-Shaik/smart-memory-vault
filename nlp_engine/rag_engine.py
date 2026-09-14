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


def clean_sentence(text: str) -> str:
    """Cleans sentence by stripping weird bullet glyphs, excess spaces, and noisy characters."""
    if not text:
        return ""
    # Replace weird unicode bullets with standard spaces
    cleaned = re.sub(r'[●•■◆▪▸►]+\s*', ' ', text)
    # Remove leading noise
    cleaned = re.sub(r'^[#*\-:\s]+', '', cleaned).strip()
    # Normalize multiple whitespaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


class VaultRAGEngine:
    """
    Production-grade RAG engine for knowledge vaults:
    1. Semantic Chunking of long documents/transcripts.
    2. Hybrid Retrieval (TF-IDF + Cosine Similarity + Intent Expansion).
    3. Contextual Answer Synthesis with Definition Detection and Clean Citations.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def chunk_memory(self, memory: Dict[str, Any], chunk_size: int = 500, overlap: int = 80) -> List[Dict[str, Any]]:
        """
        Splits a single memory/document into semantic text chunks while preserving metadata.
        """
        mem_id = memory.get("id")
        title = memory.get("title", "Untitled Memory")
        category = memory.get("category", "General")
        tags = memory.get("tags", [])
        content = memory.get("description", "") or memory.get("content", "") or memory.get("summary", "")

        if not content.strip():
            return []

        # If short content, keep as single chunk
        if len(content) <= chunk_size:
            return [{
                "memory_id": mem_id,
                "title": title,
                "category": category,
                "tags": tags,
                "chunk_index": 0,
                "text": content.strip()
            }]

        # Split into sentences for clean boundary chunks
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
                    "chunk_index": chunk_idx,
                    "text": chunk_text
                })
                chunk_idx += 1
                # Overlap: retain last sentence if meaningful
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

    def retrieve_relevant_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieves the top-k most relevant chunks using TF-IDF + query expansion + cosine similarity.
        """
        if not query or not query.strip() or not chunks:
            return []

        # Expand query intent
        query_words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
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
                if score > 0.01:
                    chunk_copy = chunks[idx].copy()
                    chunk_copy["similarity_score"] = round(float(score), 4)
                    chunk_copy["confidence_pct"] = min(99, int(score * 100) + 25)
                    scored_chunks.append(chunk_copy)

            # Sort descending by relevance
            scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
            return scored_chunks[:top_k]

        except Exception:
            return []

    def _extract_definition_or_best_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Intelligently identifies definitions ('What is X', 'Define X') or key sentences.
        """
        q_lower = query.lower().strip()
        query_keywords = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', q_lower) if w not in {"what", "how", "why", "who", "when", "where", "the", "and", "for", "with"}]

        # Check for target subject (e.g. "python", "transformer", "sql")
        target_subject = query_keywords[0] if query_keywords else ""

        extracted_candidates = []

        for c in chunks:
            raw_text = c.get("text", "")
            # Split by newlines and sentence boundaries
            segments = [seg.strip() for seg in re.split(r'[\n\r]+|[.!?]+\s+', raw_text) if len(seg.strip()) > 15]

            for seg in segments:
                clean_seg = clean_sentence(seg)
                if not clean_seg or len(clean_seg) < 15:
                    continue

                seg_lower = clean_seg.lower()

                # Score candidate
                score = 0

                # 1. Check definition patterns: "X is a...", "X refers to..."
                if target_subject and re.search(r'\b' + re.escape(target_subject) + r'\b\s+(?:is|refers to|means|represents|defined as|is a|is an)\b', seg_lower):
                    score += 50

                # 2. Check keyword overlaps
                matched_kws = sum(1 for kw in query_keywords if kw in seg_lower)
                score += (matched_kws * 10)

                # Penalize raw code / messy comment lines
                if re.search(r'(=|#|\{|\}|\(\)|print\(|def\s+|class\s+)', clean_seg):
                    score -= 15

                # Penalize question sentences
                if clean_seg.endswith("?"):
                    score -= 10

                if score > 0:
                    extracted_candidates.append((score, clean_seg, c["title"]))

        if extracted_candidates:
            extracted_candidates.sort(key=lambda x: x[0], reverse=True)
            best_candidate = extracted_candidates[0][1]
            if not best_candidate.endswith("."):
                best_candidate += "."
            return best_candidate

        # Fallback to top chunk cleaned excerpt
        if chunks:
            fallback = clean_sentence(chunks[0]["text"][:240])
            return fallback + ("..." if len(fallback) >= 230 else "")

        return "No direct summary available."

    def synthesize_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes a structured, conversational AI response with clean formatting and citations.
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

        # 1. Direct answer extraction
        direct_answer = self._extract_definition_or_best_answer(query, retrieved_chunks)

        # 2. Build Citations Metadata
        citations = []
        seen_titles = set()
        for idx, c in enumerate(retrieved_chunks, 1):
            if c["title"] not in seen_titles:
                seen_titles.add(c["title"])
                clean_snippet = clean_sentence(c["text"][:180]) + ("..." if len(c["text"]) > 180 else "")
                citations.append({
                    "citation_id": idx,
                    "title": c["title"],
                    "category": c["category"],
                    "tags": c.get("tags", []),
                    "confidence": f"{c.get('confidence_pct', 80)}%",
                    "excerpt": clean_snippet
                })

        # 3. Key Findings & Vault Highlights
        key_findings = []
        for c in retrieved_chunks[:3]:
            # Find clean informative sentences from this chunk
            lines = [clean_sentence(l) for l in re.split(r'[\n\r]+|[.!?]+\s+', c["text"]) if len(clean_sentence(l)) > 25 and not clean_sentence(l).endswith("?")]
            if lines:
                first_line = lines[0]
                if not first_line.endswith("."):
                    first_line += "."
                key_findings.append(f"• **{c['title']}** (`{c['category']}`): {first_line}")

        findings_block = "\n".join(key_findings) if key_findings else f"• {direct_answer}"

        # 4. Assemble Final Markdown Output
        answer_markdown = f"""### 🎯 Direct Answer
{direct_answer}

---

### 📋 Key Findings from Vault
{findings_block}

---

### 📚 Sources & Citations
"""
        for cit in citations:
            answer_markdown += f"- **[{cit['citation_id']}] {cit['title']}** (`{cit['category']}`) — *Confidence: {cit['confidence']}*\n  > \"{cit['excerpt']}\"\n"

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
        """
        chunks = self.build_chunk_corpus(memories, scope_category=scope_category)
        retrieved = self.retrieve_relevant_chunks(query, chunks, top_k=4)
        return self.synthesize_answer(query, retrieved)
