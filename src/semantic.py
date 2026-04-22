import faiss
import numpy as np
import os
import pickle
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from session_helper import load_model_and_index, init_session
import pandas as pd

def build_faiss_index(con, model_name, faiss_index_path, faiss_meta_path, batch_size = 1000, n_docs = 20000):
    """
    Constructs a FAISS index for semantic search from a sample of documents.
    """
    model = SentenceTransformer(model_name)

    print("Loading documents from DuckDB...")
    df = con.execute(f"""
    SELECT parent_asin, title, average_rating, price, store, image_url, page_content
    FROM meta_search
    LIMIT {n_docs}
    """).fetchdf()

    texts = df['page_content'].fillna('').tolist()

    print(f"Encoding {len(df):,} documents in batches of {batch_size}...")

    # Build page_content the same way as the generator
    texts = df['page_content'].fillna('').tolist()

    metadata = df[['parent_asin', 'title', 'average_rating', 'price', 'store', 'image_url']].to_dict(orient='records')

    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Encoding"):
        batch = texts[i:i+batch_size]
        embeddings = model.encode(batch, show_progress_bar=False)
        all_embeddings.append(embeddings)

    all_embeddings = np.vstack(all_embeddings).astype('float32')
    dimension = all_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(all_embeddings)

    faiss.write_index(index, faiss_index_path)
    with open(faiss_meta_path, 'wb') as f:
        pickle.dump(metadata, f)

    print(f"Saved index ({index.ntotal:,} vectors) and metadata.")


def query_k_highest(query, model, index, metadata, k = 10):
    
    # Encode query and search
    query_vec = model.encode([query]).astype('float32')
    distances, indices = index.search(query_vec, k)

    rows = []
    for dist, idx in zip(distances[0], indices[0]):
        row = metadata[idx].copy()
        row['score'] = float(dist)
        rows.append(row)

    return pd.DataFrame(rows)


if __name__ == "__main__":

    con = init_session()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_name = "all-MiniLM-L6-v2"
    faiss_index_path = os.path.join(base_dir, "../data/processed/faiss_index_merged.bin")
    faiss_meta_path  = os.path.join(base_dir, "../data/processed/faiss_index_merged.pkl")
    if not os.path.exists(faiss_index_path):
        build_faiss_index(con, model_name, faiss_index_path, faiss_meta_path)

    model,index, metadata = load_model_and_index(faiss_index_path, faiss_meta_path)

    result = query_k_highest("garden hose 50ft", model, index, metadata, k=10)
    print(result)
    con.close()