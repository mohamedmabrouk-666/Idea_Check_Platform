# ============================================================
# core/similarity.py
# The NLP Similarity Engine — TF-IDF + Cosine Similarity
# Sprint 11 addition: Cache system
#
# General idea of caching:
#   Without cache: every student request rebuilds the TF-IDF
#                  matrix from scratch (slow with many projects)
#   With cache:    TF-IDF matrix is built ONCE and stored in
#                  memory — all students share the same matrix
#                  Cache is cleared when admin adds/edits/deletes
#                  a project so results always stay accurate
# ============================================================

from sklearn.feature_extraction.text import TfidfVectorizer  # Converts text to vectors
from sklearn.metrics.pairwise import cosine_similarity        # Measures similarity between vectors
import json                                                    # For JSON serialization

# ── Cache storage — lives in memory while Flask app is running ─
# These variables hold the pre-computed TF-IDF data
# They are None when the cache is empty (first run or after clear)
_cache_vectorizer   = None  # The fitted TF-IDF vectorizer object
_cache_tfidf_matrix = None  # The pre-computed matrix for all old projects
_cache_projects     = None  # The list of old projects used to build the cache
_cache_project_ids  = None  # List of project IDs — used to detect if DB changed

def clear_cache():
    """
    Clear the TF-IDF cache from memory.
    Called by admin routes whenever a project is added, edited, or deleted.
    This forces the next request to rebuild the matrix with fresh data.
    Without this, changes to the projects DB would not affect similarity results.
    """
    global _cache_vectorizer, _cache_tfidf_matrix, _cache_projects, _cache_project_ids
    _cache_vectorizer   = None  # Reset vectorizer
    _cache_tfidf_matrix = None  # Reset matrix
    _cache_projects     = None  # Reset project list
    _cache_project_ids  = None  # Reset ID list
    # After this function runs, next call to calculate_similarity rebuilds everything

def _build_cache(old_projects):
    """
    Build and store the TF-IDF matrix for all old projects.
    Called automatically on the first request after cache is empty.
    Parameters:
        old_projects (list) — list of project dicts from DB
    """
    global _cache_vectorizer, _cache_tfidf_matrix, _cache_projects, _cache_project_ids

    # Combine title + description for each old project into one text string
    corpus = [p["title"] + " " + p["description"] for p in old_projects]

    # Build and fit the TF-IDF vectorizer on all old project texts
    # stop_words='english' removes common words like: the, is, and, a, to
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)  # Convert all texts to vectors at once

    # Store everything in the cache variables
    _cache_vectorizer   = vectorizer    # Save fitted vectorizer for transforming new inputs
    _cache_tfidf_matrix = tfidf_matrix  # Save pre-computed matrix for old projects
    _cache_projects     = old_projects  # Save project list for returning match details
    _cache_project_ids  = [p["id"] for p in old_projects]  # Save IDs for change detection

def calculate_similarity(new_title, new_description, old_projects):
    """
    Compare a new project idea against all old projects.
    Uses cache for the old projects matrix — only rebuilds if cache is empty.

    Parameters:
        new_title       (str)  — Title of the new project idea
        new_description (str)  — Description of the new project idea
        old_projects    (list) — List of project dicts from DB

    Returns:
        score       (float) — Highest similarity percentage (0 to 100)
        top_matches (list)  — Top 5 most similar projects with scores
    """

    # ── Step 1: Check if cache needs to be built ─────────────
    # Cache is empty on first run, or after admin changes the projects DB
    current_ids = [p["id"] for p in old_projects]  # IDs from current DB query

    if _cache_tfidf_matrix is None or _cache_project_ids != current_ids:
        # Cache is empty OR projects have changed — rebuild the matrix
        _build_cache(old_projects)  # This fills the global cache variables

    # ── Step 2: Transform the new idea using the cached vectorizer ──
    # We use transform() not fit_transform() — vectorizer is already fitted
    # This converts the new idea into a vector using the same vocabulary
    new_text   = new_title + " " + new_description  # Combine title + description
    new_vector = _cache_vectorizer.transform([new_text])  # Convert to TF-IDF vector

    # ── Step 3: Calculate cosine similarity ──────────────────
    # Compare new idea vector against all cached old project vectors
    # Result is an array of similarity scores between 0 and 1
    similarities = cosine_similarity(new_vector, _cache_tfidf_matrix)[0]

    # ── Step 4: Find top 5 most similar projects ─────────────
    # argsort gives indices sorted lowest to highest
    # [::-1] reverses to highest first, [:5] takes top 5
    top_indices = similarities.argsort()[::-1][:5]

    top_matches = []  # List to store the top matching projects
    for idx in top_indices:
        score_percent = round(float(similarities[idx]) * 100, 2)  # Convert 0-1 to percentage
        if score_percent > 0:  # Only include projects with actual similarity
            top_matches.append({
                "id"        : _cache_projects[idx]["id"],          # Project DB id
                "title"     : _cache_projects[idx]["title"],        # Project title
                "department": _cache_projects[idx]["department"],   # Department name
                "year"      : _cache_projects[idx]["year"],         # Year submitted
                "score"     : score_percent                         # Similarity percentage
            })

    # ── Step 5: Return the highest score + top matches list ──
    overall_score = top_matches[0]["score"] if top_matches else 0.0  # Highest match

    return overall_score, top_matches  # Return score and list of similar projects
