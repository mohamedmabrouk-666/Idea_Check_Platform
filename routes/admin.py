
# ============================================================
# routes/admin.py
# Admin Routes — Dashboard, Manage Old Projects, Setup, Edit
# General idea: only admins can access these routes
# Admins can: view stats, add/edit/delete old projects
# All routes are prefixed with /admin (set in app.py)
#
# Sprint 8 — /admin/setup:
#   Shows a first-time setup form ONLY if no admin exists in DB
#   After the first admin registers, this page locks forever
#   This way the university sets their own credentials
#
# Sprint 9 — /admin/projects/edit/<id>:
#   Admin can edit any old project's data from the app directly
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt                              # For hashing the setup admin password securely
from core.similarity import clear_cache   # Clear TF-IDF cache when projects DB changes
import os      # For reading SETUP_CODE from .env environment variable

admin_bp = Blueprint("admin", __name__)  # Create admin blueprint

def get_mysql():
    """Get MySQL instance — imported here to avoid circular imports."""
    from app import mysql
    return mysql

def admin_required(f):
    """
    Decorator to protect admin routes.
    Checks that user is logged in AND has role = 'admin'
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:            # Not logged in at all
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "admin": # Logged in but not admin
            flash("Access denied. Admin only.", "error")
            return redirect(url_for("student.check"))
        return f(*args, **kwargs)
    return decorated

def admin_exists():
    """
    Check if any admin user already exists in the database.
    Used by the setup route to decide whether to allow access.
    Returns: True if at least one admin exists, False otherwise
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")  # Check for any admin
    result = cur.fetchone()  # None if no admin exists
    cur.close()
    return result is not None  # True = admin exists, False = no admin yet


# ================================================================
# SPRINT 8 — SETUP ROUTE
# ================================================================

# ── SETUP PAGE ────────────────────────────────────────────────
@admin_bp.route("/setup", methods=["GET", "POST"])
def setup():
    """
    First-time setup page — creates the first admin account.

    GET:
      - If NO admin exists → show the setup form
      - If admin EXISTS   → redirect to login (page is locked)

    POST:
      - Validate the setup inputs
      - Verify the setup secret code (prevents random people from creating admin)
      - Hash the password and save the admin to DB
      - After success → redirect to login
      - Page is now locked forever (admin exists in DB)

    General idea: like WordPress first-time setup —
    you open the site, it asks you to create an admin,
    after that the setup page is gone forever.
    """

    # ── Check if setup is already done ──────────────────────
    # If any admin exists in DB, this page is permanently locked
    if admin_exists():
        flash("Setup already completed. Please log in.", "info")
        return redirect(url_for("auth.login"))  # Send away — setup is done

    # ── Handle form submission ───────────────────────────────
    if request.method == "POST":
        name         = request.form.get("name", "").strip()          # Admin full name
        email        = request.form.get("email", "").strip()         # Admin email
        password     = request.form.get("password", "").strip()      # Admin password
        confirm_pw   = request.form.get("confirm_password", "").strip()  # Confirm password
        setup_code   = request.form.get("setup_code", "").strip()    # Secret setup code

        # ── Validate all fields are filled ──────────────────
        if not all([name, email, password, confirm_pw, setup_code]):
            flash("All fields are required.", "error")
            return render_template("admin/setup.html")

        # ── Validate password length ─────────────────────────
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("admin/setup.html")

        # ── Validate passwords match ─────────────────────────
        if password != confirm_pw:
            flash("Passwords do not match.", "error")
            return render_template("admin/setup.html")

        # ── Validate setup secret code ───────────────────────
        # This code prevents any random visitor from creating an admin
        # Change "ENG-SETUP-2024" to whatever code you want to give the university
        if setup_code != os.getenv("SETUP_CODE", "ENG-SETUP-2024"):  # Read code from .env
            flash("Invalid setup code. Please contact the developer.", "error")
            return render_template("admin/setup.html")

        mysql = get_mysql()
        cur = mysql.connection.cursor()

        # ── Double-check no admin was created between GET and POST
        cur.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        if cur.fetchone():
            cur.close()
            flash("Setup already completed.", "info")
            return redirect(url_for("auth.login"))

        # ── Hash the password before saving ──────────────────
        # bcrypt.hashpw converts plain password → secure irreversible hash
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))

        # ── Save the new admin to the database ───────────────
        cur.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_pw.decode("utf-8"), "admin")  # role = admin
        )
        mysql.connection.commit()  # Persist to database
        cur.close()

        # ── Success — redirect to login ───────────────────────
        flash("Setup complete! You can now log in with your admin account.", "success")
        return redirect(url_for("auth.login"))

    # ── Show setup form on GET ───────────────────────────────
    return render_template("admin/setup.html")


# ================================================================
# EXISTING ROUTES (unchanged)
# ================================================================

