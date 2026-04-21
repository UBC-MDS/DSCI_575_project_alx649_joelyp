from duckdb import DuckDBPyConnection
import duckdb
from langchain_core.documents import Document
from langchain_groq import ChatGroq
import os
import pandas as pd
import faiss
import pickle
from sentence_transformers import SentenceTransformer

"""
Helper code set up in notebooks/milestone1_exploration.ipynb
"""

def init_session(dbpath = "../data/processed/amazon_reviews.duckdb"):
    """Initializes a duckdb session with a given path to a duckdb file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    duckdb_path = os.path.join(base_dir, dbpath)
    con = duckdb.connect(duckdb_path, read_only=True)
    return con

def retrieve_test_queries():
    """Return the Pandas dataframe with the test queries."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pd_path = os.path.join(base_dir, "../data/processed/test_queries.csv")
    df = pd.read_csv(pd_path)
    return df
    

def create_langchain_meta_generator(con: DuckDBPyConnection):
    """
    Returns a Langchain generator object for the meta dataset.

    Input
    -----
    con: DuckDBPyConnection
    An initial DuckDB connection to the database.

    Output
    ------
    A generator of Langchain objects that can be iterated through for model queries.
    """

    relation = con.sql("""
    SELECT
        parent_asin,
        CAST(title AS VARCHAR)       AS title,
        CAST(features AS VARCHAR)    AS features,
        CAST(description AS VARCHAR) AS description,
        average_rating,
        price,
        store,
        CAST(image_url AS VARCHAR)   AS image_url
    FROM meta
    """)

    # Fetch in batches of 100,000 to balance speed and RAM
    record_batch_reader = relation.fetch_record_batch(rows_per_batch=100_000)
    
    for batch in record_batch_reader:
        # Convert the Arrow batch to a list of dictionaries for easy access
        for row in batch.to_pylist():
            yield Document(
                page_content=f"{row['title']} {row['features']} {row['description']}",
                metadata={
                    'parent_asin': row['parent_asin'],
                    'title': row['title'],
                    'average_rating': row['average_rating'],
                    'price': row['price'],
                    'store': row['store'],
                    'image_url': row['image_url'],
                }
            )


def create_langchain_review_generator(con):
    """
    Returns a Langchain generator object for the review dataset.

    Input
    -----
    con: DuckDBPyConnection
    An initial DuckDB connection to the database.

    Output
    ------
    A generator of Langchain objects that can be iterated through for model queries.
    """
    
    
    relation = con.sql("""
    SELECT 
        (COALESCE(CAST(title AS VARCHAR), '') || ' ' || COALESCE(CAST(text AS VARCHAR), '')) AS combined_content,
        parent_asin, 
        CAST(title AS VARCHAR) AS title, 
        rating, 
        helpful_vote, 
        CAST(image_url AS VARCHAR) AS image_url
    FROM reviews
    """)

    # Fetch in batches of 100,000 to balance speed and RAM
    record_batch_reader = relation.fetch_record_batch(rows_per_batch=100_000)
    
    for batch in record_batch_reader:
        # Convert the Arrow batch to a list of dictionaries for easy access
        for row in batch.to_pylist():
            yield Document(
                page_content=row['combined_content'],
                metadata={
                    'parent_asin': row['parent_asin'],
                    'title': row['title'],
                    'rating': row['rating'],
                    'helpful_vote': row['helpful_vote'],
                    'image_url': row['image_url']
                }
            )

def load_model_and_index(faiss_bin = "../data/processed/faiss_index_merged.bin", faiss_pkl = "../data/processed/faiss_index_merged.pkl"):
    """Loads the semantic FAISS index from faiss_bin and faiss_pkl."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model    = SentenceTransformer("all-MiniLM-L6-v2")
    index    = faiss.read_index(os.path.join(base_dir, faiss_bin))
    with open(os.path.join(base_dir, faiss_pkl), 'rb') as f:
        metadata = pickle.load(f)
    return model, index, metadata

def construct_groq_instance(key = ""):
    """
    Attempts to setup a LLM instance with Groq for RAG use.

    Input
    -----
    key: str (default = "")
    The Groq API Key, if this value is "", it's assumed none is given and defaults to the .env key if it exists.

    Output
    ------
    A LLM instance to be used for RAG.
    """
    try:
        if key == "":
            return ChatGroq(
                model="qwen/qwen3-32b",
                api_key=os.getenv("GROQ_API_KEY")
            )
        else:
            return ChatGroq(
                model="qwen/qwen3-32b",
                api_key=key
            )
    except Exception as e:
        raise EnvironmentError(f"No working GROQ_API_KEY was detected. Full details of the error are below:\n {e}")
