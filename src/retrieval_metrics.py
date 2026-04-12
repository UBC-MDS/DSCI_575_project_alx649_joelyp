import bm25
import semantic
from session_helper import *
import os


# Main file used for building all results from the queries

if __name__ == "__main__":
    con = init_session()
    test_queries = retrieve_test_queries()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load model and index once outside the loop
    model, index, metadata = semantic.load_model_and_index()
    
    for row in test_queries.itertuples():
        bm25_result = bm25.query_k_highest(con, row.query, 10)
        filepath = f"BM25_{row.expected_method}_{row.difficulty}.csv"
        path = os.path.join(base_dir, f"../results/test_queries/{filepath}")
        bm25_result.to_csv(path)

        semantic_result = semantic.query_k_highest(model, index, metadata, row.query, 10)
        filepath = f"semantic_{row.expected_method}_{row.difficulty}.csv"
        path = os.path.join(base_dir, f"../results/test_queries/{filepath}")
        semantic_result.to_csv(path)  # also missing path argument!

        


