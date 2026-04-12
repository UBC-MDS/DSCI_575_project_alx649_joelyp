from session_helper import *

import pandas as pd
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from nltk.tokenize import word_tokenize
import string

# nltk.download('punkt') already done from preprocessing
PUNCT_SET = set(string.punctuation)


def preprocess_for_search(text):
    if not text:
        return ""
    
    tokens = word_tokenize(text.lower())
    
    clean_tokens = [
        t for t in tokens 
        if t not in PUNCT_SET and t.isalnum()
    ]
    
    return " ".join(clean_tokens)


def query_k_highest(con: DuckDBPyConnection, query: str,k: int = 10):
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
    print("Startup session")
    con = init_session()
    
    result = query_k_highest(con,"table insertable striped summer umbrella",100)

    result.to_csv("src/dummytest.csv")
    con.close()
    print("Connection closed successfully.")