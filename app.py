# ============================================================
# app.py — Main Flask Application Entry Point
# Creates the Flask app, connects DB, registers blueprints
# Sprint 10 additions:
#   - CSRF protection via Flask-WTF (blocks fake form submissions)
#   - Rate limiter setup via Flask-Limiter (blocks spam/brute force)
#   - before_request hook redirects to /admin/setup if no admin exists
# ============================================================

from flask import Flask, redirect, url_for, request, render_template  # Core Flask imports
from flask_mysqldb import MySQL          # MySQL connector
from flask_wtf.csrf import CSRFProtect                 # CSRF protection
from flask_limiter import Limiter                      # Rate limiting
from flask_limiter.util import get_remote_address      # Get user IP for rate limiting
from config import Config                              # Our config class

# ── Initialize Flask app ─────────────────────────────────────
app = Flask(__name__)            # Create the Flask app instance
app.config.from_object(Config)  # Load settings from config.py

# ── Initialize MySQL ──────────────────────────────────────────
mysql = MySQL(app)          # Connect Flask to MySQL database

# ── Make mysql accessible from route files ───────────────────
# Routes import mysql using: from app import mysql
app.extensions['mysql'] = mysql

# ── Initialize CSRF Protection ───────────────────────────────
# CSRF = Cross-Site Request Forgery
# Without this, an attacker could trick a logged-in user into
# submitting a form to our site without their knowledge
# Flask-WTF adds a hidden token to every form and verifies it
csrf = CSRFProtect(app)  # Attach CSRF protection to the app

# ── Initialize Rate Limiter ───────────────────────────────────
# Rate limiting prevents:
#   - Brute force attacks on login (trying many passwords)
#   - Spam submissions on the check form
#   - Abuse of the NLP endpoint
# get_remote_address gets the user's IP to track request counts
limiter = Limiter(
    get_remote_address,          # Track limits per IP address
    app=app,                     # Attach to our Flask app
    default_limits=["200 per day", "50 per hour"],  # Global default limits
    storage_uri="memory://"      # Store counters in memory (simple, no Redis needed)
)

# ── Make limiter accessible from route files ─────────────────
# Routes import limiter using: from app import limiter
app.extensions['limiter'] = limiter

# ── Register Blueprints ───────────────────────────────────────
from routes.auth    import auth_bp     # /login, /register, /logout
from routes.student import student_bp  # /check, /result, /history
from routes.admin   import admin_bp    # /admin/dashboard, /admin/projects, etc.

app.register_blueprint(auth_bp)                        # Auth routes
app.register_blueprint(student_bp)                     # Student routes
app.register_blueprint(admin_bp, url_prefix="/admin")  # Admin routes (all prefixed /admin)

# ── Before Request Hook — Auto-redirect to setup ─────────────
# Runs before EVERY request
# If no admin exists in DB yet → redirect to /admin/setup
# This ensures the university sets their own admin credentials
@app.before_request
def check_setup():
    """
    Check before every request if the app has been set up.
    If no admin exists → redirect to /admin/setup automatically.
    Once admin exists, this check passes silently on every request.
    """

    # Allow static files through (CSS, JS, images must always load)
    if request.endpoint == "static":
        return None

    # Allow the setup page itself (avoid infinite redirect loop)
    if request.endpoint == "admin.setup":
        return None

    # Check DB for any existing admin user
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        admin = cur.fetchone()  # None if no admin exists yet
        cur.close()

        if not admin:
            # No admin found — redirect to first-time setup
            return redirect(url_for("admin.setup"))

    except Exception:
        # DB not ready yet (e.g. Docker first boot) — allow request through
        pass

    return None  # Admin exists — proceed normally



# ── Error Handlers ────────────────────────────────────────────
# These catch HTTP errors and show a friendly page instead of
# a blank browser error or technical stack trace

@app.errorhandler(404)
def page_not_found(e):
    """Show custom 404 page when a route is not found."""
    return render_template("404.html"), 404  # Return 404 status code

@app.errorhandler(500)
def internal_error(e):
    """Show custom 500 page when an unexpected server error occurs."""
    return render_template("500.html"), 500  # Return 500 status code

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Show friendly message when user hits the rate limit."""
    from flask import flash, redirect, url_for, request as req
    flash("Too many requests. Please wait a moment and try again.", "error")
    # Redirect back to the same page the user was on
    return redirect(req.referrer or url_for("student.index"))

# ── Start development server ──────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
