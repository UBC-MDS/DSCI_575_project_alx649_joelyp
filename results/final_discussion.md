# Final Discussion

## Step 1: Improve Your Workflow

### Dataset Scaling

For local development the full 367,832 products and 15.5M reviews are used via 
the processed DuckDB. 

For Streamlit cloud deployment a random sample of 15,000 
products and up to 5 of the most helpful reviews (totalling a final 43243 reviews) was used to keep all files under GitHub's 100MB per-file limit.

### LLM Experiment
- Models compared (name, family, size)

| Name | Family | Size | Description |
| `llama-3.1-8b-instant` | LLaMA | 8B | Smallest/fastest model tested |
|`qwen/qwen3-32b`| Qwen | 32B |  Mid-sized, open sourced, good previous experiences|
| `openai/gpt-oss-20b` | OpenAI OSS | 20B | Mid-size, most conservative responses |
| `llama-3.3-70b-versatile` | LLaMA | 70B | Largest model, surprisingly shallow outputs |

See `results/milestone2_discussion` for more detailed explanation Qwen3-32B

### System Prompt Used for all Models

```You are a helpful Amazon shopping assistant specializing 
in patio, lawn and garden products. Answer the question using ONLY the 
provided product context. Be concise and cite product names when possible. 
If the context does not contain enough information, say so.```

### Results and discussions
`qwen/qwen3-32b` was retained as the default. It consistently produced the most 
accurate, well-reasoned, and citation-rich responses across all query types. See 
`results/llm_comparison.md` for the full side-by-side comparison of all 5 prompts.

## Step 2: Additional Feature (state which option you chose)

### What You Implemented

For milestone 3 we deployed the Amazon Recommender to a website based application on Streamlit, for which the current working deployment from the `main` branch can be found at [https://amazon-recommender-alx649-joelyp.streamlit.app](https://amazon-recommender-alx649-joelyp.streamlit.app).

- Description of the feature
(summarize README?)

Demonstration of all of the features can be found in [this explanation video:](replace with link to video for demo purposes later)


## Step 3: Improve Documentation and Code Quality

<!--This interestingly will probably just end up being the changelog for v0.3.0-->

## Added

### Documentation Updates
<!-- Summary of `README` improvements -->
- Include a `Known Issues` section for minor bugs with the application that are to be expected (#46).



## Changed

### Code Quality Changes
- Changed the `GROQ_API_KEY` text box for RAG Mode to a hidden text field (#46)

## Removed



## Step 4: Cloud Deployment Plan

### Data Storage
- **Raw data**: stored locally only, gitignored — too large for any cloud storage
- **Processed data**: `data/streamlitdeployment/` committed to GitHub (under 100MB per file)
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