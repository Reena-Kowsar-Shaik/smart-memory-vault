"""
nlp_engine/categorizer.py
Auto-categorization & Tag Extraction
Categories: Personal, Work, Health, Study, Finance, Ideas
"""

import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

CATEGORY_TAXONOMY = {
    "Health": [
        "doctor", "hospital", "medicine", "prescription", "clinic", "symptom", "pain",
        "appointment", "dentist", "therapy", "surgery", "diet", "workout", "fitness",
        "blood", "fever", "pharmacy", "vaccine", "exercise", "mental", "wellness"
    ],
    "Finance": [
        "money", "bank", "salary", "expense", "tax", "invoice", "investment",
        "budget", "crypto", "bitcoin", "payment", "loan", "interest", "insurance",
        "stock", "portfolio", "credit", "debit", "receipt", "audit", "wealth"
    ],
    "Work": [
        "meeting", "project", "deadline", "client", "boss", "colleague", "presentation",
        "report", "sprint", "email", "office", "manager", "team", "contract",
        "task", "deliverable", "kpi", "roadmap", "agile", "standup"
    ],
    "Study": [
        "exam", "assignment", "university", "college", "course", "lecture", "book",
        "research", "study", "homework", "syllabus", "professor", "semester", "grade",
        "thesis", "quiz", "class", "library", "notes", "academic", "interview prep"
    ],
    "Ideas": [
        "startup", "invention", "brainstorm", "concept", "feature", "strategy", "vision",
        "prototype", "creative", "innovation", "product", "pitch", "solution", "design",
        "hackathon", "experiment", "inspiration"
    ],
    "Personal": [
        "family", "vacation", "birthday", "friend", "home", "hobby", "diary",
        "journal", "reflection", "trip", "holiday", "anniversary", "dinner", "weekend",
        "travel", "memory", "celebration", "personal"
    ]
}


# High-value Domain & Technical Keywords Directory
KNOWN_DOMAINS = {
    # Programming Languages & Core
    "python", "javascript", "typescript", "java", "c++", "golang", "rust", "sql", "html", "css", "bash",
    
    # Python Specific Concepts
    "decorators", "generators", "iterators", "lambda", "list comprehension", "gil",
    "global interpreter lock", "multithreading", "multiprocessing", "asyncio", "memory management",
    "garbage collection", "metaclasses", "dunder methods", "type hinting", "virtual environment",
    
    # Data Structures & Types
    "data structures", "algorithms", "arrays", "linked list", "stack", "queue", "trees", "graphs",
    "hashmap", "dictionary", "tuples", "lists", "sets", "strings", "integers", "booleans",
    "recursion", "dynamic programming", "binary search", "sorting", "time complexity", "space complexity",
    
    # OOP & Design Patterns
    "oop", "inheritance", "polymorphism", "encapsulation", "abstraction", "classes", "objects",
    "methods", "design patterns", "singleton", "factory pattern", "clean code", "solid principles",
    
    # Frameworks, Tools & Web
    "flask", "django", "fastapi", "react", "nextjs", "vue", "angular", "node", "express",
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "docker", "kubernetes", "git", "github",
    "rest api", "graphql", "microservices", "system design", "orm", "sqlalchemy", "jwt", "authentication",
    "authorization", "middleware", "caching", "websockets", "unit testing", "pytest",
    
    # Data Science & AI
    "streamlit", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "nlp", "machine learning",
    "deep learning", "computer vision", "transformers", "llm", "bert", "gpt", "rag", "embeddings",
    
    # Interview, Career & Academic
    "interview prep", "system design", "database indexing", "transaction management",
    "project management", "agile", "scrum", "kanban", "sprint", "portfolio", "resume",
    "certification", "thesis", "research", "statistics", "analytics"
}

# Words to strictly filter out from becoming tags (generic noise, filler words, metadata)
NOISE_WORDS = {
    # Document Metadata & Author Placeholders
    "difference", "differences", "different", "document", "documents", "pdf", "docx", "file", "files",
    "page", "pages", "author", "authors", "summary", "notes", "note", "report", "reports",
    "question", "questions", "answer", "answers", "example", "examples", "sample", "samples",
    "sowmya", "tummala", "kumar", "sharma", "singh", "patel", "reddy", "john", "doe",
    "introduction", "conclusion", "section", "chapter", "guide", "concept", "point", "points",
    
    # Filler Words & Verbs
    "using", "used", "which", "what", "where", "when", "there", "their", "about", "above",
    "below", "following", "given", "based", "first", "second", "third", "also", "into",
    "from", "with", "have", "more", "most", "some", "such", "only", "other", "same",
    "even", "like", "make", "made", "good", "well", "very", "much", "many", "type", "types",
    "user", "users", "name", "names", "email", "phone", "date", "time", "year", "month",
    "true", "false", "null", "none", "item", "items", "text", "content", "data", "info",
    "allows", "allowed", "allowing", "modify", "modified", "modifying", "creation", "created",
    "creates", "meaning", "means", "meant", "without", "directly", "altering", "source", "code",
    "generally", "faster", "consume", "consumes", "consumed", "execution", "execute", "executes",
    "explain", "explained", "explaining", "describes", "described", "provides", "provided",
    "refers", "refer", "holding", "point", "native", "thread", "threads", "mutex", "bytecode"
}


class MemoryCategorizer:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english')).union(NOISE_WORDS)
        except Exception:
            self.stop_words = set(NOISE_WORDS)

    def predict_category(self, text: str) -> str:
        """Classifies text into the best matching category."""
        if not text or not text.strip():
            return "General"

        text_lower = text.lower()
        scores = {category: 0 for category in CATEGORY_TAXONOMY}

        for category, keywords in CATEGORY_TAXONOMY.items():
            for kw in keywords:
                matches = re.findall(rf"\b{re.escape(kw)}\b", text_lower)
                scores[category] += len(matches)

        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else "Study"

    def extract_tags(self, text: str, top_n: int = 6) -> list[str]:
        """
        Extracts high-value technical and conceptual keywords and keyphrases.
        Prioritizes verified technical skills, CS concepts, and multi-word terms.
        """
        if not text or not text.strip():
            return []

        text_lower = text.lower()
        extracted_tags = []

        # 1. First Pass: Check known technical & domain keyphrases
        for domain_term in KNOWN_DOMAINS:
            pattern = rf"\b{re.escape(domain_term)}\b"
            if re.search(pattern, text_lower):
                # Boost multi-word or core domain phrases
                weight = 2.0 if " " in domain_term else 1.2
                count = len(re.findall(pattern, text_lower))
                extracted_tags.append((domain_term, count * weight))

        # 2. Second Pass: Extract candidate technical words
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        filtered_words = [w for w in words if w not in self.stop_words and w not in NOISE_WORDS]

        word_counts = Counter(filtered_words)
        for word, count in word_counts.most_common(12):
            if word not in [t[0] for t in extracted_tags]:
                extracted_tags.append((word, count * 0.8))

        # Sort by score and filter duplicates
        extracted_tags.sort(key=lambda x: x[1], reverse=True)
        
        final_tags = []
        seen = set()
        for tag, _ in extracted_tags:
            tag_clean = tag.strip().lower()
            if tag_clean not in seen and tag_clean not in NOISE_WORDS and len(tag_clean) > 2:
                seen.add(tag_clean)
                final_tags.append(tag_clean)
            if len(final_tags) >= top_n:
                break

        return final_tags or ["technical-notes", "knowledge"]
