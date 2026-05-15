# ============================================================
# config.py
# Central configuration file for the Flask application
# All settings are loaded from the .env file
# Sprint 10 additions:
#   - WTF_CSRF_ENABLED — enables CSRF protection on all forms
#   - WTF_CSRF_TIME_LIMIT — CSRF token expires after 1 hour
# ============================================================

import os                        # Access environment variables
from dotenv import load_dotenv   # Load variables from .env file

load_dotenv()  # Read .env file and load all variables into os.environ

class Config:
    # Secret key — signs session cookies AND CSRF tokens
    # Must be random and secret — never commit the real value to GitHub
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_dev_key_change_this")

    # MySQL connection settings
    MYSQL_HOST      = os.getenv("MYSQL_HOST", "localhost")   # DB server address
    MYSQL_USER      = os.getenv("MYSQL_USER", "root")        # DB username
    MYSQL_PASSWORD  = os.getenv("MYSQL_PASSWORD", "")        # DB password
    MYSQL_DB        = os.getenv("MYSQL_DB", "similarity_checker")  # DB name
    MYSQL_CURSORCLASS = "DictCursor"  # Return query results as dicts not tuples

    # CSRF Protection settings (Flask-WTF)
    WTF_CSRF_ENABLED    = True   # Enable CSRF protection on all POST forms
    WTF_CSRF_TIME_LIMIT = 3600   # CSRF token expires after 1 hour (3600 seconds)
