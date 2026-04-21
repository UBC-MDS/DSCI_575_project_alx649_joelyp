import faiss
import numpy as np
import os
import pickle
from itertools import islice
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from session_helper import *
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_NAME = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = os.path.join(base_dir, "../data/processed/faiss_index_merged.bin")
FAISS_META_PATH  = os.path.join(base_dir, "../data/processed/faiss_index_merged.pkl")
BATCH_SIZE = 1000
N_DOCS = 20_000

def build_faiss_index(con):
    model = SentenceTransformer(MODEL_NAME)

    print("Loading documents from DuckDB...")
    df = con.execute(f"""
    SELECT parent_asin, title, average_rating, price, store, image_url, page_content
    FROM meta_search
    LIMIT {N_DOCS}
    """).fetchdf()

    texts = df['page_content'].fillna('').tolist()

    print(f"Encoding {len(df):,} documents in batches of {BATCH_SIZE}...")

    # Build page_content the same way as the generator
    texts = df['page_content'].fillna('').tolist()

    metadata = df[['parent_asin', 'title', 'average_rating', 'price', 'store', 'image_url']].to_dict(orient='records')

    all_embeddings = []
    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Encoding"):
        batch = texts[i:i+BATCH_SIZE]
        embeddings = model.encode(batch, show_progress_bar=False)
        all_embeddings.append(embeddings)

    all_embeddings = np.vstack(all_embeddings).astype('float32')
    dimension = all_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(all_embeddings)

    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(FAISS_META_PATH, 'wb') as f:
        pickle.dump(metadata, f)

    print(f"Saved index ({index.ntotal:,} vectors) and metadata.")


def query_k_highest(con, query, index, metadata, k = 10):
    model = SentenceTransformer(MODEL_NAME)
    
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

    if not os.path.exists(FAISS_INDEX_PATH):
        build_faiss_index(con)

    result = query_k_highest(con, "garden hose 50ft", k=10)
    print(result)
    con.close()