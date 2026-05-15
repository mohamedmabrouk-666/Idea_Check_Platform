
# ============================================================
# models/submission.py
# Submission Model — helper functions for submissions table
# General idea: every time a student checks an idea, it gets
# saved as a submission. This model handles all DB operations
# related to submissions — saving, loading, stats.
# Used by: routes/student.py, routes/admin.py
# ============================================================

import json  # For encoding/decoding top_matches as JSON string in DB

class Submission:
    """
    Represents a student's idea submission.
    Stores: the idea text, similarity score, and top matching projects.
    """

    def __init__(self, db):
        self.db = db  # MySQL connection passed from Flask app

    def create(self, user_id, title, description, department, score, top_matches):
        """
        Save a new submission to the database after NLP analysis.
        Parameters:
            user_id     (int)   — ID of the student who submitted
            title       (str)   — Project title
            description (str)   — Project description
            department  (str)   — Student's department
            score       (float) — Similarity percentage from NLP engine
            top_matches (list)  — Top 5 similar projects as a list of dicts
        Returns: ID of the newly created submission
        """
        cur = self.db.connection.cursor()
        cur.execute(
            """INSERT INTO submissions
               (user_id, title, description, department, similarity_score, top_matches)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                user_id,
                title,
                description,
                department,
                score,
                json.dumps(top_matches)  # Store list as JSON string in TEXT column
            )
        )
        self.db.connection.commit()  # Save to database
        new_id = cur.lastrowid       # Get auto-generated submission ID
        cur.close()
        return new_id

    def find_by_id(self, submission_id, user_id):
        """
        Find a specific submission by ID, scoped to a specific user.
        The user_id check ensures students can only view their own results.
        Returns: submission dict with parsed top_matches, or None
        """
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT * FROM submissions WHERE id = %s AND user_id = %s",
            (submission_id, user_id)  # Both conditions must match — security check
        )
        submission = cur.fetchone()
        cur.close()

        if submission and submission.get("top_matches"):
            # Parse the JSON string back into a Python list
            submission["top_matches"] = json.loads(submission["top_matches"])

        return submission

    def get_by_user(self, user_id):
        """
        Get all submissions for a specific student, newest first.
        Used for the student history page.
        Returns: list of submission dicts (without top_matches for performance)
        """
        cur = self.db.connection.cursor()
        cur.execute(
            """SELECT id, title, department, similarity_score, created_at
               FROM submissions
               WHERE user_id = %s
               ORDER BY created_at DESC""",  # Newest submission shown first
            (user_id,)
        )
        submissions = cur.fetchall()
        cur.close()
        return submissions

    def count_all(self):
        """
        Count total submissions across all students.
        Used by admin dashboard stats card.
        Returns: integer count
        """
        cur = self.db.connection.cursor()
        cur.execute("SELECT COUNT(*) as total FROM submissions")
        result = cur.fetchone()
        cur.close()
        return result["total"] if result else 0

    def get_average_score(self):
        """
        Calculate the average similarity score across all submissions.
        Used by admin dashboard to show platform-wide average.
        Returns: float rounded to 1 decimal, or 0 if no submissions
        """
        cur = self.db.connection.cursor()
        cur.execute("SELECT AVG(similarity_score) as avg FROM submissions")
        result = cur.fetchone()
        cur.close()
        avg = result["avg"] if result and result["avg"] else 0
        return round(float(avg), 1)  # Round to 1 decimal place

    def get_recent(self, limit=5):
        """
        Get the most recent submissions with student names.
        Used by admin dashboard recent activity table.
        Parameters:
            limit (int) — how many recent submissions to return (default 5)
        Returns: list of dicts with student name + submission data
        """
        cur = self.db.connection.cursor()
        cur.execute(
            """SELECT s.id, s.title, s.similarity_score, s.created_at,
                      u.name as student_name
               FROM submissions s
               JOIN users u ON s.user_id = u.id
               ORDER BY s.created_at DESC
               LIMIT %s""",
            (limit,)  # Parameterized limit
        )
        submissions = cur.fetchall()
        cur.close()
        return submissions

    def get_dept_stats(self):
        """
        Count submissions grouped by department.
        Used by admin dashboard department bar chart.
        Returns: list of dicts [{department, count}, ...] sorted by count desc
        """
        cur = self.db.connection.cursor()
        cur.execute(
            """SELECT department, COUNT(*) as count
               FROM submissions
               WHERE department IS NOT NULL
               GROUP BY department
               ORDER BY count DESC"""
        )
        stats = cur.fetchall()
        cur.close()
        return stats
