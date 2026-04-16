import streamlit as st
import pandas as pd
import sys
import os
import csv
import warnings
from datetime import datetime

# Suppress FutureWarnings from transformers and disable tokenizer parallelism
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ── Path setup ─────────────────────────────────────────────────────────────────
# Add src/ to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from session_helper import init_session, load_model_and_index, construct_groq_instance
from rag_pipeline import ask               # unified RAG entry point used in Tab 2
import bm25                               # BM25 keyword retriever
import semantic                          # FAISS semantic retriever
from hybrid import HybridRetriever      # Hybrid retriever

# ── Page config ────────────────────────────────────────────────────────────────
# layout="wide" uses the full browser width
st.set_page_config(
    page_title="Amazon PLG Search",
    page_icon="🌿",
    layout="wide"
)

# ── Load resources ─────────────────────────────────────────────────────────────
# @st.cache_resource ensures these heavy objects are only loaded once per session
@st.cache_resource
def get_connection():       # opens read-only DuckDB connection to processed database
    return init_session()

@st.cache_resource
def get_semantic_resources():      # loads SentenceTransformer, FAISS, product metadata
    return load_model_and_index()

con = get_connection()
sem_model, sem_index, sem_metadata = get_semantic_resources()

# Session state memory values
if "search_results" not in st.session_state:
    st.session_state.last_query = ""
    st.session_state.last_method = ""
    st.session_state.search_results = []

if "flash_message" in st.session_state:
    st.toast(st.session_state.flash_message, icon="✅")
    del st.session_state.flash_message # Clear it so it only shows once

# ── Feedback storage ───────────────────────────────────────────────────────────
FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "../data/processed/feedback.csv")

def save_feedback(query, method, asin, title, vote):
    """
    Append a single feedback row to the feedback CSV.
    Creates the file with headers if it doesn't exist yet.

    Parameters
    ----------
    query  : the search string the user entered
    method : which retrieval method was used (BM25, Semantic, Hybrid, RAG-*)
    asin   : the product's parent_asin identifier
    title  : the product title shown to the user
    vote   : 'up' or 'down'
    """
    file_exists = os.path.exists(FEEDBACK_PATH)
    with open(FEEDBACK_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['timestamp', 'query', 'method', 'asin', 'title', 'vote']
        )
        if not file_exists:      # only write header row if file being created for first time
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.now().isoformat(),
            'query':     query,
            'method':    method,
            'asin':      asin,
            'title':     title,
            'vote':      vote
        })

# ── Star rating helper ─────────────────────────────────────────────────────────
def stars(rating):
    """
    Convert a numeric rating (e.g. 4.2) into a star string (e.g. ★★★★☆  4.2).
    Rounds to the nearest whole star to avoid half-star unicode issues.
    Returns 'No rating' if the value is missing or non-numeric.
    """
    if not rating or str(rating) == 'nan':
        return "No rating"
    r      = float(rating)
    filled = int(round(r))   # round to nearest whole number of stars
    empty  = 5 - filled
    return "★" * filled + "☆" * empty + f"  {r:.1f}"

# ── Price formatter ────────────────────────────────────────────────────────────
def format_price(price):
    """
    Safely format a price value as a dollar string.
    Returns 'Price unavailable' for NaN, None, or non-numeric values —
    which are common in this dataset since many products have no listed price.
    """
    try:
        val = float(price)
        if pd.isna(val):
            return "Price unavailable"
        return f"${val:.2f}"
    except (TypeError, ValueError):
        return "Price unavailable"

# ── Result card renderer ───────────────────────────────────────────────────────
def render_result(doc, idx, query, method, show_score=True):
    """
    Render a single product result as a bordered Streamlit container.
    Displays title, rating, price, store, and optionally the retrieval score.
    Includes thumbs up/down feedback buttons that write to feedback.csv.
    Feedback system is race-condition-proof.

    Parameters
    ----------
    doc        : dict of product metadata (parent_asin, title, rating, etc.)
    idx        : zero-based position in the results list (used for display + button keys)
    query      : the original search query (stored in feedback)
    method     : retrieval method used (stored in feedback)
    show_score : whether to display the retrieval score (True for Search, False for RAG)
    """
    title  = doc.get('title', 'Unknown Product')
    asin   = doc.get('parent_asin', 'N/A')
    # average_rating is from metadata => rating is from reviews — check both
    rating = doc.get('average_rating') or doc.get('rating')
    price  = doc.get('price')
    store  = doc.get('store', '')
    score  = doc.get('score')

    # Define a unique key for the widget and the lock
    # Including 'method' and 'idx' ensures keys don't collide if the 
    # same ASIN appears in different search types or positions.
    fb_key = f"fb_{method}_{asin}_{idx}"
    lock_key = f"lock_{fb_key}"

    # Initialize the lock for this specific result if it doesn't exist
    if lock_key not in st.session_state:
        st.session_state[lock_key] = False

    with st.container(border=True):
        st.markdown(f"**{idx + 1}. {title}**")

        cols = st.columns([2, 2, 2, 2])
        cols[0].caption(f"Rating: {stars(rating)}")
        cols[1].caption(f"Price: {format_price(price)}")
        cols[2].caption(f"Store: {store if store else 'N/A'}")
        if show_score and score:
            cols[3].caption(f"Score: {score:.3f}")

        fb, _ = st.columns([2, 8])
        with fb:
            # The widget is disabled once the lock is set to True
            feedback_val = st.feedback(
                options="thumbs", 
                key=fb_key,
                disabled=st.session_state[lock_key]
            )

            # Check if user interacted AND we haven't processed this vote yet
            if feedback_val is not None and not st.session_state[lock_key]:
                # 1. SET LOCK IMMEDIATELY
                st.session_state[lock_key] = True
                
                # 2. Map and Save (1 = Up, 0 = Down)
                score_type = "up" if feedback_val == 1 else "down"
                save_feedback(query, method, asin, title, score_type)
                
                # 3. Provide immediate UI feedback
                st.session_state.flash_message = f"Recorded feedback for {title}"

                # 4. Rerun to refresh the UI and show the 'disabled' state
                st.rerun()
 
# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🌿 Amazon Patio, Lawn & Garden Search")
st.caption("Search 367,000+ products using keyword, semantic, hybrid, or AI-powered RAG search.")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────

tab_search, tab_rag = st.tabs(["🔍 Search Only", "RAG Mode"])
with tab_search:
# TAB 1 - Search Only
    # st.form groups the text input, radio, and submit button together
    with st.form(key="search_form"):
        s_col1, s_col2 = st.columns([3, 1])
        with s_col1:
            search_query = st.text_input(
                "Search query",
                placeholder="e.g. garden hose 50ft, something to keep pests away..."
            )
        with s_col2:
            search_method = st.radio(
                "Method",
                options=["BM25", "Semantic", "Hybrid"],
                horizontal=True
            )
        # form_submit_button triggers on both button click and Enter key
        search_btn = st.form_submit_button("🔍 Search", use_container_width=True)

    if search_btn and search_query.strip():
        # Clear previous search's feedback locks
        for key in list(st.session_state.keys()):
            if key.startswith("lock_fb_"):
                del st.session_state[key]

        with st.spinner("Searching..."):
            st.session_state.last_query = search_query
            st.session_state.last_method = search_method
            results = None
            if search_method == "BM25":
                # Keyword search via DuckDB FTS index — fast, exact token matching
                results = bm25.query_k_highest(con, search_query, k=25).to_dict(orient='records')
            
            elif search_method == "Semantic":
                # Vector similarity search via FAISS — captures intent, not just keywords
                res     = semantic.query_k_highest(con, search_query, k=25)
                results = res.to_dict(orient='records') if isinstance(res, pd.DataFrame) else res
            
            else:  # Hybrid
                # Combine both retrievers and deduplicate by parent_asin
                # Semantic results take priority => BM25 fills in any gaps
                hr = HybridRetriever(k = 25)
                res = hr.query(con, search_query)
                results = res.to_dict(orient='records') if isinstance(res, pd.DataFrame) else res
            st.session_state.search_results = results
                
        st.markdown(f"**Top {len(results)} results** for *\"{search_query}\"* — **{search_method}**")
        st.divider()

    if st.session_state.search_results:
        for i, doc in enumerate(st.session_state.search_results):
            render_result(doc, i, search_query, search_method)
        
    elif search_btn: # No results
        # Submitted with an empty query
        if search_query == "": # blank query
            st.warning("Please enter a search query.")
        else:
            st.warning("No results found. Try a different query or search method.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RAG Mode
with tab_rag:
    st.caption("AI-generated answers grounded in real product data.")

    with st.form(key="rag_form"):
        r_col1, r_col2 = st.columns([3, 1])
        with r_col1:
            rag_query = st.text_input(
                "Ask a question",
                placeholder="e.g. What is the best garden hose for 50ft?"
            )
        with r_col2:
            rag_method = st.radio(
                "Retriever",
                options=["Hybrid", "Semantic", "BM25"],
                horizontal=True
            )
        rag_key = st.text_input(
            "Add Groq API Key here (tries to use .env key if not entered and running locally)",
            placeholder="gsk_0123456789XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
        rag_btn = st.form_submit_button("🤖 Ask", use_container_width=True)

    if rag_btn and rag_query.strip():
        # Clear locks
        for key in list(st.session_state.keys()):
            if key.startswith("lock_fb_"):
                del st.session_state[key]

        with st.spinner("Retrieving and generating answer..."):
            # Use a unique key for RAG state to avoid Search Tab conflicts
            llm_instance = construct_groq_instance(rag_key)
            result = ask(rag_query, llm=llm_instance, mode=rag_method.lower())
            
            st.session_state.rag_results = result  # Dedicated RAG key
            st.session_state.last_rag_query = rag_query
            st.session_state.last_rag_method = rag_method

    # Rendering outside the 'if rag_btn' block for persistence
    if st.session_state.get("rag_results"):
        res = st.session_state.rag_results
        q_text = st.session_state.get("last_rag_query", "")
        m_text = st.session_state.get("last_rag_method", "")

        st.info(res["answer"], icon="🤖")

        st.markdown(f"**Retrieved Products for:** *\"{q_text}\"*")
        st.divider()

        # Iterate over the 'docs' list specifically
        for i, doc in enumerate(res.get("docs", [])):
            # Pass the query/method from session_state so they persist during feedback
            render_result(doc, i, q_text, f"RAG-{m_text}")

    elif rag_btn:
        st.warning("Please enter a question.")