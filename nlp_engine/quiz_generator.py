"""
nlp_engine/quiz_generator.py
AI-Powered Study Flashcards & Interactive Quiz Engine for Smart Memory Vault
Generates intelligent study cards and context-aware multiple-choice questions
from notes, interview sheets, documents & PDFs.
"""

import re
import random
from typing import List, Dict, Any
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize

# High-quality technical distractors categorized by topic
DOMAIN_DISTRACTOR_POOLS = {
    "python_core": [
        "Decorator", "Generator", "Iterator", "List Comprehension", 
        "Global Interpreter Lock (GIL)", "Garbage Collector", "Lambda Function", "Context Manager"
    ],
    "data_structures": [
        "Tuple", "List", "Dictionary", "Set", "Linked List", 
        "Binary Search Tree", "Hash Map", "Stack", "Queue", "Heap"
    ],
    "oop": [
        "Inheritance", "Polymorphism", "Encapsulation", "Abstraction", 
        "Method Overriding", "Class Constructor", "Interface", "Multiple Inheritance"
    ],
    "web_db": [
        "REST API", "Database Index", "ORM Query", "JWT Authentication", 
        "Middleware", "Caching Layer", "Connection Pool", "Foreign Key"
    ],
    "general_cs": [
        "Time Complexity", "Space Complexity", "Recursion", "Dynamic Programming", 
        "Concurrency", "Serialization", "Multithreading", "Asyncio"
    ]
}

FILTER_NOISE_TOKENS = {
    "difference", "differences", "document", "documents", "pdf", "docx", "file", "files",
    "page", "pages", "author", "authors", "summary", "notes", "note", "report", "reports",
    "question", "questions", "answer", "answers", "example", "examples", "sample", "samples",
    "sowmya", "tummala", "kumar", "sharma", "singh", "patel", "reddy", "john", "doe",
    "using", "used", "which", "what", "where", "when", "there", "their", "about", "above",
    "below", "following", "given", "based", "first", "second", "third", "also", "into",
    "from", "with", "have", "more", "most", "some", "such", "only", "other", "same",
    "even", "like", "make", "made", "good", "well", "very", "much", "many", "type", "types",
    "user", "users", "name", "names", "email", "phone", "date", "time", "year", "month",
    "true", "false", "null", "none", "item", "items", "text", "content", "data", "info",
    "overview", "scope", "section", "chapter", "topic", "topics", "doc", "title"
}


