"""
nlp_engine/summarizer.py
Extractive Text & Document Summarizer (Paragraphs, Bullet points & Podcast Scripts)
"""

import re
from collections import Counter
from typing import List, Dict, Any, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize


def clean_sentence(text: str) -> str:
    """Cleans sentence by stripping weird bullet glyphs, excess spaces, and noisy characters."""
    if not text:
        return ""
    # Remove markdown headers and formatting
    cleaned = re.sub(r'^[#*\-:\s●•■◆▪▸►]+\s*', '', text).strip()
    # Strip URL links
    cleaned = re.sub(r'http\S+|www\.\S+', '', cleaned)
    # Remove standalone braces or brackets
    cleaned = re.sub(r'[\{\}\<\>]+', ' ', cleaned)
    # Normalize multiple whitespaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def clean_sentence_line(text: str) -> str:
    """Cleans trailing code markers or example words from sentence end."""
    text = re.sub(r'\s*(?:Example|Examples|Python|Output|None|Operations on Strings)\s*:?$', '', text, flags=re.I).strip()
    return text


class TextSummarizer:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
                "is", "was", "are", "were", "be", "been", "being", "have", "has", "had",
                "do", "does", "did", "can", "could", "will", "would", "should", "of", "by"
            }

        # Indicators to prioritize core definitions and conceptual explanations
        self.boost_keywords = {
            "key", "important", "main", "primary", "essential", "critical", "goal", "objective",
            "feature", "features", "architecture", "implemented", "built", "uses", "utilizes",
            "developed", "result", "results", "conclusion", "conclude", "summary", "overview",
            "benefit", "benefits", "technique", "process", "framework", "component", "method",
            "definition", "defines", "refers", "purpose", "highlight", "highlights", "immutable",
            "mutable", "sequence", "ordered", "collection", "operation", "operations", "syntax",
            "indexing", "slicing", "concatenation", "repetition", "membership", "function", "methods"
        }

    def extract_clean_concept_sentences(self, text: str) -> List[str]:
        """
        Extracts high-quality conceptual and explanatory sentences from notes/documents/PDFs,
        filtering out code blocks, output dumps, and raw execution logs.
        """
        if not text or not text.strip():
            return []

        # Split any embedded numbered lists in text (e.g. "1. Item ... 2. Item ...")
        text = re.sub(r'(?<=[a-zA-Z0-9\.\)\'\"\`])\s+(?=[0-9]+[\.\)]\s+)', '\n', text)

        normalized = re.sub(r'[\r\n]+', '\n', text)
        raw_lines = [l.strip() for l in normalized.split('\n') if l.strip()]

        cleaned_items = []
        curr = ""

        for l in raw_lines:
            # Skip code execution lines, examples, outputs
            if re.match(r'^(print\(|def\s+|class\s+|#|import\s+|from\s+|str\d+\s*=|result\s*=|text\[|names\s*=|numbers\s*=|Output:|None|Example:|Python|Examples:)', l):
                if curr:
                    c = clean_sentence_line(curr)
                    if len(c) >= 15:
                        cleaned_items.append(c)
                    curr = ""
                continue

            is_numbered = bool(re.match(r'^[0-9]+[\.\)]\s*', l))
            line_clean = re.sub(r'^[0-9]+[\.\)]\s*', '', l)
            line_clean = re.sub(r'^[#*\-:\s●•■◆▪▸►]+\s*', '', line_clean).strip()

            if not line_clean or len(line_clean) < 10:
                continue

            words = line_clean.split()
            # Skip short headers without explanatory verbs
            if len(words) <= 3 and not re.search(r'\b(is|are|means|refers|used|can|returns|contains|supports)\b', line_clean, re.I):
                if curr:
                    c = clean_sentence_line(curr)
                    if len(c) >= 15:
                        cleaned_items.append(c)
                    curr = ""
                continue

            if is_numbered and curr:
                c = clean_sentence_line(curr)
                if len(c) >= 15:
                    cleaned_items.append(c)
                curr = line_clean
            elif curr:
                if curr.endswith(('(', '[', '{', ',', ':', '"', "'", '-')) or not curr[-1] in '.!?':
                    curr += ' ' + line_clean
                else:
                    c = clean_sentence_line(curr)
                    if len(c) >= 15:
                        cleaned_items.append(c)
                    curr = line_clean
            else:
                curr = line_clean

        if curr:
            c = clean_sentence_line(curr)
            if len(c) >= 15:
                cleaned_items.append(c)

        final_sentences = []
        seen = set()
        for item in cleaned_items:
            try:
                sub_sents = sent_tokenize(item)
            except Exception:
                sub_sents = re.split(r'(?<=[.!?])\s+', item)

            for s_raw in sub_sents:
                s = clean_sentence_line(s_raw)
                # Skip example snippets or trivial placeholder phrases
                if re.search(r'^(this is a multi-line|python!|hello world)', s, re.I):
                    continue
                if len(s) >= 18 and len(re.findall(r'[a-zA-Z]', s)) >= 10:
                    if not s.endswith(('.', '!', '?', ':')):
                        s += '.'
                    s_lower = s.lower()
                    if s_lower not in seen:
                        seen.add(s_lower)
                        final_sentences.append(s)

        return final_sentences

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        """Generates a concise, high-density conceptual summary."""
        sentences = self.extract_clean_concept_sentences(text)
        if not sentences:
            return ""

        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text) if w.lower() not in self.stop_words]
        word_freq = Counter(words)
        max_freq = max(word_freq.values()) if word_freq else 1
        norm_freq = {k: v / max_freq for k, v in word_freq.items()}

        sentence_scores = {}
        total_sents = len(sentences)

        for idx, sent in enumerate(sentences):
            sent_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', sent)]
            base_score = sum(norm_freq.get(w, 0) for w in sent_words)
            boost = sum(2.0 for w in sent_words if w in self.boost_keywords)

            # Definition boost
            if re.search(r'\b(is a|is an|are|refers to|used to|defined as|process of)\b', sent, re.I):
                boost += 4.0

            pos_weight = 1.3 if (idx < max(2, int(total_sents * 0.2))) or (idx >= total_sents - 2) else 1.0
            sentence_scores[idx] = (base_score + boost) * pos_weight

        top_indices = sorted(sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences])
        return " ".join([sentences[i] for i in top_indices])

    def generate_bullets(self, text: str, max_points: int = 5) -> List[str]:
        """Generates rich, formatted bullet points highlighting key concepts."""
        sentences = self.extract_clean_concept_sentences(text)
        if not sentences:
            return []

        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text) if w.lower() not in self.stop_words]
        word_freq = Counter(words)
        max_freq = max(word_freq.values()) if word_freq else 1
        norm_freq = {k: v / max_freq for k, v in word_freq.items()}

        scored_sents = []
        for idx, s in enumerate(sentences):
            sw = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', s)]
            score = sum(norm_freq.get(w, 0) for w in sw)
            score += sum(2.0 for w in sw if w in self.boost_keywords)
            if re.search(r'\b(is a|is an|are|refers to|used to|defined as|meaning|supports|provides|allows)\b', s, re.I):
                score += 3.0
            scored_sents.append((score, idx, s))

        scored_sents.sort(key=lambda x: x[0], reverse=True)
        selected = sorted(scored_sents[:max_points], key=lambda x: x[1])

        formatted_bullets = []
        for _, _, sent in selected:
            if " - " in sent:
                parts = sent.split(" - ", 1)
                formatted_bullets.append(f"• **{parts[0].strip()}:** {parts[1].strip()}")
            elif ":" in sent and not sent.endswith(":"):
                parts = sent.split(":", 1)
                if len(parts[0].split()) <= 4:
                    formatted_bullets.append(f"• **{parts[0].strip()}:** {parts[1].strip()}")
                else:
                    formatted_bullets.append(f"• {sent}")
            else:
                formatted_bullets.append(f"• {sent}")

        return formatted_bullets

    def generate_podcast_narrative(self, title: str, category: str, content: str) -> str:
        """
        Creates an engaging, articulate podcast narration script (~1.5-2 minutes).
        Selects key ideas and expresses them in natural, easy-to-understand spoken style.
        """
        sentences = self.extract_clean_concept_sentences(content)
        if not sentences:
            return f"Welcome to your Smart Memory Vault audio briefing. Today we're exploring {title}, categorized under {category}. No detailed notes were found for this item."

        key_summary = self.summarize(content, max_sentences=2)
        bullets = self.generate_bullets(content, max_points=3)
        clean_bullets = [clean_sentence(b.replace('• **', '').replace('**:', ':').replace('•', '')) for b in bullets]

        script_parts = [
            f"Welcome to your Smart Memory Vault audio briefing. Today, we're exploring {title}, filed in your {category} vault.",
            f"Here is the essential overview: {key_summary}"
        ]

        if clean_bullets:
            bullet_text = "Let's review the key highlights to remember. "
            for i, b in enumerate(clean_bullets, 1):
                bullet_text += f"First, {b} " if i == 1 else f"Next, {b} "
            script_parts.append(bullet_text)

        script_parts.append(f"In summary, {title} provides essential domain knowledge in your {category} vault. Thank you for listening, and keep up your daily learning momentum!")

        return " ".join(script_parts)

    def generate_vault_digest_narrative(self, memories: List[Dict[str, Any]]) -> str:
        """
        Creates an executive multi-document digest podcast script (~2 minutes).
        Synthesizes top memories into a cohesive, high-level briefing.
        """
        if not memories:
            return "Welcome to your Smart Memory Vault executive briefing. Your vault is currently empty. Add your study notes, documents, and projects to generate your daily podcast."

        total_count = len(memories)
        top_mems = memories[:4]
        categories = list(set(m.get("category", "General") for m in top_mems))

        script = (
            f"Welcome to your Smart Memory Vault executive audio briefing. "
            f"You currently have {total_count} active memory records across {len(categories)} domains including {', '.join(categories[:3])}. "
            f"Here is your curated knowledge digest for today. "
        )

        for idx, m in enumerate(top_mems, 1):
            m_title = m.get("title", f"Memory {idx}")
            m_cat = m.get("category", "General")
            m_desc = m.get("summary") or m.get("description", "")
            m_sent = self.summarize(m_desc, max_sentences=1)
            if not m_sent:
                m_sent = clean_sentence(m_desc[:150])
            script += f"First, in your {m_cat} records: for {m_title}, {m_sent} " if idx == 1 else f"Next, under {m_cat}: in {m_title}, {m_sent} "

        script += (
            "Overall, your knowledge vault is actively growing with solid cross-disciplinary insights. "
            "Keep reinforcing your concepts with active recall. Have a productive and successful day!"
        )

        return script
