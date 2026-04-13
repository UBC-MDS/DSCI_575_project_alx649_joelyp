# DSCI_575_project_alx649_joelyp

This project is a product recommendation tool utilizing the [2023 Amazon Review Dataset](https://amazon-reviews-2023.github.io) for patio, lawn, and garden items. Currently, there are two retriever methods implemented in this project: a BM25 keyword retriever using DuckDB FTS index and a semantic retriever using FAISS and sentence-transformers. For milestone 2, a LLM powered retrieving method will be implemented as well as an app for live interaction with the search system which is currently in progress.


## Setup


### Environment Setup

Navigate to the repo folder after cloning and run the following:

```
conda env create -f environment.yml
conda activate amazon-recommender
```

### Data Preprocessing

Once this is done, download the `Patio_Lawn_and_Garden` dataset from [https://amazon-reviews-2023.github.io](https://amazon-reviews-2023.github.io) and store both `meta_Patio_Lawn_and_Garden.jsonl` and `Patio_Lawn_and_Garden.jsonl` in the `data/raw` folder. Then run all cells in `notebooks/milestone1_preprocessing.ipynb` to generate the following files:

- Sample JSON files containing the first 100 entries from each file (`data/processed/meta_Patio_Lawn_and_Garden_sample.jsonl` and `data/procssed/Patio_Lawn_and_Garden_sample.jsonl`)
- Cleaned up CSV files containing only the required subset of the raw JSON data (`data/processed/meta_clean.csv` and `data/processed/reviews_clean.csv`)
- Parquet files from the CSV files generated (`data/processed/meta_clean.parquet` and `data/processed/reviews_clean.parquet`)
- DuckDB tables for use in the actual searches (`data/processed/amazon_reviews.duckdb`)

Note that the full generation of these files will take around 10 minutes to complete, which may be faster depending on computer RAM and processing power. You should also ensure at least 10 GB of additional hard disk memory to store the generated files.

### Building the Semantic Index

After running `notebooks/milestone1_preprocessing.ipynb`, build the FAISS index by running:
```
python src/semantic.py
```

### Running the App

Use the following command to run the app locally (note this may take a while to load depending on computer):

```
streamlit run app/app.py
```

Currently, the dev branch version of the app is deployed at [https://amazon-recommender-dev.streamlit.app](https://amazon-recommender-dev.streamlit.app). The main branch version will be linked in the Github "About" section and added to this README in Milestone 2 once implemented.


## Source Files

- `src/bm25.py` — BM25 keyword retriever using DuckDB FTS index
- `src/semantic.py` — Semantic retriever using FAISS and sentence-transformers
- `src/session_helper.py` — DuckDB connection and LangChain document utilities
- `src/retrieval_metrics.py` — Runs all test queries through both retrievers and saves results to `results/test_queries/`


## Test Query Dataset

Within `data/processed/test_queries.csv`, there is a dataframe consisting of all the queries used to test the BM25 and semantic methods as well as LLM once it is completed in Milestone 2. This is a description of the columns:

- `query`: The actual query
- `expected_method`: One of BM25, semantic, LLM, or Other indicating the method that is expected to perform best
- `difficulty`: A manual 1 to 5 integer score based on initial human estimates of how well the expected best method is going to perform on this (1 indicating a very simple example where a well matching item can be found, 5 being that it's unlikely any exact results will occur).


### Descriptions of the `Other` Section

The queries labelled as `Other` are meant to be somewhat extraneous but possible queries a user could make that could be quite challening for any of the methods to answer sufficiently. Some of these are here mostly out of interest to see what will happen.


| Query | Explanation | Expected Best Method|
| -------- | -------- | --------------- | 
| read plants for planting by small lake | Meant to be "reed plants for planting by small lake", but with a typo. | semantic/LLM | 
| 40 in 3D Simulation Bread Shape Pillow Soft Lumbar Baguette Back Cushion Funny Food Plush Stuffed Toy | [Specific item sourced from Amazon](https://www.amazon.ca/Wepop-Simulation-Pillow-Cushion-Stuffed/dp/B07SHP29DM/ref=sr_1_11?dib=eyJ2IjoiMSJ9.XjrWVarAG8Mn0fh7F7AMoE1I2iW_naksuPUZZQD-0NFkMMTxL-ZULjykiibf5EEAyjgXaem_hq8taspvA2W9Rf1p10-_cjMoqVdV81eeqsWIy6PzDikO1R113to0m5Eg8YzWci6qZgoqhdqFpdAi7DRlgM1YKPPV7N7usvinlh0AfybVAH5mBrq0_PIoef6BKGJkqhyyar9cKeVx41ZnLl9VqSGbjNTP5qj0X5BmTA8ZkusYRPR7thKv3IZyk3eaEkwvLtrsBkHi0bTRgocuLjJtXzQUy_mLcdi9kKFR84A.mwHccl427IV85Sn1-BsGZVcXJEBRHy_dVxtcOr5yGPQ&dib_tag=se&keywords=random%2Bstuff&qid=1775713924&sr=8-11&th=1) designed for keyword matching that is not very related to gardening or patio related items. | BM25 | 
| ydcpyf m.y.p un.qcxn. iape.b dro. | Meant to be "thirty meter flexible garden hose", but typed on a DVORAK keyboard instead of an intended QWERTY keyboard. | LLM |
| richardella ecuformis | Attempted user recalling of a specific type of grass that grows mainly in Chile, mistaken first part of the scientific name with [Richardella dulcifica](https://toptropicals.com/catalog/uid/synsepalum_dulcificum.htm?srsltid=AfmBOoohgSrUzqeCqUY27htuuQQb1HxFhANXlBKv93Yca6dgG9kuzeWe), commonly known as "Miracle Fruit" | semantic | 
| den mest kompakta och lättbärbara isbehållaren för att förvara kall champagne i över 12 timmar på en varm sommardag  | [Google translation of](https://translate.google.com/?hl=en&sl=auto&tl=sv&text=the%20most%20compact%20and%20carryable%20ice%20tub%20to%20store%20cold%20champagne%20in%20for%20over%2012%20hours%20on%20a%20hot%20summer%20day&op=translate) "the most compact and carryable ice tub to store cold champagne in for over 12 hours on a hot summer day" to Swedish  | LLM |

## Results

Full discussion of the results from running the BM25 and semantic searches on `data/processed/test_queries.csv` can be found in `results/milestone1_discussion.md`.


## References

This project utilizes the [Amazon Reviews 2023 Dataset](https://amazon-reviews-2023.github.io) collected by [McAuley Lab](https://cseweb.ucsd.edu/~jmcauley/).

## Contributors

### Alexander Wen

- **Affiliation**: University of British Columbia
- **GitHub**: [@alxwen711](https://github.com/alxwen711)


### Joel Nicholas Peterson

- **Affiliation**: University of British Columbia
- **GitHub**: [@j031nich0145](https://github.com/j031nich0145)




