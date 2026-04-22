# Final Discussion

## Improved Workflow

### Dataset Scaling

For local development the full 367,832 products and 15.5M reviews are used via 
the processed DuckDB. 

For Streamlit cloud deployment a random sample of 15,000 
products and up to 5 of the most helpful reviews (totalling a final 43243 reviews) was used to keep all files under GitHub's 100MB per-file limit.

### LLM Experiment
Models compared (name, family, size)

| Name | Family | Size | Description |
|------|--------|------|-------------|
| `llama-3.1-8b-instant` | LLaMA | 8B | Smallest/fastest model tested |
| `openai/gpt-oss-20b` | OpenAI OSS | 20B | Mid-size, most conservative responses |
|`qwen/qwen3-32b`| Qwen | 32B |  Mid-sized, open sourced, good previous experiences|
| `llama-3.3-70b-versatile` | LLaMA | 70B | Largest model, surprisingly shallow outputs |

See `results/milestone2_discussion` for more detailed explanation for using Qwen3-32B

### System Prompt Used for all Models

\```You are a helpful Amazon shopping assistant specializing 
in patio, lawn and garden products. Answer the question using ONLY the 
provided product context. Be concise and cite product names when possible. 
If the context does not contain enough information, say so.\```

### Results and discussions
`qwen/qwen3-32b` was retained as the default. It consistently produced the most 
accurate, well-reasoned, and citation-rich responses across all query types. See 
`results/llm_comparison.md` for the full side-by-side comparison of all 5 prompts.

## Additional Feature 

### What You Implemented 

For milestone 3 we deployed the Amazon Recommender to a website based application on Streamlit, for which the current working deployment from the `main` branch can be found at [https://amazon-recommender-alx649-joelyp.streamlit.app](https://amazon-recommender-alx649-joelyp.streamlit.app).

- Description of the feature
(summarize README?)

Demonstration of all of the features can be found in [this explanation video:](replace with link to video for demo purposes later)


## Improved Documentation and Code Quality

<!--This interestingly will probably just end up being the changelog for v0.3.0-->

## Added

- Working Streamlit deployment (#51)

### Documentation Updates
<!-- Summary of `README` improvements -->
- Include a `Known Issues` section for minor bugs with the application that are to be expected (#46).



## Changed

### Code Quality Changes
- Changed the `GROQ_API_KEY` text box for RAG Mode to a hidden text field (#46)
- Removed most of the constant file path values within the codebase (#51)



## Cloud Deployment Plan

For this project we utilized Streamlit for deployment to (https://amazon-recommender-alx649-joelyp.streamlit.app/)[https://amazon-recommender-alx649-joelyp.streamlit.app/] from a public GitHub repository. Utilizing AWS would have a similar process with additional changes primarily in data storage so that the entire dataset could be utilized.

### Data Storage

The main draw back of deploying from a public Github repository is that every file on GitHub is restricted to being at most 100 MB, which is why a random sample of 15000 products and most of their reviews were utilized for this deployment. A single S3 bucket can be setup to store all data and indices similar to this repository, just on a larger scale. This would be the locations of all of the respective files:

|Files|Location|
|-|-|
|Raw Data| `raw/meta_Patio_Lawn_and_Garden.jsonl` , `raw/Patio_Lawn_and_Garden.jsonl`|
|Processed duckDB|`processed/amazon_reviews.duckdb`|
|FAISS index|`processed/faiss_index_merged.bin`,`processed/faiss_index_merged.pkl`|

The [2023 Amazon Patio and Home Dataset](https://amazon-reviews-2023.github.io) used was roughly 10.5 GB, and would be larger if we were to consider additional data from further years being added. However, the FAISS index only relies on the processed duckDB to be generated, so upon concating new product metadata and reviews on a monthly basis to `processed/amazon_reviews.duckdb`, the raw data as well as the intermediate files generated to update the duckDB would be removable on a regular basis to prevent this amount of data from being too excessive for storage costs. Each month the BM25 index would also be recreated in the processed DuckDB via `PRAGMA create_fts_index`; from local testing, this took under 10 minutes each time, so temporarily pausing the service and rerunning this with a basic EC2 instance would be sufficient.


### Compute

Streamlit Community Cloud's free tier was utilized for running this app. Website testing showed that queries were very time efficient, each taking at most a few seconds before displaying results. Thus it would be possible to setup a cluster of on-demand `t3a.micro` instances, this way each user could when needed be assigned a node to run the app, thus solving the concurrency challenge. In the case that a single node has to be dedicated to keeping a single Streamlit website up for the app, a larger instance such as `t3a.large` can be setup as a head node with several `t3a.nano` executor nodes on demand to handle feedback logging; in this scenario concurrency would be handled by Streamlit's built-in session isolation and each user gets their own session state. From how we set up the RAG mode, all LLM inference would use Groq API, thus being fully hosted, and no local compute being required.

### Streaming/Updates

Updating the data was partially discussed in the `Data Storage` section, and using the above infrastructure improvments specifically for cloud deployment, the amount of time to rerun `deployment_preprocessing.ipynb` would mostly be dependent on the amount of new data coming in instead of requiring a full rebuild each time. The only part not addressed being how the FAISS index would be updated. For the 15000 product website deployment, it took about half an hour locally to create the FAISS index. What is possible then is to create a separate ECS cluster specifically for the task of reading through `processed/amazon_reviews.duckdb` and rebuilding the FAISS index, speeding this task up with several `t3a.large` worker nodes as necessary. Even if this process takes a few hours or longer, this setup would not interfere with the actively running Streamlit cloud deployment, and only upon completion can this new FAISS index replace the old one. Furthermore, the performance of the semantic search using a FAISS index that does not include every product in the database is still relatively high; within our local deployment, we took a sample of 20000 of the 367000+ products to build a manageable FAISS index, and this was still sufficent to produce results that were qualatitively stronger than the BM25 method on its own. 