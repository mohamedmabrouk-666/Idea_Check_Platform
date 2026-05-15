
# ============================================================
# models/user.py
# User Model — helper functions for user database operations
# General idea: instead of writing raw SQL in every route,
# we put all user-related DB queries here in one place
# This keeps routes clean and makes code reusable
# ============================================================

class User:
    """
    Represents a user in the system.
    Roles: 'student' (default) or 'admin'
    Used by: routes/auth.py
    """

    def __init__(self, db):
        self.db = db  # MySQL connection passed from the Flask app

    def find_by_email(self, email):
        """
        Find a user by their email address.
        Used during login to verify credentials.
        Returns: dict with user data, or None if not found
        """
        cur = self.db.connection.cursor()  # Open DB cursor
        cur.execute(
            "SELECT * FROM users WHERE email = %s",  # Parameterized — safe from SQL injection
            (email,)
        )
        user = cur.fetchone()  # Returns dict (DictCursor) or None
        cur.close()            # Always close cursor after use
        return user

    def find_by_id(self, user_id):
        """
        Find a user by their ID.
        Used to load user info from session data.
        Returns: dict with user data, or None if not found
        """
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return user

    def create(self, name, email, hashed_password, role="student"):
        """
        Insert a new user into the database.
        Called during registration.
        Password must already be hashed before calling this.
        Returns: ID of the newly created user
        """
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)  # All values safely parameterized
        )
        self.db.connection.commit()  # Save changes to database
        new_id = cur.lastrowid       # Get the auto-generated ID
        cur.close()
        return new_id

    def email_exists(self, email):
        """
        Check if an email is already registered.
        Used during registration to prevent duplicate accounts.
        Returns: True if email exists, False otherwise
        """
        cur = self.db.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cur.fetchone()  # None if not found
        cur.close()
        return result is not None  # Convert to boolean
