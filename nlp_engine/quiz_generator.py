"""
nlp_engine/quiz_generator.py
Dynamic AI-Powered Study Flashcards & Interactive Quiz Engine for Smart Memory Vault.
Dynamically extracts concepts, definitions, functional relationships, key facts, and bullet points
from user notes, documents, OCR images, PDFs, voice memos, and YouTube transcripts.
"""

import re
import random
from typing import List, Dict, Any, Optional
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize


class StudyQuizEngine:
    """Generates 100% dynamic, context-aware study flashcards and interactive quiz questions."""

    def __init__(self):
        self.stop_words = {
            "the", "this", "that", "these", "those", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should",
            "can", "could", "may", "might", "must", "and", "or", "but", "if", "because", "as",
            "until", "while", "of", "at", "by", "for", "with", "about", "against", "between",
            "into", "through", "during", "before", "after", "above", "below", "to", "from", "up",
            "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "s", "t", "just", "don", "now", "also", "using", "used",
            "which", "what", "etc", "user", "users", "item", "items", "like", "make", "made",
            "get", "got", "one", "two", "three", "well", "see", "way", "even", "new", "want", "use",
            "called", "said", "took", "went", "gave", "look", "looked", "main", "key", "many", "much",
            "every", "across", "along", "without", "within", "since", "know", "known", "learn", "study"
        }

        # Meta-words & structural labels that should never be treated as subject-matter concepts
        self.meta_labels = {
            "example", "examples", "eg", "e.g", "ie", "i.e", "note", "notes", "nb", "n.b",
            "warning", "caution", "tip", "tips", "hint", "hints", "important", "summary",
            "title", "description", "details", "page", "pages", "figure", "figures",
            "table", "tables", "chart", "diagram", "step", "steps", "case", "cases",
            "code", "syntax", "output", "input", "result", "results", "demo", "overview",
            "section", "chapter", "point", "points", "doc", "docs",
            "document", "file", "files", "total", "count", "info", "information",
            "source", "author", "date", "version", "status", "def", "definition", "question"
        }

    def _is_valid_concept(self, term: str) -> bool:
        """Validates that a candidate term is a meaningful domain concept rather than noise or metadata."""
        if not term:
            return False
        t_clean = term.strip().strip(":.-_*").lower()
        if len(t_clean) < 3 or len(t_clean) > 40:
            return False
        if t_clean in self.stop_words or t_clean in self.meta_labels:
            return False
        # Must contain alphabetical letters
        if not re.search(r'[a-zA-Z]', t_clean):
            return False
        # Disallow if starts with a meta-label word (e.g. "Example 1", "Figure 2", "Step 3", "Doc Day-3")
        first_word = t_clean.split()[0]
        if first_word in self.meta_labels:
            return False
        return True

    def _clean_text(self, text: str) -> str:
        """Strips web URLs, file extensions, and noisy spoken artifacts."""
        if not text:
            return ""
        cleaned = re.sub(r'https?://\S+', '', text)
        cleaned = re.sub(r'\b[a-zA-Z0-9_-]+\.(?:pdf|docx|txt|doc|pptx|png|jpg|jpeg|webp)\b', '', cleaned, flags=re.I)
        cleaned = re.sub(r'[\?&]si=[a-zA-Z0-9_-]+', '', cleaned)
        cleaned = re.sub(r'[●■◆★•]+', ' ', cleaned)
        # Strip common meta prefixes at line starts
        cleaned = re.sub(r'(?i)\b(?:Example|Note|Tip|Warning|Summary|Output|Input)\s*:\s*', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _extract_sentences_and_points(self, text: str) -> List[str]:
        """Splits text into clean individual sentences and bullet points."""
        cleaned = self._clean_text(text)
        if not cleaned:
            return []
        
        raw_lines = [line.strip("- *•\t\r") for line in cleaned.splitlines() if len(line.strip("- *•\t\r")) >= 15]
        if not raw_lines:
            raw_lines = [cleaned]

        all_sents = []
        for line in raw_lines:
            try:
                sents = sent_tokenize(line)
            except Exception:
                sents = [s.strip() for s in re.split(r'[.!?]+', line) if len(s.strip()) > 15]
            all_sents.extend(sents)

        combined = []
        seen = set()
        for s in all_sents:
            s_clean = s.strip()
            # Strip list numbers like "1.", "1)"
            s_clean = re.sub(r'^\d+[\.\)]\s*', '', s_clean).strip()
            if len(s_clean) >= 18 and len(s_clean.split()) >= 3:
                s_lower = s_clean.lower()
                if s_lower not in seen:
                    seen.add(s_lower)
                    combined.append(s_clean)
        return combined

    def _extract_dynamic_concepts(self, text: str, memories: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """Dynamically identifies key concepts, terms, tools, and noun phrases from the text and memories."""
        concepts = []

        # 1. Look for Key: Value or Term - Definition formats (e.g. "Data Types: Classification of values")
        colon_matches = re.findall(r'(?:^|\n)\s*([A-Z][a-zA-Z0-9_\s-]{2,30})\s*[:\-–]\s*([^\n]{10,})', text)
        for term, _ in colon_matches:
            if self._is_valid_concept(term):
                concepts.append(term.strip())

        # 2. Extract multi-word capitalized phrases (e.g. "Type Conversions", "Data Types", "Neural Network")
        multi_cap = re.findall(r'\b[A-Z][a-zA-Z0-9_-]+(?:\s+[A-Z][a-zA-Z0-9_-]+)+\b', text)
        for mc in multi_cap:
            if self._is_valid_concept(mc):
                concepts.append(mc.strip())

        # 3. Extract single capitalized nouns
        single_cap = re.findall(r'\b[A-Z][a-zA-Z0-9_-]{3,}\b', text)
        for sc in single_cap:
            if self._is_valid_concept(sc):
                concepts.append(sc.strip())

        # 4. Extract technical terms / quoted phrases / bracketed terms
        quoted = re.findall(r'["\']([^"\']{3,35})["\']', text)
        for q in quoted:
            if self._is_valid_concept(q):
                concepts.append(q.strip())

        # 5. Extract keywords from memory tags and titles if available
        if memories:
            for m in memories:
                t = m.get("title", "").split("|")[0].strip()
                t_clean = re.sub(r'^(?:Image:\s*|Voice Note -?\s*|Doc:\s*|YouTube:\s*)', '', t, flags=re.I).strip()
                if self._is_valid_concept(t_clean):
                    concepts.append(t_clean)
                for tag in (m.get("tags") or []):
                    if self._is_valid_concept(tag):
                        concepts.append(tag.title())

        # 6. Extract frequent meaningful domain words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        meaningful = [w for w in words if self._is_valid_concept(w)]
        counts = Counter(meaningful)
        for word, count in counts.most_common(15):
            concepts.append(word.title())

        # Deduplicate while preserving order and prioritizing multi-word terms
        multi_word_concepts = [c for c in concepts if " " in c]
        unique_concepts = []
        seen = set()
        for c in concepts:
            c_clean = c.strip()
            c_lower = c_clean.lower()
            if c_lower in seen or not self._is_valid_concept(c_clean):
                continue
            # If it's a single word already contained in a multi-word concept, skip to avoid redundancy
            if " " not in c_clean and any(c_lower in mwc.lower().split() for mwc in multi_word_concepts):
                continue
            seen.add(c_lower)
            unique_concepts.append(c_clean)

        return unique_concepts

    def _get_dynamic_vault_distractor_pool(self, memories: Optional[List[Dict[str, Any]]], exclude: str = "") -> List[str]:
        """Harvests real terms and concepts across all vault memories to ensure distractors are 100% dynamic."""
        pool = []
        if memories:
            for m in memories:
                t = m.get("title", "").split("|")[0].strip()
                t_clean = re.sub(r'^(?:Image:\s*|Voice Note -?\s*|Doc:\s*|YouTube:\s*)', '', t, flags=re.I).strip()
                if self._is_valid_concept(t_clean) and t_clean.lower() != exclude.lower():
                    pool.append(t_clean)
                for tag in (m.get("tags") or []):
                    if self._is_valid_concept(tag) and tag.lower() != exclude.lower():
                        pool.append(tag.title())
                desc_words = re.findall(r'\b[A-Z][a-zA-Z0-9_-]+\b', m.get("description", ""))
                for dw in desc_words:
                    if self._is_valid_concept(dw) and dw.lower() != exclude.lower():
                        pool.append(dw)
        return list(dict.fromkeys(pool))

    def _generate_dynamic_distractors(
        self,
        correct_answer: str,
        local_pool: List[str],
        memories: Optional[List[Dict[str, Any]]] = None,
        count: int = 3
    ) -> List[str]:
        """Generates realistic, dynamic multiple-choice distractors derived from context and vault notes."""
        cleaned_correct = correct_answer.strip().lower()
        candidates = [
            p.strip() for p in local_pool
            if p.strip().lower() != cleaned_correct and len(p.strip()) >= 2
        ]

        if len(candidates) < count and memories:
            vault_pool = self._get_dynamic_vault_distractor_pool(memories, exclude=correct_answer)
            for vp in vault_pool:
                if vp.lower() != cleaned_correct and vp.lower() not in [c.lower() for c in candidates]:
                    candidates.append(vp)

        if len(candidates) >= count:
            return random.sample(candidates, count)

        dynamic_fallbacks = [
            f"Alternative formulation of {correct_answer[:15]}",
            "Secondary Reference Factor",
            "Independent Variable Metric",
            "Structural Analysis Method",
            "Dynamic Execution Module",
            "Empirical Verification Model",
            "Contextual Evaluation Protocol",
            "Operational Baseline Standard"
        ]
        combined = candidates + [f for f in dynamic_fallbacks if f.lower() != cleaned_correct]
        deduped = list(dict.fromkeys(combined))
        return random.sample(deduped, count) if len(deduped) >= count else deduped[:count]

    def generate_flashcards(
        self,
        text: str,
        title: str = "",
        memories: Optional[List[Dict[str, Any]]] = None,
        num_cards: int = 8
    ) -> List[Dict[str, Any]]:
        """Generates comprehensive, dynamic active-recall study flashcards directly from note content."""
        cards = []
        seen_fronts = set()
        back_counts = Counter()
        sentences = self._extract_sentences_and_points(text)
        concepts = self._extract_dynamic_concepts(text, memories)

        # 1. Check for Definition Patterns (e.g. "Data Types: Classification of data values")
        for sent in sentences:
            colon_match = re.match(r'^([A-Z][a-zA-Z0-9_\s-]{2,30})\s*[:\-–]\s*(.{15,})', sent)
            if colon_match:
                term, explanation = colon_match.group(1).strip(), colon_match.group(2).strip()
                if self._is_valid_concept(term):
                    front = f"What is the definition and role of **{term}**?"
                    if front.lower() not in seen_fronts and back_counts[explanation.lower()] < 2:
                        seen_fronts.add(front.lower())
                        back_counts[explanation.lower()] += 1
                        cards.append({
                            "concept": term.title(),
                            "front": front,
                            "back": explanation,
                            "topic": "Core Concept"
                        })

            # Check for "X is a/an/the..." or "X refers to..."
            def_match = re.search(
                r'^(?:[A-Z][a-zA-Z0-9_\s-]{1,25})\s+(?:is\s+(?:a|an|the|defined\s+as)|are\s+(?:the)?|refers\s+to|serves\s+as|enables|calculates|manages|handles)\s+(.+)',
                sent,
                re.IGNORECASE
            )
            if def_match:
                words = sent.split()
                subject_candidates = [w for w in words[:4] if self._is_valid_concept(w)]
                if subject_candidates:
                    subject = " ".join(subject_candidates[:2]).strip(",:.")
                    if self._is_valid_concept(subject):
                        front = f"What does **{subject}** accomplish in this context?"
                        if front.lower() not in seen_fronts and back_counts[sent.lower()] < 2:
                            seen_fronts.add(front.lower())
                            back_counts[sent.lower()] += 1
                            cards.append({
                                "concept": subject.title(),
                                "front": front,
                                "back": sent.strip(),
                                "topic": "Concept Purpose"
                            })

        # 2. Key Concepts in Sentences
        for c in concepts:
            if len(cards) >= num_cards:
                break
            matching_sents = [s for s in sentences if re.search(rf'\b{re.escape(c)}\b', s, re.I)]
            for target_sent in matching_sents:
                if back_counts[target_sent.lower()] < 2:
                    front = f"Explain the context and significance of **{c}**:"
                    if front.lower() not in seen_fronts:
                        seen_fronts.add(front.lower())
                        back_counts[target_sent.lower()] += 1
                        cards.append({
                            "concept": c,
                            "front": front,
                            "back": target_sent.strip(),
                            "topic": "Key Insight"
                        })
                        break

        # 3. Memory Summary Takeaways
        if memories and len(cards) < num_cards:
            for m in memories:
                if len(cards) >= num_cards:
                    break
                m_title = m.get("title", "").split("|")[0].strip()
                m_title = re.sub(r'^(?:Image:\s*|Voice Note -?\s*|Doc:\s*|YouTube:\s*)', '', m_title, flags=re.I).strip()
                m_cat = m.get("category", "General")
                m_summ = m.get("summary", "").strip() or m.get("description", "")[:250]
                if m_title and m_summ and self._is_valid_concept(m_title) and back_counts[m_summ.lower()] < 2:
                    front = f"What are the main takeaways and key concepts of **{m_title}**?"
                    if front.lower() not in seen_fronts:
                        seen_fronts.add(front.lower())
                        back_counts[m_summ.lower()] += 1
                        cards.append({
                            "concept": f"{m_cat}: {m_title[:28]}",
                            "front": front,
                            "back": m_summ,
                            "topic": f"{m_cat} Summary"
                        })

        # 4. Fallback from remaining sentences if text is concise
        if len(cards) < num_cards and sentences:
            for idx, s in enumerate(sentences):
                if len(cards) >= num_cards:
                    break
                if back_counts[s.lower()] < 2 and len(s) > 25:
                    front = f"Recall the key principle or fact:\n*\"{s[:120]}...\"*?"
                    if front.lower() not in seen_fronts:
                        seen_fronts.add(front.lower())
                        back_counts[s.lower()] += 1
                        cards.append({
                            "concept": f"Fact #{len(cards)+1}",
                            "front": front,
                            "back": s,
                            "topic": "Knowledge Recall"
                        })

        # 5. Guaranteed fallback card if completely empty
        if not cards:
            clean_title = re.sub(r'^(?:Image:\s*|Voice Note -?\s*|Doc:\s*|YouTube:\s*)', '', title.split("|")[0].strip(), flags=re.I) or "Vault Knowledge Note"
            cards.append({
                "concept": clean_title,
                "front": f"What key information is recorded under **{clean_title}**?",
                "back": self._clean_text(text)[:300] or "Knowledge records stored in your Smart Memory Vault.",
                "topic": "Overview"
            })

        return cards[:num_cards]

    def generate_quiz(
        self,
        text: str,
        title: str = "",
        memories: Optional[List[Dict[str, Any]]] = None,
        num_questions: int = 6
    ) -> List[Dict[str, Any]]:
        """Generates dynamic, high-engagement multiple-choice quiz questions with contextual options and explanations."""
        quiz_questions = []
        seen_q = set()
        sentences = self._extract_sentences_and_points(text)
        concepts = self._extract_dynamic_concepts(text, memories)

        # 1. Cloze / Fill-in-the-blank Concept Questions
        for sent in sentences:
            if len(quiz_questions) >= num_questions:
                break
            for c in concepts:
                if len(c) >= 3 and self._is_valid_concept(c) and re.search(rf'\b{re.escape(c)}\b', sent, re.I):
                    cloze_sent = re.sub(rf'\b{re.escape(c)}\b', '___________', sent, count=1, flags=re.I)
                    q_text = f"Fill in the blank: \"{cloze_sent}\""
                    if q_text.lower() not in seen_q:
                        seen_q.add(q_text.lower())
                        distractors = self._generate_dynamic_distractors(c, concepts, memories=memories, count=3)
                        options = [c] + distractors
                        random.shuffle(options)

                        quiz_questions.append({
                            "id": len(quiz_questions) + 1,
                            "type": "Fill in the blank",
                            "question": q_text,
                            "options": options,
                            "correct_answer": c,
                            "explanation": f"✅ **Correct Answer:** **{c}**\n\n📖 *Context:* \"{sent}\""
                        })
                        break

        # 2. Concept Definition & Capability Questions
        for c in concepts:
            if len(quiz_questions) >= num_questions:
                break
            if not self._is_valid_concept(c):
                continue
            matching_sents = [s for s in sentences if re.search(rf'\b{re.escape(c)}\b', s, re.I)]
            if matching_sents:
                target_sent = matching_sents[0]
                q_text = f"According to your notes, what is associated with or describes **{c}**?"
                if q_text.lower() not in seen_q:
                    seen_q.add(q_text.lower())
                    
                    correct_opt = target_sent if len(target_sent) <= 90 else target_sent[:87] + "..."
                    other_sents = [
                        s if len(s) <= 90 else s[:87] + "..."
                        for s in sentences if s != target_sent and len(s) > 15
                    ]
                    distractors = self._generate_dynamic_distractors(correct_opt, other_sents, memories=memories, count=3)
                    options = [correct_opt] + distractors
                    random.shuffle(options)

                    quiz_questions.append({
                        "id": len(quiz_questions) + 1,
                        "type": "Concept Identification",
                        "question": q_text,
                        "options": options,
                        "correct_answer": correct_opt,
                        "explanation": f"✅ **Correct Fact for {c}:** \"{target_sent}\""
                    })

        # 3. Purpose & Architecture Questions from Memories
        if memories and len(quiz_questions) < num_questions:
            for m in memories:
                if len(quiz_questions) >= num_questions:
                    break
                m_title = m.get("title", "").split("|")[0].strip()
                m_title = re.sub(r'^(?:Image:\s*|Voice Note -?\s*|Doc:\s*|YouTube:\s*)', '', m_title, flags=re.I).strip()
                m_summ = m.get("summary", "").strip() or m.get("description", "")[:120]
                if m_title and m_summ and len(m_summ) > 20 and self._is_valid_concept(m_title):
                    q_text = f"What is the primary scope or takeaway of '{m_title}'?"
                    if q_text.lower() not in seen_q:
                        seen_q.add(q_text.lower())
                        correct_opt = (m_summ[:85] + "...") if len(m_summ) > 85 else m_summ
                        other_summaries = [
                            m2.get("summary", "")[:85] + "..."
                            for m2 in memories
                            if m2.get("id") != m.get("id") and m2.get("summary")
                        ]
                        distractors = self._generate_dynamic_distractors(correct_opt, other_summaries, memories=memories, count=3)
                        options = [correct_opt] + distractors
                        random.shuffle(options)

                        quiz_questions.append({
                            "id": len(quiz_questions) + 1,
                            "type": "Note Comprehension",
                            "question": q_text,
                            "options": options,
                            "correct_answer": correct_opt,
                            "explanation": f"✅ **Summary of {m_title}:** \"{m_summ}\""
                        })

        # 4. Fallback if still under count
        if not quiz_questions and title:
            clean_title = re.sub(r'^(?:Image:\s*|Voice Note -?\s*|Doc:\s*|YouTube:\s*)', '', title.split("|")[0].strip(), flags=re.I) or "Vault Knowledge Note"
            correct_opt = f"Core knowledge regarding {clean_title}"
            distractors = ["Unrelated background process", "External network socket", "Static hardware baseline"]
            options = [correct_opt] + distractors
            random.shuffle(options)
            quiz_questions.append({
                "id": 1,
                "type": "General Review",
                "question": f"What is the main topic covered in **{clean_title}**?",
                "options": options,
                "correct_answer": correct_opt,
                "explanation": f"This active recall set is derived dynamically from your personal knowledge records on **{clean_title}**."
            })

        return quiz_questions[:num_questions]


# Singleton Engine Instance
quiz_engine = StudyQuizEngine()
