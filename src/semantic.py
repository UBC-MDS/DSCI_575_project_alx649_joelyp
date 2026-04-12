from session_helper import *
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

# Path to save/load the FAISS index
base_dir = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(base_dir, "../data/processed/faiss_index")

# Model recommended by the course — small, fast, good quality
MODEL_NAME = "all-MiniLM-L6-v2"


def build_faiss_index(con):
    """
    Builds a FAISS index from the meta documents and saves it to disk.
    Only needs to be run once — subsequent searches load from disk.

    Parameters
    ----------
    con : DuckDBPyConnection
        Active DuckDB session
    """

    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    print("Streaming documents from DuckDB...")
    # Reuse the existing generator from session_helper
    # docs = list(create_langchain_meta_generator(con))
    docs = list(create_langchain_meta_generator(con))[:50_000]  # create initial subset

    print(f"Building FAISS index from {len(docs):,} documents...")
    vector_store = FAISS.from_documents(docs, embeddings)

    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"Index saved to {FAISS_INDEX_PATH}")

def query_k_highest(con, query, k=10):
    """
    Search the FAISS index using semantic similarity.

    Encodes the query using the same model used to build the index,
    then finds the k most similar documents by vector distance.

    Parameters
    ----------
    con   : DuckDBPyConnection — not used directly but kept to match bm25 interface
    query : the search string entered by the user
    k     : number of top results to return (default 10)

    Returns
    -------
    DataFrame with columns: parent_asin, title, average_rating, price, store, image_url, score
    """

    # Load the embedding model
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    # Load the saved FAISS index from disk
    vector_store = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True  # required by LangChain for local files
    )

    # Search — returns list of (Document, score) tuples
    results = vector_store.similarity_search_with_score(query, k=k)

    # Flatten into a list of dicts matching the bm25 output format
    rows = []
    for doc, score in results:
        row = doc.metadata.copy()
        row['score'] = score
        rows.append(row)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    con = init_session()

    # Build the index if it doesn't exist yet
    if not os.path.exists(FAISS_INDEX_PATH):
        build_faiss_index(con)

    result = query_k_highest(con, "garden hose 50ft", k=10)
    print(result)

    con.close()