class StudyQuizEngine:
    """Generates intelligent study flashcards and interactive quiz questions from vault memories."""

    def __init__(self):
        pass

    def _clean_sentences(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        
        # Strip document headers, author lines, and doc titles before splitting
        lines = []
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            if re.match(r'^(?:author|doc|document|page|file|date|title|created|email|phone)[\s:]+', line_str, re.I):
                continue
            if re.match(r'^[a-z0-9_-]+\.(?:pdf|docx|txt|doc|pptx)$', line_str, re.I):
                continue
            if len(line_str) < 15 and not line_str.endswith("?"):
                continue
            lines.append(line_str)

        sanitized_text = " ".join(lines)
        try:
            sentences = sent_tokenize(sanitized_text)
        except Exception:
            sentences = [s.strip() for s in re.split(r'[.!?\n]+', sanitized_text) if s.strip()]
        
        cleaned = []
        for s in sentences:
            s_clean = s.strip()
            # Clean up leading question numbers like "1. ", "2) "
            s_clean = re.sub(r'^\d+[\.\)]\s*', '', s_clean)
            if len(s_clean) > 25 and not s_clean.startswith("http"):
                cleaned.append(s_clean)
        return cleaned

    def _extract_qa_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extracts explicit Q&A patterns (e.g., 'Q: ... A: ...' or '1. What is ...? ...')."""
        qa_pairs = []
        
        # Pattern 1: Explicit Q: ... A: ...
        pattern1 = re.findall(
            r'(?:Q(?:uestion)?[\s\d.:)]+)(.+?)\s*(?:A(?:nswer)?[\s.:)]+)(.+?)(?=(?:Q(?:uestion)?[\s\d.:)]+)|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        for q, a in pattern1:
            q_clean = q.strip().replace('\n', ' ')
            a_clean = a.strip().replace('\n', ' ')
            if len(q_clean) > 8 and len(a_clean) > 15:
                qa_pairs.append({
                    "question": q_clean if q_clean.endswith("?") else f"{q_clean}?",
                    "answer": a_clean[:350]
                })

        # Pattern 2: Numbered questions ending in ? followed by response text
        pattern2 = re.findall(
            r'(?:^|\n)\s*(?:\d+[\.\)]\s*)([A-Z][^\n\?]+\?)\s*\n+([^\n\d]+(?:\n[^\n\d]+)*)',
            text
        )
        for q, a in pattern2:
            q_clean = q.strip().replace('\n', ' ')
            a_clean = a.strip().replace('\n', ' ')
            if len(q_clean) > 8 and len(a_clean) > 15 and not any(p["question"] == q_clean for p in qa_pairs):
                qa_pairs.append({
                    "question": q_clean,
                    "answer": a_clean[:350]
                })

        return qa_pairs

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extracts key technical entities and concepts, strictly filtering out noise."""
        words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', text)
        lower_technical = re.findall(
            r'\b(?:decorator|decorators|generator|generators|iterator|iterators|tuple|tuples|list|lists|dictionary|set|sets|class|classes|inheritance|polymorphism|encapsulation|recursion|concurrency|multithreading|asyncio|database|orm|api|token|gil)\b',
            text,
            re.IGNORECASE
        )
        all_terms = [w.title() for w in words + lower_technical if len(w) > 3 and w.lower() not in FILTER_NOISE_TOKENS]
        counts = Counter(all_terms)
        return [term for term, _ in counts.most_common(15)]

    def generate_flashcards(self, text: str, title: str = "") -> List[Dict[str, str]]:
        """Generates conceptual, technically rich Q&A flashcards from memory text."""
        cards = []
        seen_concepts = set()

        # 1. First priority: Extract explicit Q&A pairs from text if present
        qa_pairs = self._extract_qa_blocks(text)
        for qa in qa_pairs:
            q_text = qa["question"]
            
            # Format clean concept badge
            concept_label = "Concept Review"
            if "difference between" in q_text.lower():
                diff_match = re.search(r'difference between\s+([A-Za-z0-9_-]+)\s+(?:and|&)\s+([A-Za-z0-9_-]+)', q_text, re.I)
                if diff_match:
                    concept_label = f"{diff_match.group(1).title()} vs {diff_match.group(2).title()}"
                else:
                    concept_label = "Comparison Analysis"
            elif "gil" in q_text.lower() or "global interpreter lock" in q_text.lower():
                concept_label = "Python GIL"
            elif "decorator" in q_text.lower():
                concept_label = "Python Decorators"
            else:
                words = [w.title() for w in re.findall(r'\b[A-Za-z]{3,}\b', q_text) if w.lower() not in FILTER_NOISE_TOKENS]
                if words:
                    concept_label = " ".join(words[:2])

            if concept_label not in seen_concepts:
                seen_concepts.add(concept_label)
                cards.append({
                    "concept": concept_label,
                    "front": q_text,
                    "back": qa["answer"]
                })

        sentences = self._clean_sentences(text)

        # 2. Extract Concept Definitions & Mechanics
        for sent in sentences:
            if len(cards) >= 8:
                break
            
            # Definition matching: "X is a Y that does Z", "X refers to Y"
            def_match = re.search(
                r'^(?:[A-Z][a-z0-9_-]*\s+)?([A-Za-z0-9_-]{3,30})\s+(?:is\s+(?:a|an|the|defined\s+as)|are\s+(?:the)?|refers\s+to|serves\s+as|is\s+used\s+(?:to|for)|provides|allows)\s+(.+)',
                sent,
                re.IGNORECASE
            )
            if def_match:
                subject = def_match.group(1).strip()
                if subject.lower() in FILTER_NOISE_TOKENS:
                    continue

                subj_title = subject.title()
                if subj_title not in seen_concepts:
                    seen_concepts.add(subj_title)
                    cards.append({
                        "concept": subj_title,
                        "front": f"What is **{subj_title}** and how does it function?",
                        "back": sent
                    })

            # Comparison matching
            diff_match = re.search(
                r'(?:difference\s+between|differences\s+between|distinction\s+between)\s+([A-Za-z0-9_-]+)\s+(?:and|&|vs\.?)\s+([A-Za-z0-9_-]+)',
                sent,
                re.IGNORECASE
            )
            if diff_match:
                item_a = diff_match.group(1).strip().title()
                item_b = diff_match.group(2).strip().title()
                comp_key = f"{item_a} vs {item_b}"
                if comp_key not in seen_concepts:
                    seen_concepts.add(comp_key)
                    cards.append({
                        "concept": comp_key,
                        "front": f"What is the key technical difference between **{item_a}** and **{item_b}**?",
                        "back": sent
                    })

        # 3. Fallback: Meaningful Key Concept Takeaways
        if len(cards) < 4:
            for sent in sentences:
                if len(cards) >= 6:
                    break
                words = [w.title() for w in re.findall(r'\b[A-Za-z]{4,}\b', sent) if w.lower() not in FILTER_NOISE_TOKENS]
                if words:
                    key_topic = words[0]
                    if key_topic not in seen_concepts:
                        seen_concepts.add(key_topic)
                        cards.append({
                            "concept": f"Key Topic: {key_topic}",
                            "front": f"Explain the core principle regarding: **{key_topic}**",
                            "back": sent
                        })

        # Ensure fallback card if deck is empty
        if not cards and text.strip():
            clean_title = re.sub(r'^(?:Doc:\s*|\.pdf|\.docx|\.txt)', '', title, flags=re.I).strip() or "Key Concepts"
            cards.append({
                "concept": clean_title,
                "front": f"What are the primary technical concepts outlined in **{clean_title}**?",
                "back": sentences[0] if sentences else text[:300]
            })

        return cards[:8]

    def generate_quiz(self, text: str, title: str = "") -> List[Dict[str, Any]]:
        """
        Generates context-aware, conceptual multiple-choice quiz questions with
        intelligent distractors extracted directly from text entities and domain taxonomy.
        """
        sentences = self._clean_sentences(text)
        if not sentences and not text.strip():
            return []

        quiz_questions = []
        extracted_concepts = self._extract_key_concepts(text)
        qa_pairs = self._extract_qa_blocks(text)

        # 1. Generate questions from explicit Q&A pairs (e.g. interview sheets)
        for qa in qa_pairs[:3]:
            q_text = qa["question"]
            correct_ans_full = qa["answer"]
            ans_first_sent = sent_tokenize(correct_ans_full)[0] if correct_ans_full else "Core conceptual definition."
            
            # Meaningful plausible alternative distractors
            if "difference between" in q_text.lower():
                distractors = [
                    "Both share identical mutable memory references and can be freely updated.",
                    "One is strictly restricted to runtime compilation while the other is parsed at build time.",
                    "Neither structure allows indexing or iteration in modern runtime environments."
                ]
            elif "decorator" in q_text.lower():
                distractors = [
                    "It compiles the Python script directly to native C assembly bytecode.",
                    "It restricts a class to a single global singleton instance in memory.",
                    "It automatically serializes object hierarchies into JSON records."
                ]
            elif "gil" in q_text.lower() or "lock" in q_text.lower():
                distractors = [
                    "A compiler directive that forces all variables to be statically typed.",
                    "A garbage collection algorithm that periodically wipes unreferenced heap memory.",
                    "A networking protocol that securely encrypts socket payloads."
                ]
            else:
                other_answers = [p["answer"] for p in qa_pairs if p["question"] != q_text]
                if other_answers:
                    distractors = [sent_tokenize(a)[0][:110] for a in other_answers[:2]]
                    distractors.append("Acts as a deprecated fallback interface with no active runtime impact.")
                else:
                    distractors = [
                        "Provides low-level hardware memory pointer arithmetic.",
                        "Manages static class-level variables across isolated processes.",
                        "Enforces strict type safety checks prior to script execution."
                    ]

            options = [ans_first_sent[:120] + ("..." if len(ans_first_sent) > 120 else "")] + distractors[:3]
            random.shuffle(options)

            quiz_questions.append({
                "id": len(quiz_questions) + 1,
                "question": q_text,
                "options": options,
                "correct_answer": ans_first_sent[:120] + ("..." if len(ans_first_sent) > 120 else ""),
                "explanation": f"Key Explanation: \"{correct_ans_full}\""
            })

        # 2. Generate Concept Definition Multiple-Choice Questions
        for sent in sentences:
            if len(quiz_questions) >= 5:
                break

            def_match = re.search(
                r'^(?:[A-Z][a-z0-9_-]*\s+)?([A-Za-z0-9_-]{3,30})\s+(?:is\s+(?:a|an|the|defined\s+as)|are\s+(?:the)?|refers\s+to|is\s+used\s+(?:to|for))\s+(.+)',
                sent,
                re.IGNORECASE
            )
            if def_match:
                subject = def_match.group(1).strip().title()
                predicate = def_match.group(2).strip()

                if subject.lower() in FILTER_NOISE_TOKENS or len(subject) < 3:
                    continue

                # Curate distractors from relevant domain pools and extracted concepts
                subj_stem = subject.rstrip('s').lower()
                distractor_pool = []
                
                # Check extracted concepts
                for c in extracted_concepts:
                    if c.rstrip('s').lower() != subj_stem and c.lower() not in FILTER_NOISE_TOKENS:
                        if c.title() not in distractor_pool:
                            distractor_pool.append(c.title())

                # Merge with rich taxonomy
                all_domain_distractors = (
                    DOMAIN_DISTRACTOR_POOLS["python_core"] + 
                    DOMAIN_DISTRACTOR_POOLS["data_structures"] + 
                    DOMAIN_DISTRACTOR_POOLS["oop"] +
                    DOMAIN_DISTRACTOR_POOLS["general_cs"]
                )
                for d in all_domain_distractors:
                    if d.rstrip('s').lower() != subj_stem and d not in distractor_pool:
                        distractor_pool.append(d)

                selected_distractors = random.sample(distractor_pool, min(3, len(distractor_pool)))
                options = [subject] + selected_distractors
                random.shuffle(options)

                predicate_clean = predicate[:130] + ("..." if len(predicate) > 130 else "")
                quiz_questions.append({
                    "id": len(quiz_questions) + 1,
                    "question": f"Which concept is defined as: \"...{predicate_clean}\"?",
                    "options": options,
                    "correct_answer": subject,
                    "explanation": f"Correct Concept: **{subject}** — Context: \"{sent}\""
                })

        # 3. Generate Targeted Conceptual Fill-In Questions
        if len(quiz_questions) < 4:
            for sent in sentences:
                if len(quiz_questions) >= 5:
                    break
                
                for concept in extracted_concepts:
                    c_stem = concept.rstrip('s').lower()
                    if len(concept) > 3 and c_stem not in FILTER_NOISE_TOKENS and re.search(rf'\b{re.escape(concept)}\b', sent, re.IGNORECASE):
                        blanked = re.sub(rf'\b{re.escape(concept)}\b', '______', sent, count=1, flags=re.IGNORECASE)
                        
                        distractor_pool = []
                        for c in extracted_concepts:
                            if c.rstrip('s').lower() != c_stem and c.lower() not in FILTER_NOISE_TOKENS:
                                if c.title() not in distractor_pool:
                                    distractor_pool.append(c.title())

                        for d in DOMAIN_DISTRACTOR_POOLS["python_core"] + DOMAIN_DISTRACTOR_POOLS["data_structures"]:
                            if d.rstrip('s').lower() != c_stem and d not in distractor_pool:
                                distractor_pool.append(d)

                        selected_distractors = random.sample(distractor_pool, min(3, len(distractor_pool)))
                        options = [concept.title()] + selected_distractors[:3]
                        random.shuffle(options)

                        quiz_questions.append({
                            "id": len(quiz_questions) + 1,
                            "question": f"Complete the statement: \"{blanked}\"",
                            "options": options,
                            "correct_answer": concept.title(),
                            "explanation": f"Full Context: \"{sent}\""
                        })
                        break

        return quiz_questions[:5]
