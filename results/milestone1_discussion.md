# Milestone 1 Query Test Summary

## Results Discussion

All results from the test queries stored in `data/processed/test_queries.csv` are stored in the `results/test_queries` folder. The CSV files are named in the format `{utilized method}_{expected_method}_{difficulty}`. For example, if you want to view the matching items the BM25 method returned for the query `patio chair with reclining features` (`expected_method = semantic, difficulty = 3`), the CSV file containing these results is `results/test_queries/BM24_semantic_3.csv`. 

### BM25 Queries

These are the five queries categorized for the BM25 method to perform well in, arranged in perceived difficulty:

```
1. grass electric lawnmower
2. large metal rectangular garden bed
3. potting soil 10L
4. table insertable striped summer umbrella
5. tulip seeds red orange yellow green blue purple
```


### Semantics Queries

These are the five queries categorized for the semantic method to perform well in, arranged in perceived difficulty:

```
1. container to put plants in
2. something for automatically watering a lawn
3. patio chair with reclining features
4. small starter planting pots for young children
5. protection set for power drill
```


### LLM Queries

These are the five queries categorized for the LLM method to perform well in, arranged in perceived difficulty. For the purpose of this report, these queries were designed with the intent of the BM25 and semantics methods struggling to return meaningful results here.

```
1. highest rated patio decking options
2. least expensive rake for autumn leaves
3. good souvinier plants for a trip returning from Peru
4. best option to keep irrigation water cool while away for a long time
5. the most impressive grill for an annual sasuage grilling competition
```


### Other Queries

These last five queries are fun challenges that could reasonably occur, and none of the methods (including LLM) may be able to provide results for these queries fully. See the [README section](https://github.com/UBC-MDS/DSCI_575_project_alx649_joelyp/blob/main/README.md#descriptions-of-the-other-section) for more description about these queries.
<!-- This link will be functional once dev is merged to main for milestone 1. Also this comment won't show up in the render. -->

```
1. read plants for planting by small lake
2. 40 in 3D Simulation Bread Shape Pillow Soft Lumbar Baguette Back Cushion Funny Food Plush Stuffed Toy
3. ydcpyf m.y.p un.qcxn. iape.b dro.
4. richardella ecuformis
5. den mest kompakta och lättbärbara isbehållaren för att förvara kall champagne i över 12 timmar på en varm sommardag
```

## Summary of Methods

### BM25

BM25 performed well for short, specific keyword queries where product titles 
contained the exact search terms. Queries like "grass electric lawnmower" and 
"potting soil 10L" returned highly relevant results with strong scores.

However, BM25 struggled significantly when query terms were absent from the 
corpus. For example, "highest rated patio decking options" returned a pool 
cover, bird food, and a BBQ mat — none relevant — because the term "decking" 
does not appear in product titles. Similarly, "good souvenir plants for a trip 
returning from Peru" caused BM25 to latch onto the token "Peru", returning 
metal detectors and snow thrower parts that happened to mention Peru in their 
titles.

BM25 is also sensitive to multi-term queries where unintended tokens dominate 
scoring. The method is fast and deterministic but brittle outside its comfort 
zone of exact keyword matching.

### Semantics

Semantic search showed stronger intent understanding for natural language 
queries. For "grass electric lawnmower", semantic returned cleaner lawnmower 
results than BM25 by understanding the overall concept rather than matching 
individual tokens like "grass".

However, semantic search struggled with complex intent. "Good souvenir plants 
for a trip returning from Peru" returned generic flowers and plants — missing 
the "souvenir" concept entirely. On edge case queries like "richardella 
ecuformis" (an obscure scientific name typo), semantic returned completely 
unrelated products such as cables and pool parts, performing no better than BM25.

A key limitation in this milestone is that the semantic index was built on only 
20,000 of the 851,875 available products due to computational constraints. This 
likely reduced recall for semantic queries where the relevant product existed in 
the full corpus but not in the subset. A full index is planned for Milestone 2.

### Where More Advanced Methods Would Help

Complex intent queries (LLM category) were challenging for both methods. 
Queries like "best option to keep irrigation water cool while away for a long 
time" require reasoning about user context that neither keyword matching nor 
vector similarity can capture alone. RAG with LLM reranking is expected to 
improve results significantly for this query category in Milestone 2.

Query expansion could also help BM25 handle vocabulary mismatch, and a hybrid 
search combining BM25 and semantic scores would partially offset each method's 
individual weaknesses.