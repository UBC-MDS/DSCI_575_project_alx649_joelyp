# Milestone 1 Query Test Summary

## Results Discussion

All results from the test queries stored in `data/processed/test_queries.csv` are stored in the `results/test_queries` folder. The CSV files are named in the format `{utilized method}_{expected_method}_{difficulty}`. For example, if you want to view the matching items the BM25 method returned for the query `patio chair with reclining features` (`expected_method = semantic, difficulty = 3`), the CSV file containing these results is `results/test_queries/BM24_semantic_3.csv`. 

## Comparison Table

| Query | BM25 Results (brief) | Semantic Results (brief) | Better Method | Notes |
|-------|---------------------|--------------------------|---------------|-------|
| grass electric lawnmower | Lawnmowers + grass trimmers | Clean lawnmower results | Semantic | BM25 matches "grass" too broadly |
| large metal rectangular garden bed | Galvanized raised garden beds | Metal raised garden beds | Tie | Both methods perform well |
| potting soil 10L | Tractor belt as top result | Variety of soil products | Semantic | BM25 completely fails on this query |
| table insertable striped summer umbrella | Patio umbrellas + tablecloths | Patio umbrella accessories | Tie | Both return relevant results |
| tulip seeds red orange yellow green blue purple | Multicoloured tulip bulbs | Sunflower seeds | BM25 | Semantic confuses bulbs with seeds |
| container to put plants in | Mixed — mostly relevant | Flower pots and planters | Semantic | BM25 returns unrelated signs |
| something for automatically watering a lawn | Carburetor as top result | Irrigation/sprinkler systems | Semantic | BM25 fails on natural language |
| patio chair with reclining features | Zero gravity chairs | Reclining patio chairs | Tie | Both perform well |
| small starter planting pots for young children | Starter pots — duplicates | Seedling pots | Tie | Both misinterpret "young children" |
| protection set for power drill | Power drills | Chainsaw gear | Neither | Both miss the intent |
| highest rated patio decking options | BBQ mat, pool cover | Patio storage boxes | Neither | Neither understands "decking" |
| least expensive rake for autumn leaves | Various rakes, unsorted | Inexpensive rakes | Semantic | Neither sorts by price |
| good souvenir plants for a trip returning from Peru | Metal detectors, Monstera Peru | Gift cactus, Peruvian lily | Semantic | BM25 latches onto "Peru" token |
| best option to keep irrigation water cool while away | Mist systems, timers | Irrigation kits, sprinklers | Tie | Both surprisingly reasonable |
| most impressive grill for sausage competition | Grills + accessories | Grills + accessories | Tie | Neither understands "impressive" |
| read plants for planting by small lake | Welcome mats | Aquatic planting items | Semantic | Semantic handles typo better |
| 40 in 3D Simulation Bread Shape Pillow... | Outdoor pillows — consistent | Pillows + seating | BM25 | BM25 surprisingly consistent |
| ydcpyf m.y.p un.qcxn. iape.b dro. | No results | Random items | Neither | DVORAK keyboard input — both fail |
| richardella ecuformis | No results | Random items | Neither | Obscure scientific name — both fail |
| Swedish ice tub query | Random + urn planter | Random + alcohol items | Neither | Non-English query — both fail |


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

#### 1. container to put plants in

Semantic model as expected provided various options for plant containment in flower pots, garden beds, and a few other options that were all reasonable. BM25 to some extent due to the simplicity of this query also provided reasonable responses (pot hanger, air planter, terrarium) but also had a few that would not suffice such as the 7th highest option (`SmartSign 7 x 10 inch “Notice - No Open Toed Shoes Beyond This Point” OSHA Sign, 55 mil HDPE Plastic, Blue, Black and White`).

#### 2. something for automatically watering a lawn

The semantic model has very similar results to the LLM-4 query `best option to keep irrigation water cool while away for a long time`, but BM25 has more problems with this due to some of the extra wording possibly since while water related items do exist, the top choice for BM25 was `Carburetor for Troy-Bilt Storm 2660 31AM6BO3711 26" Craftsman 247.881733 SB410 SB450 31AS6BEE793 247.886400 247.881732 247.881980 247.884331 31AS6BEE799 Snow Thrower`.

#### 3. patio chair with reclining features

Nearly every result from semantics is a reclining patio chair verbatim, so BM25 would be expected to perform close to as well. In actuality it does, although it interestingly has a tendancy to prefer "Zero Gravity Chairs", probably from the body description of those placing heavy emphasis on features.

#### 4. small starter planting pots for young children

The semantics approach interprets this query not really in the sense for young human children but as for young children seedlings. Asides from this the results are as expected. BM25 also exhibits similar results, but this is where we start noticing that esepecially with BM25, there are cases where multiple extremely similar items are returned in the list, often from the same brand, and being even the same product with very minor differences.

#### 5. protection set for power drill

For this query, BM25 seems to overfixate on the last 2 words and returns mainly power drills and other products similar to this that are not considered protection sets. Semantics does better in providing protection equipment products, and from the results, it seems it considers a chainsaw to be extremely similar to a power drill.