# ── DASHBOARD ────────────────────────────────────────────────
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """
    Show admin dashboard with statistics:
    - Total old projects in the database
    - Total student submissions
    - Average similarity score
    - Submissions per department
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Count total old projects in the database
    cur.execute("SELECT COUNT(*) as total FROM old_projects")
    total_projects = cur.fetchone()["total"]

    # Count total student submissions ever
    cur.execute("SELECT COUNT(*) as total FROM submissions")
    total_submissions = cur.fetchone()["total"]

    # Calculate the average similarity score across all submissions
    cur.execute("SELECT AVG(similarity_score) as avg_score FROM submissions")
    avg_score_result = cur.fetchone()["avg_score"]
    avg_score = round(avg_score_result, 1) if avg_score_result else 0

    # Count submissions grouped by department (for chart)
    cur.execute(
        """SELECT department, COUNT(*) as count
           FROM submissions GROUP BY department ORDER BY count DESC"""
    )
    dept_stats = cur.fetchall()

    # Get the 5 most recent submissions
    cur.execute(
        """SELECT s.title, s.similarity_score, s.created_at, u.name as student_name
           FROM submissions s JOIN users u ON s.user_id = u.id
           ORDER BY s.created_at DESC LIMIT 5"""
    )
    recent_submissions = cur.fetchall()
    cur.close()

    return render_template(
        "admin/dashboard.html",
        total_projects     = total_projects,
        total_submissions  = total_submissions,
        avg_score          = avg_score,
        dept_stats         = dept_stats,
        recent_submissions = recent_submissions
    )


# ── LIST ALL PROJECTS ─────────────────────────────────────────
@admin_bp.route("/projects")
@admin_required
def projects():
    """Show all old projects with search and filter options."""
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    search     = request.args.get("search", "")
    department = request.args.get("department", "")

    # Build query with optional filters
    query  = "SELECT * FROM old_projects WHERE 1=1"
    params = []

    if search:
        query  += " AND (title LIKE %s OR description LIKE %s)"
        params += [f"%{search}%", f"%{search}%"]

    if department:
        query  += " AND department = %s"
        params.append(department)

    query += " ORDER BY year DESC, id DESC"

    cur.execute(query, params)
    all_projects = cur.fetchall()

    # Get distinct departments for the filter dropdown
    cur.execute("SELECT DISTINCT department FROM old_projects ORDER BY department")
    departments = [row["department"] for row in cur.fetchall()]
    cur.close()

    return render_template(
        "admin/projects.html",
        projects      = all_projects,
        departments   = departments,
        search        = search,
        selected_dept = department
    )


# ── ADD PROJECT ───────────────────────────────────────────────
@admin_bp.route("/projects/add", methods=["POST"])
@admin_required
def add_project():
    """Add a new old project to the database via form submission."""
    title       = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    department  = request.form.get("department", "").strip()
    year        = request.form.get("year", "").strip()
    keywords    = request.form.get("keywords", "").strip()

    if not title or not description:
        flash("Title and description are required.", "error")
        return redirect(url_for("admin.projects"))

    mysql = get_mysql()
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO old_projects (title, description, department, year, keywords) VALUES (%s, %s, %s, %s, %s)",
        (title, description, department, year or None, keywords)
    )
    mysql.connection.commit()
    cur.close()

    clear_cache()  # Clear TF-IDF cache — new project must be included in next similarity check
    flash("Project added successfully.", "success")
    return redirect(url_for("admin.projects"))


# ================================================================
# SPRINT 9 — EDIT PROJECT ROUTE
# ================================================================

# ── EDIT PROJECT ──────────────────────────────────────────────
@admin_bp.route("/projects/edit/<int:project_id>", methods=["GET", "POST"])
@admin_required
def edit_project(project_id):
    """
    Edit an existing old project.

    GET:
      - Load the project data from DB
      - Show a pre-filled edit form

    POST:
      - Validate the new data
      - Update the record in DB
      - Redirect back to projects list

    General idea: instead of delete + re-add,
    admin can directly fix a typo or update a description
    without losing the project's ID or history.
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    if request.method == "POST":
        # ── Get updated values from the form ─────────────────
        title       = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        department  = request.form.get("department", "").strip()
        year        = request.form.get("year", "").strip()
        keywords    = request.form.get("keywords", "").strip()

        # ── Validate required fields ──────────────────────────
        if not title or not description:
            flash("Title and description are required.", "error")
            return redirect(url_for("admin.edit_project", project_id=project_id))

        # ── Update the project in the database ───────────────
        cur.execute(
            """UPDATE old_projects
               SET title = %s, description = %s, department = %s,
                   year = %s, keywords = %s
               WHERE id = %s""",
            (title, description, department, year or None, keywords, project_id)
        )
        mysql.connection.commit()  # Save changes
        cur.close()

        clear_cache()  # Clear TF-IDF cache — updated project text must be re-vectorized
        flash("Project updated successfully.", "success")
        return redirect(url_for("admin.projects"))  # Go back to projects list

    # ── Load existing project data for the form ───────────────
    cur.execute("SELECT * FROM old_projects WHERE id = %s", (project_id,))
    project = cur.fetchone()  # Get current project data
    cur.close()

    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("admin.projects"))

    return render_template("admin/edit_project.html", project=project)


# ── DELETE PROJECT ────────────────────────────────────────────
@admin_bp.route("/projects/delete/<int:project_id>", methods=["POST"])
@admin_required
def delete_project(project_id):
    """Delete an old project from the database by its ID."""
    mysql = get_mysql()
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM old_projects WHERE id = %s", (project_id,))
    mysql.connection.commit()
    cur.close()

    clear_cache()  # Clear TF-IDF cache — deleted project must be removed from comparisons
    flash("Project deleted successfully.", "success")
    return redirect(url_for("admin.projects"))
