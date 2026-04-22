import os
import re
from collections.abc import Callable
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from session_helper import init_session, load_model_and_index
import bm25
from hybrid import HybridRetriever
from prompts import prompt_template

load_dotenv()

# ── Retrievers ─────────────────────────────────────────────────────────────────

def retrieve_semantic(query, embedding_model, faiss_index, faiss_metadata, k=5):
    """
    Retrieve top k products using FAISS vector similarity.
    Returns a list of metadata dicts.
    """
    query_vec = embedding_model.encode([query]).astype('float32')
    distances, indices = faiss_index.search(query_vec, k)
    return [faiss_metadata[i] for i in indices[0]]


def retrieve_bm25(con, query, k=5):
    """
    Retrieve top k products using BM25 keyword search via DuckDB FTS.
    Returns a list of metadata dicts.
    """
    results = bm25.query_k_highest(con, query, k)
    return results.to_dict(orient='records')


def retrieve_hybrid(con, query, embedding_model, faiss_index, faiss_metadata, k=5):
    """
    Combine semantic and BM25 results, deduplicated by parent_asin.
    Semantic results take priority in ordering.
    Returns top k unique products.
    """
    retriever = HybridRetriever(embedding_model = embedding_model, faiss_index = faiss_index, faiss_metadata = faiss_metadata, k = k)
    results = retriever.query(con, query)
    return results.to_dict(orient='records')


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
    


def ask(query, llm, mode="hybrid", con = None, embedding_model = None, faiss_index = None, faiss_metadata = None):
    """
    Run a query through the RAG pipeline.

    Parameters
    ----------
    query : the user's search question
    llm : A ChatGroq instance configured with a valid API key
    mode  : 'semantic', 'bm25', or 'hybrid' (default)
    con : DuckDB connection necessary for bm25 and hybrid methods
    embedding_model : embedding model necessary for semantic and hybrid methods
    faiss_index : optimal FAISS index file necessary for semantic and hybrid methods
    faiss_metadata : optimal FAISS metadata file necessary for semantic and hybrid methods

    Returns
    -------
    dict with keys: answer, docs
    """
    if mode == "semantic":
        docs   = retrieve_semantic(query, embedding_model, faiss_index, faiss_metadata, k = 25)
    elif mode == "bm25":
        docs   = retrieve_bm25(con, query, k = 25)        
    else:
        docs   = retrieve_hybrid(con, query, embedding_model, faiss_index, faiss_metadata, k = 25)
    context = build_context(docs)
    # RAG Chain
    answer  = strip_thinking(
        (prompt_template | llm | StrOutputParser()).invoke(
            {"context": context, "question": query}
        )
    )
    return {"answer": answer, "docs": docs}


# ── Smoke test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    con = init_session()
    sem_model, faiss_index, faiss_metadata = load_model_and_index()

    # Setup LLM for RAG
    # NOTE: Ensure that .env has been setup with GROQ_API_KEY!
    try:
        llm = ChatGroq(
            model="qwen/qwen3-32b",
            api_key=os.getenv("GROQ_API_KEY")
        )
    except Exception as e:
        raise EnvironmentError(f"Ensure that the .env file has been configured with a working GROQ_API_KEY. Full details of the error are below:\n {e}")

    result = ask(query = "What is a good garden hose for 50ft?", 
                 llm = llm, 
                 mode="hybrid", 
                 con = con, 
                 embedding_model = sem_model, 
                 faiss_index = faiss_index, 
                 faiss_metadata = faiss_metadata)
    print("Answer:\n", result["answer"])
    print("\nTop products:")
    for d in result["docs"]:
        print(f"  - {d['title']}")
    con.close()