### LLM Queries

These are the five queries categorized for the LLM method to perform well in, arranged in perceived difficulty. For the purpose of this report, these queries were designed with the intent of the BM25 and semantics methods struggling to return meaningful results here.


#### 1. highest rated patio decking options

Semantic model makes an interesting error here in that patio decking was somehow interpreted as various patio storage box options. BM25 on the other hand while more inconsistent did return `Diversitech Outdoor Gas Grill BBQ & Fire Pit Mat 48" x 30" - Protects Decks & Patios - 10 Year Warranty, Black` as the second highest option which does protect patio flooring, which is somewhat close to patio decking. Neither options appear to be sorted by `average_rating` and this behaviour holds for other queries that are more effective with LLM generated SQL solutions.

#### 2. least expensive rake for autumn leaves

Both models return various rakes fairly well but with no actual sorting on price. Adding "least expensive" to the query appears to help the semantic model somewhat as it does return some more inexpensive options.

#### 3. good souvinier plants for a trip returning from Peru

This query is fairly rigid which is how BM25 and semantic are able to return various plants that are at least somewhat related to Peru. Much of the challenge in these models is determing what would be considered a "souvenir plant"; semantic model appears to associate a gift box with such explaining how `Fat Plants San Diego Cactus Plants in Gift Box | Rooted in 4 inch Planter Pots with Soil | Living Indoor or Outdoor Plants | Gift Tin Pot Option (Peruvian Old Man)` was the top option, whereas BM25 cannot make this connection.

#### 4. best option to keep irrigation water cool while away for a long time

The thought was that with how open ended this query was, both models would struggle to provide a consistent set of responses. In actuality, both models appear to provide a set of reasonable responses for the query consisting of mist systems, faucet timers, smart wifi sprinklers, and irrigation kits. There are some outliers here and asides from the rankings no other explanation is given for what is the best option, but a user would likely be satisfied with these queries.

#### 5. the most impressive grill for an annual sasuage grilling competition

In both models, a few of the top 10 results were grills but there was also many other things that were only grill-related. Further more, there is very little actual reasoning prevalent as to what is considered an "impressive" grill for sausages, as no discernable patterns in average_rating or price can be found.

### Other Queries

