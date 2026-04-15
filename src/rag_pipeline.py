import os
import re
import faiss
import pickle
#import numpy as np
from collections.abc import Callable
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from session_helper import init_session
import bm25

load_dotenv()

# ── Paths and constants ────────────────────────────────────────────────────────

base_dir = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(base_dir, "../data/processed/faiss_index.bin")
FAISS_META_PATH  = os.path.join(base_dir, "../data/processed/faiss_meta.pkl")
MODEL_NAME       = "all-MiniLM-L6-v2"

# ── Load models and index once at import time ──────────────────────────────────

# Embedding model for encoding queries
embedding_model = SentenceTransformer(MODEL_NAME)

# FAISS index and associated product metadata
faiss_index = faiss.read_index(FAISS_INDEX_PATH)
with open(FAISS_META_PATH, 'rb') as f:
    faiss_metadata = pickle.load(f)

# DuckDB connection for BM25
con = init_session()

# ── Retrievers ─────────────────────────────────────────────────────────────────

def retrieve_semantic(query, k=5):
    """
    Retrieve top k products using FAISS vector similarity.
    Returns a list of metadata dicts.
    """
    query_vec = embedding_model.encode([query]).astype('float32')
    distances, indices = faiss_index.search(query_vec, k)
    return [faiss_metadata[i] for i in indices[0]]


def retrieve_bm25(query, k=5):
    """
    Retrieve top k products using BM25 keyword search via DuckDB FTS.
    Returns a list of metadata dicts.
    """
    results = bm25.query_k_highest(con, query, k)
    return results.to_dict(orient='records')


def retrieve_hybrid(query, k=5):
    """
    Combine semantic and BM25 results, deduplicated by parent_asin.
    Semantic results take priority in ordering.
    Returns top k unique products.
    """
    semantic_docs = retrieve_semantic(query, k=k)
    bm25_docs     = retrieve_bm25(query, k=k)

    # Deduplicate — first seen wins (semantic has priority)
    seen     = set()
    combined = []
    for doc in semantic_docs + bm25_docs:
        asin = doc.get('parent_asin')
        if asin not in seen:
            seen.add(asin)
            combined.append(doc)

    return combined[:k]


# ── Context builder ────────────────────────────────────────────────────────────

def build_context(docs):
    """
    Format a list of product metadata dicts into a prompt-ready context string.
    """
    return "\n\n".join(
        f"Product: {doc.get('title', 'N/A')}\n"
        f"ASIN: {doc.get('parent_asin', 'N/A')}\n"
        f"Rating: {doc.get('average_rating', 'N/A')}/5\n"
        f"Price: ${doc.get('price', 'N/A')}\n"
        f"Store: {doc.get('store', 'N/A')}"
        for doc in docs
    )


# ── Prompt template ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful Amazon shopping assistant specializing 
in patio, lawn and garden products. Answer the question using ONLY the 
provided product context. Be concise and cite product names when possible. 
If the context does not contain enough information, say so."""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])


# ── Output cleaner ─────────────────────────────────────────────────────────────

def strip_thinking(text):
    """Remove <think>...</think> chain-of-thought blocks from model output."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


# ── RAG chains ─────────────────────────────────────────────────────────────────

def build_rag_chain(llm: ChatGroq, context_func: Callable):
    """
    Construct a RAG chain.

    Parameters
    ----------
    llm : A ChatGroq instance configured with a valid API key
    context_func  : Callable function for providing context for the LLM.

    Returns
    -------
    RunnableSerializable: A runnable RAG Chain object.
    """
    rag_chain = (
        {
            "context": RunnableLambda(lambda q: build_context(context_func(q))),
            "question": RunnablePassthrough()
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )
    return rag_chain
    


def ask(query, llm, mode="hybrid"):
    """
    Run a query through the RAG pipeline.

    Parameters
    ----------
    query : the user's search question
    llm : A ChatGroq instance configured with a valid API key
    mode  : 'semantic', 'bm25', or 'hybrid' (default)

    Returns
    -------
    dict with keys: answer, docs
    """
    if mode == "semantic":
        docs   = retrieve_semantic(query)
        answer = strip_thinking(build_rag_chain(llm, retrieve_semantic).invoke(query))
    elif mode == "bm25":
        docs   = retrieve_bm25(query)
        # BM25-only uses same prompt, just different context
        context = build_context(docs)
        answer  = strip_thinking(
            (prompt_template | llm | StrOutputParser()).invoke(
                {"context": context, "question": query}
            )
        )
    else:
        docs   = retrieve_hybrid(query)
        answer = strip_thinking(build_rag_chain(llm, retrieve_hybrid).invoke(query))

    return {"answer": answer, "docs": docs}


# ── Smoke test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # Setup LLM for RAG
    # NOTE: Ensure that .env has been setup with GROQ_API_KEY!
    try:
        llm = ChatGroq(
            model="qwen/qwen3-32b",
            api_key=os.getenv("GROQ_API_KEY")
        )
    except Exception as e:
        raise EnvironmentError(f"Ensure that the .env file has been configured with a working GROQ_API_KEY. Full details of the error are below:\n {e}")

    result = ask("What is a good garden hose for 50ft?", llm = llm, mode="hybrid")
    print("Answer:\n", result["answer"])
    print("\nTop products:")
    for d in result["docs"]:
        print(f"  - {d['title']}")
    con.close()