from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util


def rank_attractions(attractions, user_query, top_k=10):
    # Create documents: combine name + desc + subcategories
    docs = []
    for item in attractions:
        text_parts = [item.get("name", ""), item.get("description", "")]
        if item.get("subcategory"):
            text_parts += [sub.get("name", "") for sub in item["subcategory"] if sub]
        doc = " ".join(filter(None, text_parts)).strip()
        if doc:
            docs.append((item, doc))

    if not docs:
        print("⚠️ No valid documents to rank. Returning raw attractions.")
        return attractions[:top_k]

    items, doc_texts = zip(*docs)

    # BM25 ranking
    tokenized_corpus = [doc.lower().split() for doc in doc_texts]
    if len(tokenized_corpus) == 0:
        print("⚠️ Empty tokenized corpus. Returning raw attractions.")
        return attractions[:top_k]

    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(user_query.lower().split())

    # Semantic similarity
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_emb = model.encode(user_query, convert_to_tensor=True)
    doc_embs = model.encode(doc_texts, convert_to_tensor=True)
    sim_scores = util.pytorch_cos_sim(query_emb, doc_embs)[0]

    # Combine BM25 and semantic score
    combined = [
        (items[i], 0.5 * bm25_scores[i] + 0.5 * sim_scores[i].item())
        for i in range(len(items))
    ]
    combined.sort(key=lambda x: x[1], reverse=True)

    return [item for item, score in combined[:top_k]]
