
# ============================================================
# routes/student.py
# Student Routes — Check Idea, View Results, View History
# Sprint 10 additions:
#   - Rate limiting on /check (3 per minute — NLP is expensive)
#   - Input sanitization before saving to DB
# General flow:
#   /check → submit idea → NLP runs → /result → /history
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
import json                                            # For storing top_matches as JSON
from core.similarity  import calculate_similarity      # NLP engine
from core.suggestions   import get_suggestion            # Suggestion generator
from core.pdf_generator import generate_pdf              # PDF report generator

student_bp = Blueprint("student", __name__)  # Create student blueprint

def get_mysql():
    """Get MySQL instance — avoid circular imports."""
    from app import mysql
    return mysql

def get_limiter():
    """Get rate limiter instance from app."""
    from app import limiter
    return limiter

def login_required(f):
    """Decorator — redirects to login if user is not logged in."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:  # No session = not logged in
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

def sanitize(text):
    """
    Basic input sanitization — removes leading/trailing whitespace
    and limits length to prevent excessively large inputs.
    Called on all user text inputs before saving to DB.
    """
    if not text:
        return ""
    return text.strip()[:5000]  # Max 5000 characters per field


# ── INDEX / HOME ──────────────────────────────────────────────
@student_bp.route("/")
def index():
    """Landing page — shown to all visitors."""
    return render_template("index.html")


# ── CHECK IDEA ────────────────────────────────────────────────
@student_bp.route("/check", methods=["GET", "POST"])
@login_required
def check():
    """
    GET  → Show the idea submission form
    POST → Validate inputs, run NLP, save result, redirect to result page
    Rate limit: 5 per minute per IP (NLP processing is resource-intensive)
    """
    # Apply rate limit — max 5 submissions per minute per IP
    get_limiter().limit("5 per minute")(lambda: None)()

    if request.method == "POST":
        # Get and sanitize all form inputs
        title       = sanitize(request.form.get("title", ""))        # Project title
        description = sanitize(request.form.get("description", ""))  # Project description
        department  = sanitize(request.form.get("department", ""))   # Department

        # Count words for validation
        title_words = len(title.split())        # Number of words in title
        desc_words  = len(description.split())  # Number of words in description

        # Validate title word count (5 to 15 words)
        if title_words < 5:
            flash("Title is too short. Please write at least 5 words.", "error")
            return render_template("student/check.html")

        # Validate description word count (50 to 300 words)
        if desc_words < 50:
            flash("Description is too short. Please write at least 50 words.", "error")
            return render_template("student/check.html")

        if desc_words > 300:
            flash("Description is too long. Please keep it under 300 words.", "error")
            return render_template("student/check.html")

        mysql = get_mysql()
        cur = mysql.connection.cursor()

        # Load all old projects from DB for NLP comparison
        cur.execute("SELECT id, title, description, department, year FROM old_projects")
        old_projects = cur.fetchall()  # List of dicts

        if not old_projects:
            flash("No projects in database yet. Please contact admin.", "warning")
            cur.close()
            return render_template("student/check.html")

        # Run NLP similarity engine — TF-IDF + cosine similarity
        score, top_matches = calculate_similarity(title, description, old_projects)

        # Generate suggestion advice based on the score
        suggestion = get_suggestion(score, top_matches)

        # Save submission to database
        cur.execute(
            """INSERT INTO submissions
               (user_id, title, description, department, similarity_score, top_matches)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                session["user_id"],      # Current logged-in student
                title,
                description,
                department,
                score,
                json.dumps(top_matches)  # Store list as JSON string
            )
        )
        mysql.connection.commit()     # Save to database
        submission_id = cur.lastrowid # Get auto-generated submission ID
        cur.close()

        # Redirect to result page with the new submission ID
        return redirect(url_for("student.result", submission_id=submission_id))

    return render_template("student/check.html")


# ── VIEW RESULT ───────────────────────────────────────────────
@student_bp.route("/result/<int:submission_id>")
@login_required
def result(submission_id):
    """
    Show the similarity result for a specific submission.
    Only the owner (student who submitted) can view their result.
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Load submission — user_id check ensures student sees only their own results
    cur.execute(
        "SELECT * FROM submissions WHERE id = %s AND user_id = %s",
        (submission_id, session["user_id"])  # Security: scope to current user
    )
    submission = cur.fetchone()
    cur.close()

    if not submission:
        flash("Submission not found.", "error")
        return redirect(url_for("student.check"))

    # Parse stored JSON string back into Python list
    top_matches = json.loads(submission["top_matches"]) if submission["top_matches"] else []
    score       = submission["similarity_score"]

    # Get suggestion advice for this score
    suggestion = get_suggestion(score, top_matches)

    return render_template(
        "student/result.html",
        submission  = submission,
        top_matches = top_matches,
        score       = score,
        suggestion  = suggestion
    )


# ── VIEW HISTORY ──────────────────────────────────────────────
@student_bp.route("/history")
@login_required
def history():
    """Show all past submissions for the currently logged-in student."""
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Load all submissions for this student, newest first
    cur.execute(
        """SELECT id, title, department, similarity_score, created_at
           FROM submissions WHERE user_id = %s
           ORDER BY created_at DESC""",
        (session["user_id"],)  # Only this student's submissions
    )
    submissions = cur.fetchall()
    cur.close()

    return render_template("student/history.html", submissions=submissions)


# ── DOWNLOAD PDF ──────────────────────────────────────────────
@student_bp.route("/result/<int:submission_id>/pdf")
@login_required
def download_pdf(submission_id):
    """
    Generate and download a PDF report for a specific submission.
    Only the owner of the submission can download their PDF.
    The PDF is generated in memory — no file is saved on the server.
    Uses: core/pdf_generator.py to build the PDF content.
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Load the submission — user_id check ensures student owns this submission
    cur.execute(
        "SELECT * FROM submissions WHERE id = %s AND user_id = %s",
        (submission_id, session["user_id"])  # Security: scope to current user only
    )
    submission = cur.fetchone()  # Returns dict or None

    if not submission:
        flash("Submission not found.", "error")
        cur.close()
        return redirect(url_for("student.check"))

    # Parse the stored JSON top_matches back into a Python list
    top_matches = json.loads(submission["top_matches"]) if submission["top_matches"] else []
    score       = submission["similarity_score"]  # Similarity percentage

    # Get suggestion advice for this score
    suggestion = get_suggestion(score, top_matches)

    cur.close()

    # Generate the PDF in memory using reportlab
    pdf_buffer = generate_pdf(
        submission   = submission,           # Submission data dict
        top_matches  = top_matches,          # List of similar projects
        suggestion   = suggestion,           # Advice dict
        student_name = session["user_name"]  # Student name from session
    )

    # Build a clean filename for the downloaded file
    # Replace spaces with underscores for a valid filename
    safe_title = submission["title"][:30].replace(" ", "_")  # First 30 chars of title
    filename   = f"IdeaCheck_Report_{safe_title}.pdf"        # e.g. IdeaCheck_Report_Smart_Home.pdf

    # Send the in-memory PDF as a file download response
    return send_file(
        pdf_buffer,                           # In-memory buffer containing PDF bytes
        mimetype     = "application/pdf",     # Tell browser this is a PDF file
        as_attachment = True,                 # Force download instead of opening in browser
        download_name = filename              # Filename shown in browser download dialog
    )
