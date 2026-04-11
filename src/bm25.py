import pandas as pd
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from session_helper import *

def tokenize(query):
    """
    TODO: look back at nltk package for implementation
    Generic helper function for tokenizing text.
    """
    return query

def score_query(text_column,query):
    """
    Returns a Series object with the BM25 scores for each given text (assumes this is already tokenized)

    text_column -> tokenized text column from either meta_clean.csv or reviews_clean.csv
    query -> text query 

    NOTE: Do NOT use this yet, keep pandas as far out of this as possible
    """

    # Set up the documents for BM25Retriever (This part may be preprocessable)
    documents = [Document(page_content = text) for text in text_column]
    retriever = BM25Retriever.from_documents(documents)

    # Run query and return results
    scores_series = pd.Series(retriever.vectorizer.get_scores(tokenize(query)))

    return scores_series

def query_k_highest(text_column,query,k = 10):
    """
    Returns the documents with the k highest scores for the query.
    
    text_column -> tokenized text column from either meta_clean.csv or reviews_clean.csv
    query -> text query 
    k -> number of documents to return (if greater than the number of documents or -1, defaults to returning all)
    """
    pass







if __name__ == "__main__":
    print("Startup session")
    con = init_session()
    
    
    # 3. Query the 'meta_search' table (not 'reviews')
    basic_query = "lawnmower"
    
    print("Running query...")
    results = con.execute(f"""
        SELECT 
            title, 
            price, 
            store, 
            fts_main_meta_search.match_bm25(parent_asin, '{basic_query}') AS score
        FROM meta_search
        WHERE score IS NOT NULL
        ORDER BY score DESC
        LIMIT 10
    """).df()    
    
    print(results)
    results.to_csv("src/dummytest.csv")
    con.close()
    print("Connection closed successfully.")