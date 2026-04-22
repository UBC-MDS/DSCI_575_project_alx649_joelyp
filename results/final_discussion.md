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

## Current Deployment Specs

### Data Storage
- **Raw data**: stored locally only and is gitignored as it's too large for GitHub
- **Processed data**: `data/streamlitdeployment/` committed to GitHub as smaller sample is under 100MB per file
- **Vector index**: `faiss_index_deploy.bin` committed to GitHub in streamlitdeployment/
- **BM25 index**: rebuilt at app startup from the deploy DuckDB via PRAGMA create_fts_index

### Compute
- App runs on Streamlit Community Cloud's free tier
- Concurrency is handled by Streamlit's built-in session isolation and each user gets 
  their own session state
- All LLM inference uses Groq API: fully hosted, no local compute required

### Streaming/Updates
- New products would require rerunning `deployment_preprocessing.ipynb` to regenerate 
  the deploy DuckDB and FAISS index, then committing the updated files
- The pipeline has no automated update mechanism and updates are manual at this time

### Cloud Deployment Plan (AWS)

### Data Storage
- **Raw data**: Stored in **Amazon S3** (standard tier): cost-effective for large 
  files, never committed to git. The full 10GB dataset would cost ~$0.23/month to store.
- **Processed data**: Also in **S3**: the cleaned CSVs, parquet files, and DuckDB 
  would live in a private S3 bucket and be pulled to the compute instance on startup.
- **Vector index**: FAISS index stored in **S3**: loaded into memory at app startup. 
  For production scale, this would be replaced with **Amazon OpenSearch** which supports native vector similarity search without loading everything into RAM.
- **BM25 index**: Rebuilt at startup from the DuckDB via `PRAGMA create_fts_index`, 
  or replaced with **Amazon OpenSearch** full-text search which natively supports BM25.

### Compute
- **App runtime**: **AWS Elastic Beanstalk** or **AWS App Runner** for the Streamlit 
  app: both handle auto-scaling and deployment from a container image. Alternatively 
  an **EC2 t3.medium** instance (~$30/month) for a simple single-server deployment.
- **Concurrency**: With Elastic Beanstalk, multiple EC2 instances can run behind an 
  **Application Load Balancer**: each user session is routed to an available instance. 
  The FAISS index would be loaded once per instance and shared across sessions via 
  Streamlit's `@st.cache_resource`.
- **LLM inference**: Continue using **Groq API** for LLM calls: fully hosted, no 
  GPU compute needed on our end. For a self-hosted alternative, **AWS SageMaker** 
  could host the Qwen model on a GPU instance, but at significantly higher cost.

### Streaming/Updates
- New product data would land in **S3** via a scheduled **AWS Lambda** function that 
  pulls from the Amazon Reviews dataset periodically.
- An **AWS Glue** ETL job would rerun the preprocessing pipeline to update the DuckDB 
  and regenerate the FAISS index, saving the new files back to S3.
- The app would pick up the new index on its next cold start, or a manual restart 
  could be triggered via Elastic Beanstalk's rolling deployment.
- For real-time updates, **Amazon Kinesis** could stream new review data directly into 
  the pipeline, though this is overkill for a product recommendation tool with 
  infrequent dataset updates.