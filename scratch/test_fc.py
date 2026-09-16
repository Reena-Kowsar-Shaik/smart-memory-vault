import sys, os
sys.path.insert(0, os.path.abspath("."))
from core.database import get_db, Memory
from nlp_engine import quiz_engine

print("=== 1. TESTING TOPIC FLASHCARDS (MIN 5 GUARANTEE) ===")
topics = [
    'Python', 'Flask', 'OOP', 'File Handling', 'Interview',
    'Resume', 'Project', 'Meeting', 'Certificate',
    'Data Structures', 'Database', 'Security', 'Web',
    'AI', 'Health', 'Finance', 'Study', 'Personal'
]
for topic in topics:
    cards = quiz_engine.generate_flashcards_by_topic(topic, count=8)
    assert len(cards) >= 5, f"Topic {topic} failed min cards: {len(cards)}"
    print(f"  [OK] Topic: {topic:<18} | Count: {len(cards)} | First: {cards[0]['concept']}")

import sys, os
sys.path.insert(0, os.path.abspath("."))
from core.database import get_db, Memory
from nlp_engine import quiz_engine

with get_db() as s:
    mems = s.query(Memory).all()
    seen = set()
    for m in mems:
        if m.title in seen:
            continue
        seen.add(m.title)
        sep = '.' if not m.title.endswith('.') else ''
        content_text = f"{m.title}{sep}\n{m.description}\n{m.summary}"
        qq = quiz_engine.generate_quiz(content_text, title=m.title)
        print(f"Memory: {m.title[:35]:<35} | Quiz Qs: {len(qq)}")
        for q in qq:
            print(f"   Q{q['id']}: {q['question'][:60]}...")