These last five queries are fun challenges that could reasonably occur, and none of the methods (including LLM) may be able to provide results for these queries fully. See the [README section](https://github.com/UBC-MDS/DSCI_575_project_alx649_joelyp/blob/main/README.md#descriptions-of-the-other-section) for more description about these queries.
<!-- This link will be functional once dev is merged to main for milestone 1. Also this comment won't show up in the render. -->

#### 1. read plants for planting by small lake

This query was meant to be "reed plants for planting by small lake", but with a typo. The initial thought with both methods was that book related items would then appear which did not entirely happen. BM25 returned an assortment of items, most commonly welcome mats, while semantics was able to capture some context by returning mainly aquatic based planting items.

#### 2. 40 in 3D Simulation Bread Shape Pillow Soft Lumbar Baguette Back Cushion Funny Food Plush Stuffed Toy

The inclusion of this query is a [specific item sourced from Amazon](https://www.amazon.ca/Wepop-Simulation-Pillow-Cushion-Stuffed/dp/B07SHP29DM/ref=sr_1_11?dib=eyJ2IjoiMSJ9.XjrWVarAG8Mn0fh7F7AMoE1I2iW_naksuPUZZQD-0NFkMMTxL-ZULjykiibf5EEAyjgXaem_hq8taspvA2W9Rf1p10-_cjMoqVdV81eeqsWIy6PzDikO1R113to0m5Eg8YzWci6qZgoqhdqFpdAi7DRlgM1YKPPV7N7usvinlh0AfybVAH5mBrq0_PIoef6BKGJkqhyyar9cKeVx41ZnLl9VqSGbjNTP5qj0X5BmTA8ZkusYRPR7thKv3IZyk3eaEkwvLtrsBkHi0bTRgocuLjJtXzQUy_mLcdi9kKFR84A.mwHccl427IV85Sn1-BsGZVcXJEBRHy_dVxtcOr5yGPQ&dib_tag=se&keywords=random%2Bstuff&qid=1775713924&sr=8-11&th=1) that is not very related to gardening or patio related items, thus making it very poor for keyword matching methods. Surprisingly this nicheness seems to have helped BM25 because it's top result was pillow based (`RSH Décor Indoor Outdoor Set of 2 U-Shape Cushions and 2 Lumbar Pillows Weather Resistant, (Large, Medlo Sonoma)`) and more importantly, all of it's top 10 results were near identical. Semantics on the other hand did mostly return pillow typed items but also had more variation with the seating options, the sixth highest result (`Simplay3 Handy Home 3-Level Heavy Duty Work/Garden Seat - 12" x 15" x 9" - Green, Made in USA`) a somewhat distant match. 

#### 3. ydcpyf m.y.p un.qcxn. iape.b dro.

In this query the DVORAK keyboard setting was "mistakenly" used. If the characters were typed on a QWERTY keyboard, the actual query is `thirty meter flexible garden hose`. Neither BM25 nor semantics though are equipped with keyboard layout translators, thus the results are expectedly poor. Semantics returns all sorts of items with little actual connection, while BM25 outright has no results entirely, indicating absolutely no token matches.

#### 4. richardella ecuformis

This query is an attempted user recalling of a specific type of grass that grows mainly in Chile, mistaken first part of the scientific name with [Richardella dulcifica](https://toptropicals.com/catalog/uid/synsepalum_dulcificum.htm?srsltid=AfmBOoohgSrUzqeCqUY27htuuQQb1HxFhANXlBKv93Yca6dgG9kuzeWe), commonly known as "Miracle Fruit". BM25 seeing there is no matches for these exact words returns no results. Semantic in a similar case to the previous test case has no clue what is the context here and returns borderline random results.

#### 5. den mest kompakta och lättbärbara isbehållaren för att förvara kall champagne i över 12 timmar på en varm sommardag

As a last query that admittedly was just designed to be as confusing as possible while still being able to be linked to an actual product, this is a [Google translation of](https://translate.google.com/?hl=en&sl=auto&tl=sv&text=the%20most%20compact%20and%20carryable%20ice%20tub%20to%20store%20cold%20champagne%20in%20for%20over%2012%20hours%20on%20a%20hot%20summer%20day&op=translate) "the most compact and carryable ice tub to store cold champagne in for over 12 hours on a hot summer day" to Swedish. BM25 here does return some results; a variation of `Att Southern UR1212WH 12-Inch White Grecian Urn Planter - Quantity 33` appears three times in the top 10, with all other results being random and not related to an ice box. The semantic method is also mostly random, although it does have two vaugely alcohol related products in its top 10 (`Cork Sauna Mat (450 X 300 X 12MM)` and `19cm Resin Wine Bottle and Barrel Outdoor Fountain with Led Light, Beer Self-Circulating Water Garden Courtyard Lawn Decoration，Self-Circulating Water Feature Fountain`). In either case, neither method was really able to determine this was in a different language and checked for matches on a primarily English corpus.

## Summary of Method Findings

### BM25

The main strength of this model is the fixation on specific tokens; if a user knows a specific item they are looking for then this method can locate it quite easily. This search method is also aided if the query has more description, the query `tulip seeds red orange yellow green blue purple` shows this strength very well. However with the fixation on specific tokens, it does not understand when some tokens are more important than others. There are also cases where the context of these tokens are completely not understood such as with the `potting soil 10L` query returning tractor belts. Contextual understanding of a query is also not possible with this method as seen with the `protection set for power drill` query returning actual power drills. Lastly, there are also cases where BM25 can return no results entirely if none of the tokens match the corpus.

### Semantics

With semantic based methods, there is a better understanding of queries that have a specified meaning that do not explicitly state the product, such as the `container to put plants in` query. This contextual understanding can sometimes be taken too literally though, as the `tulip seeds red orange yellow green blue purple` query, which does mistakenly assume tulips grow from seeds (they grow from bulbs) led to this model assuming the user would be looking for sunflower seeds. There are signs of word connection, such as how chainsaws were heavily involved in the `protection set for power drill` query. Unlike BM25, this model can return a result under every query, but will at times not be able to return anything sensible. This is most apparent with the `Other` subset of queries, many of which LLM interpretation would be of assistance.

Additionally with both models, neither of these were really able to pick up on quantitative requests such as highest rated or least expensive. This is partially due to the implementation of these methods both only considering the written text of the title and descriptions of these products, and could be assisted if they were converted into hybrid models that also took the other columns of the dataframe into consideration. Other linguistic encodings (keyboard, languages, mispellings) also proved challenging for both models, and would be more easily processed with RAG based models that could use generated SQL to narrow the data to relevant items before selection. 

## Key Takeaways

- **BM25 excels at exact keyword matching** but is brittle outside this comfort 
  zone — a single unexpected token can completely derail results
- **Semantic search handles natural language better** but is limited by the 
  20,000 product subset indexed; many relevant products likely exist in the 
  remaining 830,000 that were not indexed
- **Neither method handles quantitative requests** — queries asking for 
  "highest rated" or "least expensive" require SQL-style filtering that pure 
  text retrieval cannot provide
- **Complex intent queries** (LLM category) exposed the ceiling of both methods 
  — understanding "souvenir", "impressive", or "competition" requires reasoning 
  beyond keyword or vector similarity
- **Edge cases are revealing** — DVORAK input, foreign languages, and scientific 
  names all fail completely, highlighting that real-world search needs robust 
  query preprocessing and language detection upstream
- **Hybrid search is the logical next step** — BM25 and semantic scores are 
  complementary; combining them would offset each method's individual weaknesses
- **RAG + LLM reranking** is expected to significantly improve results for the 
  LLM query category in Milestone 2 by enabling reasoning over retrieved candidates