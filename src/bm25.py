from session_helper import init_session
from duckdb import DuckDBPyConnection

from nltk.tokenize import word_tokenize
import string
import nltk


def preprocess_for_search(text):
    """Returns a tokenized version of a text query string."""
    if not text:
        return ""
    
    tokens = word_tokenize(text.lower())
    
    clean_tokens = [
        t for t in tokens 
        if t not in set(string.punctuation) and t.isalnum()
    ]
    
    return " ".join(clean_tokens)


def query_k_highest(con: DuckDBPyConnection, query: str, k: int = 10):
    """
    Returns the documents with the k highest scores for the query.
    
    Parameters
    ----------
    con : DuckDBPyConnection
        DuckDB session
    query : str 
        text query 
    k : int, optional (default = 10) 
        number of documents to return
    
    Returns
    -------
    DataFrame
        Contains the k results with the highest score in BM25 for the query.
    """

    tokenized_query = preprocess_for_search(query)
    
    # if search table is already built in preprocessing

    results = con.execute("""
    SELECT 
        parent_asin,
        title, 
        price, 
        store,
        average_rating,
        image_url,
        fts_main_meta_search.match_bm25(parent_asin, ?) AS score
    FROM meta_search
    WHERE score IS NOT NULL
    ORDER BY score DESC
    LIMIT ?
""", [tokenized_query, k]).df()

    return results



if __name__ == "__main__":
    # Ensure the tokenizer exists
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    print("Startup session")
    con = init_session()
    
    result = query_k_highest(con,"potting soil 10L",10000)

    result.to_csv("src/dummytest.csv")
    con.close()
    print("Connection closed successfully.")