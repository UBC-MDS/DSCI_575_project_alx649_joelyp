# Milestone 1 Query Test Summary

## Results Discussion

All results from the test queries stored in `data/processed/test_queries.csv` are stored in the `results/test_queries` folder. The CSV files are named in the format `{utilized method}_{expected_method}_{difficulty}`. For example, if you want to view the matching items the BM25 method returned for the query `patio chair with reclining features` (`expected_method = semantic, difficulty = 3`), the CSV file containing these results is `results/test_queries/BM24_semantic_3.csv`. 

### BM25 Queries

These are the five queries categorized for the BM25 method to perform well in, arranged in perceived difficulty:


#### 1. grass electric lawnmower

Both BM25 and semantic methods returned various entries related to lawnmowers; most of them being lawnmowers. 9 of the 10 entries in the semantic method were explicitly lawnmowers, most of which being electric. Interestingly, the closest match by BM25 found was `Brteyes Upgrade Electric Cordless Grass Trimmer, Lightweight Handheld Garden Grass Trimmer Rechargeable Lawn Trimmer & Edger,Telescopic Handle&4pc Plastic Blades&1pc Metal Blade`, which does not explicitly mention a "lawnmower" of any sort even if it very much could be used like one, indicating the BM25 method may not be able to determine which tokens of the query are more important to match. Also notable is that there was no overlap in the top 10 results for these methods.

#### 2. large metal rectangular garden bed

The idea of this query was to return some sort of planter, with the adjectives meant to help BM25. The first result being `SINCETHEN Galvanized Raised Garden Bed for Vegetables Herbs Plants, Oval Large Metal Planter Box for Outdoor Use, Raised Garden Bed Galvanized Steel 4X2X1 FT, Silver` indicates these descriptors were accounted for very well. The semantic method's top result `Outdoor 8x4Ft Metal Raised Garden Bed Patio Large Frame Planters Box for Vegetables/Flower/` is also a very close match to expectation.

#### 3. potting soil 10L

10L was specifically included to see if the BM25 method would be able to return bags of soil of exactly this capacity. What proceded to happen was that the top result was `Lawn Mower Tractor Deck Belt 5/8" x 143 1/2" Replacement for Husqvarna 574845603 GT 52XLS, GT 48XLSI, GTH 2752TF, GTH 24V52LS, GTH 26V52LS, GTH 3052TDF, GTH 3052TF GTH 52XLS TS 352 Series`, which is not close to what is expected. This query was reran manually in `bm25.py` and it produced the same top 10 results, so it's very strange this query just fails like this. The semantic method on the other hand was able to return a variety of soil products, even if none of them were exactly 10L bags.

#### 4. table insertable striped summer umbrella

For this query the intent was a patio type of umbrella visually similar to this:

![Depiction of the patio umbrella.](img/umbrella.jpg)

The BM25 method was mostly successful in that its results were either an umbrella similar to this depiction, or related accesories involving a table that such an umbrella would be inserted into as noted by the top result `Eforcurtain Stripes Round Zippered Outdoor Tablecloth with Umbrella Hole, 60 Inch Round Water Proof Fabric Patio Table Cover for Picnic Black and White`. Semantic method has a simlar set of results with `Outus 2 Pieces Patio Table Umbrella Hole Ring Umbrella Cone Wedge Plug Umbrella Stabilizer Sleeve for 2 to 2.5 Inch Patio Table Hole and 1.5 Inch Pool Umbrella Adapter` being the top result.

#### 5. tulip seeds red orange yellow green blue purple

The general idea of this query was to return tulip seeds in a wide assortment of colours; the rainbow colours in this sense were supposed to throw both models off somewhat. This is a case where BM25 clearly outperforms semantics. BM25's top result is `Blumex Parrot Tulip 10 Bulbs - Exotic & New - 12/+ cm Bulbs`, which is a multicoloured tulip varient that is surprisingly understandable to the query's intent, while semantic's top result is `100 Orange EVENING COLORS SUNFLOWER Helianthus Annuus Flower Seeds`, which made an error in taking the seeds implication more literally.

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

