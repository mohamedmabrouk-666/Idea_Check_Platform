
# ============================================================
# routes/auth.py
# Authentication Routes — Register, Login, Logout
# Sprint 10 additions:
#   - Rate limiting on /login (5 attempts per minute per IP)
#   - Rate limiting on /register (3 attempts per minute per IP)
#   - This prevents brute force password attacks
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt  # Password hashing library

auth_bp = Blueprint("auth", __name__)  # Create auth blueprint

def get_mysql():
    """Get MySQL instance — avoid circular imports by importing inside function."""
    from app import mysql
    return mysql

def get_limiter():
    """Get the rate limiter instance from app extensions."""
    from app import limiter
    return limiter


# ── REGISTER ──────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    GET  → Show the registration form
    POST → Validate inputs, hash password, save user to DB
    Rate limit: 3 requests per minute per IP (prevents spam accounts)
    """
    # Apply rate limit — max 3 register attempts per minute per IP
    get_limiter().limit("3 per minute")(lambda: None)()

    if request.method == "POST":
        name     = request.form.get("name", "").strip()      # Full name from form
        email    = request.form.get("email", "").strip()     # Email from form
        password = request.form.get("password", "").strip()  # Password from form

        # Validate all fields are filled
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        # Validate password length
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth/register.html")

        mysql = get_mysql()
        cur = mysql.connection.cursor()

        # Check if email already exists in DB
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))  # Safe parameterized query
        if cur.fetchone():
            flash("Email already registered. Please log in.", "error")
            cur.close()
            return render_template("auth/register.html")

        # Hash password before saving — never store plain text passwords
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Insert new user into database
        cur.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_pw.decode("utf-8"), "student")  # Default role = student
        )
        mysql.connection.commit()  # Save to database
        cur.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ── LOGIN ──────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → Show the login form
    POST → Verify credentials, create session if correct
    Rate limit: 5 attempts per minute per IP (prevents brute force)
    """
    # Apply rate limit — max 5 login attempts per minute per IP
    get_limiter().limit("5 per minute")(lambda: None)()

    if request.method == "POST":
        email    = request.form.get("email", "").strip()     # Email from form
        password = request.form.get("password", "").strip()  # Password from form

        if not email or not password:
            flash("Please fill in all fields.", "error")
            return render_template("auth/login.html")

        mysql = get_mysql()
        cur = mysql.connection.cursor()

        # Find user by email in database
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))  # Safe parameterized
        user = cur.fetchone()  # Returns dict or None
        cur.close()

        # Verify password using bcrypt — compares input with stored hash
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            session["user_id"]   = user["id"]    # Store user ID in session cookie
            session["user_name"] = user["name"]  # Store name for navbar display
            session["user_role"] = user["role"]  # Store role for access control

            # Redirect based on role — admin goes to dashboard, student to check
            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("student.check"))

        # Wrong credentials — show generic error (don't reveal which field is wrong)
        flash("Invalid email or password.", "error")
        return render_template("auth/login.html")

    return render_template("auth/login.html")


# ── LOGOUT ─────────────────────────────────────────────────────
@auth_bp.route("/logout")
def logout():
    """Clear session data and redirect to login page."""
    session.clear()  # Remove all session variables (user_id, user_name, user_role)
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
