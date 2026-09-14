import unittest
from nlp_engine.rag_engine import VaultRAGEngine


class TestVaultRAGEngine(unittest.TestCase):

    def setUp(self):
        self.rag = VaultRAGEngine()
        self.sample_memories = [
            {
                "id": 1,
                "title": "Machine Learning Research Notes",
                "category": "Study",
                "tags": ["ml", "python", "transformers"],
                "description": "Transformers use self-attention mechanisms to process sequence data in parallel. BERT and GPT are two major architectures built upon the Transformer model. We evaluated multi-head attention with 8 heads on NLP datasets."
            },
            {
                "id": 2,
                "title": "Loan Management Project Architecture",
                "category": "Work",
                "tags": ["python", "oop", "database"],
                "description": "The Loan Management System uses Object-Oriented Programming (OOP) in Python with SQLite and PostgreSQL databases. It features user authentication, credit score checking, and automated monthly payment schedules."
            },
            {
                "id": 3,
                "title": "Gym & Diet Routine",
                "category": "Health",
                "tags": ["fitness", "workout"],
                "description": "Weekly split includes Chest and Triceps on Monday, Back and Biceps on Wednesday, Legs on Friday. Daily target is 150g protein and 3 liters of water."
            }
        ]

    def test_chunk_memory_short(self):
        chunks = self.rag.chunk_memory(self.sample_memories[0])
        self.assertGreaterEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["title"], "Machine Learning Research Notes")
        self.assertEqual(chunks[0]["category"], "Study")

    def test_chunk_memory_long(self):
        long_doc = {
            "id": 4,
            "title": "Long System Architecture Report",
            "category": "Work",
            "tags": ["system", "architecture"],
            "description": "Paragraph one contains details about microservices and API gateways. " * 20
        }
        chunks = self.rag.chunk_memory(long_doc, chunk_size=200, overlap=40)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0]["title"], "Long System Architecture Report")

    def test_retrieve_relevant_chunks(self):
        chunks = self.rag.build_chunk_corpus(self.sample_memories)
        results = self.rag.retrieve_relevant_chunks("What is self-attention in transformers?", chunks)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["title"], "Machine Learning Research Notes")
        self.assertIn("confidence_pct", results[0])

    def test_synthesize_answer_with_citations(self):
        chunks = self.rag.build_chunk_corpus(self.sample_memories)
        retrieved = self.rag.retrieve_relevant_chunks("How does the loan management system work?", chunks)
        res = self.rag.synthesize_answer("How does the loan management system work?", retrieved)
        
        self.assertIn("answer", res)
        self.assertIn("citations", res)
        self.assertGreater(len(res["citations"]), 0)
        self.assertEqual(res["citations"][0]["title"], "Loan Management Project Architecture")

    def test_chat_end_to_end(self):
        response = self.rag.chat("What are my workout days and protein intake?", self.sample_memories)
        self.assertIn("Direct Answer", response["answer"])
        self.assertIn("Sources & Citations", response["answer"])
        self.assertEqual(response["top_source"], "Gym & Diet Routine")

    def test_empty_vault_query(self):
        response = self.rag.chat("Something not in the vault xyz999", [])
        self.assertEqual(response["confidence"], 0)
        self.assertIn("could not find", response["answer"])


if __name__ == "__main__":
    unittest.main()
