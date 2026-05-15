
# ============================================================
# models/project.py
# OldProject Model — helper functions for old_projects table
# General idea: all DB queries related to the old projects
# database are kept here — used by routes/admin.py and
# routes/student.py (to load projects for NLP comparison)
# ============================================================

class OldProject:
    """
    Represents an old graduation project in the database.
    These are the projects that new ideas are compared against.
    Used by: routes/admin.py, core/similarity.py
    """

    def __init__(self, db):
        self.db = db  # MySQL connection passed from Flask app

    def get_all(self):
        """
        Get all old projects from the database.
        Used by similarity.py to load the full comparison dataset.
        Returns: list of dicts [{id, title, description, department, year, keywords}, ...]
        """
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT id, title, description, department, year, keywords FROM old_projects"
            " ORDER BY year DESC"  # Newest projects first
        )
        projects = cur.fetchall()  # Fetch all rows as list of dicts
        cur.close()
        return projects

    def get_filtered(self, search="", department=""):
        """
        Get projects with optional search and department filter.
        Used by admin projects page to display filtered results.
        Parameters:
            search     (str) — keyword to search in title or description
            department (str) — filter by exact department name
        Returns: list of matching project dicts
        """
        cur = self.db.connection.cursor()

        # Build query dynamically based on which filters are provided
        query  = "SELECT * FROM old_projects WHERE 1=1"  # 1=1 allows clean AND additions
        params = []  # Collect params for safe parameterized execution

        if search:
            query  += " AND (title LIKE %s OR description LIKE %s)"
            params += [f"%{search}%", f"%{search}%"]  # % is SQL wildcard for LIKE

        if department:
            query  += " AND department = %s"
            params.append(department)

        query += " ORDER BY year DESC, id DESC"  # Sort by newest first

        cur.execute(query, params)
        projects = cur.fetchall()
        cur.close()
        return projects

    def create(self, title, description, department, year, keywords):
        """
        Insert a new old project into the database.
        Called by admin when adding projects manually.
        Returns: ID of the newly inserted project
        """
        cur = self.db.connection.cursor()
        cur.execute(
            """INSERT INTO old_projects (title, description, department, year, keywords)
               VALUES (%s, %s, %s, %s, %s)""",
            (title, description, department, year or None, keywords)  # None if year is empty
        )
        self.db.connection.commit()  # Persist changes
        new_id = cur.lastrowid
        cur.close()
        return new_id

    def delete(self, project_id):
        """
        Delete an old project by its ID.
        Called by admin from the projects management page.
        """
        cur = self.db.connection.cursor()
        cur.execute(
            "DELETE FROM old_projects WHERE id = %s",  # Safe parameterized delete
            (project_id,)
        )
        self.db.connection.commit()  # Save changes
        cur.close()

    def count(self):
        """
        Count total number of old projects in the database.
        Used by admin dashboard stats card.
        Returns: integer count
        """
        cur = self.db.connection.cursor()
        cur.execute("SELECT COUNT(*) as total FROM old_projects")
        result = cur.fetchone()
        cur.close()
        return result["total"] if result else 0

    def get_departments(self):
        """
        Get list of unique department names from old_projects.
        Used to populate dropdown filters in admin and student forms.
        Returns: list of department name strings
        """
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT DISTINCT department FROM old_projects"
            " WHERE department IS NOT NULL ORDER BY department"
        )
        rows = cur.fetchall()
        cur.close()
        return [row["department"] for row in rows]  # Extract just the name strings
