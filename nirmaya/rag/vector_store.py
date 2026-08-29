import json
import math
import os
import re
from typing import List, Dict, Any

class MedicalVectorStore:
    """TF-IDF & Semantic Vector Store for Grounded Medical Knowledge Retrieval"""

    def __init__(self, data_path: str = None):
        if not data_path:
            data_path = os.path.join(os.path.dirname(__file__), "..", "data", "medical_knowledge.json")
        self.data_path = data_path
        self.documents = []
        self.doc_vectors = []
        self.vocabulary = {}
        self.idf = {}
        self.load_and_index()

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = [w for w in cleaned.split() if len(w) > 2]
        return tokens

    def load_and_index(self):
        if not os.path.exists(self.data_path):
            return
        with open(self.data_path, "r", encoding="utf-8-sig") as f:
            self.documents = json.load(f)

        # Build combined text per document
        doc_texts = []
        for doc in self.documents:
            kw = " ".join(doc.get("keywords", []))
            sym = " ".join(doc.get("symptoms", []))
            combined = f"{doc['condition']} {doc['category']} {kw} {doc['summary']} {sym}"
            doc_texts.append(combined)

        # Build vocabulary & Document Frequencies
        df_counts = {}
        N = len(doc_texts)
        for text in doc_texts:
            tokens = set(self._tokenize(text))
            for tok in tokens:
                df_counts[tok] = df_counts.get(tok, 0) + 1

        self.vocabulary = {tok: idx for idx, tok in enumerate(df_counts.keys())}
        self.idf = {tok: math.log((N + 1) / (count + 1)) + 1.0 for tok, count in df_counts.items()}

        # Build TF-IDF vectors for documents
        self.doc_vectors = []
        for text in doc_texts:
            vec = self._compute_tfidf(text)
            self.doc_vectors.append(vec)

    def _compute_tfidf(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        
        vec = {}
        norm_sq = 0.0
        for t, count in tf.items():
            if t in self.idf:
                val = (count / len(tokens)) * self.idf[t]
                vec[t] = val
                norm_sq += val * val

        # Normalize
        norm = math.sqrt(norm_sq)
        if norm > 0:
            for t in vec:
                vec[t] /= norm
        return vec

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_vec = self._compute_tfidf(query)
        if not query_vec:
            return []

        scores = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            dot_product = sum(query_vec[t] * doc_vec.get(t, 0.0) for t in query_vec)
            scores.append((dot_product, idx))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            if score > 0.05:  # Relevance threshold
                doc = self.documents[idx].copy()
                doc["relevance_score"] = round(float(score), 3)
                results.append(doc)

        return results
