from __future__ import annotations

from src.bow_analysis import tokenize


def extract_tfidf_terms(documents: list[str], top_k: int = 8) -> list[str]:
    cleaned = [doc for doc in documents if doc.strip()]
    if not cleaned:
        return []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=50)
        matrix = vectorizer.fit_transform(cleaned)
        scores = matrix[-1].toarray()[0]
        terms = vectorizer.get_feature_names_out()
        ranked = sorted(zip(terms, scores), key=lambda item: item[1], reverse=True)
        return [term for term, score in ranked[:top_k] if score > 0]
    except Exception:
        stopwords = {"the", "and", "for", "that", "with", "this", "from", "are", "you"}
        words = [word for word in tokenize(cleaned[-1]) if word not in stopwords]
        seen: list[str] = []
        for word in words:
            if word not in seen:
                seen.append(word)
        return seen[:top_k]
