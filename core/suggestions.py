# ============================================================
# core/suggestions.py
# Suggestion Engine — Tells the student what to do based on score
# General idea: after we know the similarity percentage,
# we generate helpful advice to guide the student
# ============================================================

def get_suggestion(score, top_matches):
    """
    Generate a suggestion message and status based on the similarity score.
    
    Parameters:
        score       (float) — Similarity percentage (0 to 100)
        top_matches (list)  — List of the most similar old projects
    
    Returns:
        dict with keys:
            status  (str) — "danger", "warning", or "success"
            title   (str) — Short headline for the result
            message (str) — Detailed advice for the student
            tips    (list) — Specific actionable improvement tips
    """

    # ── HIGH similarity (above 70%) — Idea is too similar ───
    # The idea is very close to an existing project, needs major changes
    if score >= 70:
        return {
            "status" : "danger",   # Red color in the UI
            "title"  : "High Similarity Detected — Idea Needs Major Changes",
            "message": (
                "Your project idea is very similar to existing graduation projects. "
                "To make your idea unique, you need to change the core concept or "
                "add a significantly different approach."
            ),
            "tips": [
                "Change the main application domain (e.g., if it's for hospitals, try applying it to schools)",
                "Add a new technology layer not present in similar projects (e.g., add AI/ML to a basic system)",
                "Combine two different ideas into one novel concept",
                "Focus on a more specific problem that the similar projects don't address",
                f"The most similar project is: '{top_matches[0]['title']}' — make sure yours is clearly different"
            ]
        }

    # ── MEDIUM similarity (40% to 70%) — Some overlap, needs refinement
    # The idea shares some themes but could be differentiated
    elif score >= 40:
        return {
            "status" : "warning",  # Yellow/orange color in the UI
            "title"  : "Moderate Similarity — Consider Refining Your Idea",
            "message": (
                "Your project has some overlap with existing projects, but there is "
                "enough difference to make it work. Focus on clearly defining what "
                "makes your approach unique."
            ),
            "tips": [
                "Clearly define your unique contribution in the description",
                "Add specific features that the similar projects don't have",
                "Mention a specific technology or method that makes your approach different",
                "Be more specific about the problem you are solving",
                "Consider adding a unique dataset, location, or target user group"
            ]
        }

    # ── LOW similarity (below 40%) — Idea is original ───────
    # Great! The idea is new and not covered by existing projects
    else:
        return {
            "status" : "success",  # Green color in the UI
            "title"  : "Great! Your Idea Appears to be Original",
            "message": (
                "Your project idea shows low similarity to existing projects. "
                "This is a good sign! Make sure your description clearly explains "
                "the technical approach and expected outcomes."
            ),
            "tips": [
                "Make sure your description explains the technical implementation clearly",
                "Define the tools and technologies you plan to use",
                "Describe the expected results and how you will measure success",
                "Consider adding keywords that describe your project's domain"
            ]
        }
