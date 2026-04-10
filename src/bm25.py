import pandas as pd

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

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
    """

    # Set up the documents for BM25Retriever (This part may be preprocessable)
    documents = [Document(page_content = text) for text in text_column]
    retriever = BM25Retriever.from_documents(documents)

    # Run query and return results
    scores_series = pd.Series(retriever.vectorizer.get_scores(tokenize(query)))

    return scores_series










if __name__ == "__main__":
    pass