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


### Semantics

