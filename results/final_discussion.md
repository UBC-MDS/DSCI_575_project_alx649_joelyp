# Final Discussion

## Step 1: Improve Your Workflow

### Dataset Scaling
- Number of products used

There are 367832 meta data documents and 15495259 reviews, products is number of meta data documents

- Changes to sampling strategy (if any)

Discuss sampling sizes used here for the streamlit deployment

### LLM Experiment
- Models compared (name, family, size)

| Name | Family | Size | Description |
|-|-|-|-|
|`qwen/qwen3-32b`| Qwen | 32 billion parameters, 64 layers | Initial setup utilized in Milestone 2, see `results/milestone2_discussion` for more detailed explanation|

- Results and discussions
    - Prompt used (copy it here)

```
You are a helpful Amazon shopping assistant specializing 
in patio, lawn and garden products. Answer the query using ONLY the 
provided product context. Be concise and cite names and ASIN only for products matching the query. 
In the case where there are no results that reasonably fit the query, briefly describe the general
products that were returned. Request for additional clarification in the query if necessary.
```
    - Results
    
    Very similar to Milestone 2 section, rewrite upon new test Wednesday
- Which model you chose and why

## Step 2: Additional Feature (state which option you chose)

### What You Implemented

For milestone 3 we deployed the Amazon Recommender to a website based application on Streamlit, for which the current working deployment from the `main` branch can be found at [https://amazon-recommender-alx649-joelyp.streamlit.app](https://amazon-recommender-alx649-joelyp.streamlit.app).

- Description of the feature
(summarize README?)

Demonstration of all of the features can be found in [this explanation video:](replace with link to video for demo purposes later)


  
## Step 3: Improve Documentation and Code Quality

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



## Step 4: Cloud Deployment Plan

### Data Storage: 

Where will you store the following?
raw data
processed data
vector index
BM25 index

### Compute
Where will your app run?
How will you handle multiple users (concurrency)?
How will you handle LLM inference (API vs hosted model)?

### Streaming/Updates
How will you incorporate new products in production?
How will your pipeline stay up to date?