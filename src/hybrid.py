import os
from duckdb import DuckDBPyConnection
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from session_helper import init_session
import bm25
import semantic


class HybridRetriever:
    
    def __init__(self, k = 10, bm_strength = 0.5):
        self.k = k
        self.bm_strength = bm_strength
        self.semantic_strength = 1 - self.bm_strength
        self.merge_cols = ["parent_asin","title","price","store","average_rating","image_url"]

    def query(self, con: DuckDBPyConnection, text: str):
        # Obtain sufficient results such that overlap is very likely
        bm25_results = bm25.query_k_highest(con, text, 10000)
        semantic_results = semantic.query_k_highest(con, text, 10000)
        
        # Normalize scores to a scale of 0 to 1 when combined (higher is better)
        semantic_results["score"] = semantic_results["score"]-min(semantic_results["score"]) # best result is 0, must inverse the scale
        semantic_results["semantic_score"] = (1-(semantic_results["score"]/max(semantic_results["score"])))
        semantic_results = semantic_results[self.merge_cols+["semantic_score"]]

        if len(bm25_results) != 0: # Could return 0 results
            bm25_results["score"] = bm25_results["score"]-min(bm25_results["score"]) # worst result is 0
            bm25_results["bm25_score"] = (bm25_results["score"]/max(bm25_results["score"]))
        else:
            bm25_results["bm25_score"] = None # blank column
        bm25_results = bm25_results[self.merge_cols+["bm25_score"]]

        # Merge and compute combined scores to a normalized 0 to 1 scale
        hybrid_results = pd.merge(bm25_results, semantic_results, on = self.merge_cols, how = "outer")
        metric_cols = ["bm25_score","semantic_score"]
        hybrid_results[metric_cols] = hybrid_results[metric_cols].fillna(0)
        hybrid_results["score"] = hybrid_results["bm25_score"]*self.bm_strength + hybrid_results["semantic_score"]*self.semantic_strength

        # Return k highest values
        hybrid_results = hybrid_results.sort_values("score", ascending = False)[:self.k]
        return hybrid_results

if __name__ == "__main__": # base class test
    print("Startup session")
    con = init_session()
    test_query = "patio chair with reclining features" # semantic 3
    #test_query = "richardella ecuformis" # Other 4, should match semantic because bm25 just returns nothing
    hr = HybridRetriever(k = 100)
    result = hr.query(con,test_query)
    result.to_csv("src/dummytest.csv")
    con.close()
    print("Connection closed successfully.")