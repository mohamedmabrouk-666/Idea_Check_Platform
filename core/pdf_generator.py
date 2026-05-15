# ============================================================
# core/pdf_generator.py
# PDF Report Generator — Sprint 12
# General idea: after a student checks their idea and sees
# the result, they can download a professional PDF report
# that contains: their idea details, similarity score,
# top matching projects, and improvement suggestions.
# Uses reportlab library to build the PDF from scratch.
# ============================================================

from reportlab.lib.pagesizes   import A4                        # Standard A4 page size
from reportlab.lib             import colors                     # Color definitions
from reportlab.lib.styles      import getSampleStyleSheet, ParagraphStyle  # Text styles
from reportlab.lib.units       import cm                         # Centimeter unit for margins
from reportlab.platypus        import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable  # PDF building blocks
from reportlab.lib.enums       import TA_CENTER, TA_LEFT         # Text alignment options
from io                        import BytesIO                    # In-memory byte stream (no file saved to disk)
import datetime                                                  # For the report date

# ── Color palette — matches the web app theme ─────────────────
COLOR_NAVY   = colors.HexColor("#1a2332")   # Deep navy — headers
COLOR_STEEL  = colors.HexColor("#2c4a6e")   # Steel blue — subheaders
COLOR_ACCENT = colors.HexColor("#3d7ebf")   # Medium blue — accents
COLOR_SUCCESS = colors.HexColor("#27ae60")  # Green — low similarity
COLOR_WARNING = colors.HexColor("#e67e22")  # Orange — medium similarity
COLOR_DANGER  = colors.HexColor("#c0392b")  # Red — high similarity
COLOR_LIGHT   = colors.HexColor("#e8f0f7")  # Light blue — table backgrounds
COLOR_GRAY    = colors.HexColor("#6b7c93")  # Gray — secondary text
COLOR_WHITE   = colors.white                # White

def get_score_color(score):
    """
    Return the appropriate color based on similarity score.
    Mirrors the web app color logic for consistency.
    """
    if score >= 70:
        return COLOR_DANGER   # Red — high similarity (bad)
    elif score >= 40:
        return COLOR_WARNING  # Orange — medium similarity
    else:
        return COLOR_SUCCESS  # Green — low similarity (good)

def generate_pdf(submission, top_matches, suggestion, student_name):
    """
    Generate a PDF report for a student's similarity check result.

    Parameters:
        submission   (dict) — submission data from DB (title, description, dept, score, date)
        top_matches  (list) — top 5 similar projects [{title, department, year, score}]
        suggestion   (dict) — suggestion dict {status, title, message, tips}
        student_name (str)  — name of the student who submitted

    Returns:
        BytesIO object — in-memory PDF file ready to send as HTTP response
        No file is saved to disk — everything stays in memory
    """

    # ── Create in-memory buffer to hold PDF bytes ─────────────
    buffer = BytesIO()  # PDF will be written here instead of a file

    # ── Setup document with A4 size and margins ───────────────
    doc = SimpleDocTemplate(
        buffer,                      # Write to memory buffer
        pagesize     = A4,           # Standard A4 page
        rightMargin  = 2 * cm,       # 2cm right margin
        leftMargin   = 2 * cm,       # 2cm left margin
        topMargin    = 2 * cm,       # 2cm top margin
        bottomMargin = 2 * cm        # 2cm bottom margin
    )

    # ── Define text styles ────────────────────────────────────
    styles = getSampleStyleSheet()  # Load default styles as base

    # Title style — large centered navy text
    style_title = ParagraphStyle(
        "CustomTitle",
        parent    = styles["Title"],
        fontSize  = 22,
        textColor = COLOR_NAVY,
        alignment = TA_CENTER,
        spaceAfter = 4
    )

    # Subtitle style — smaller centered steel blue text
    style_subtitle = ParagraphStyle(
        "CustomSubtitle",
        parent    = styles["Normal"],
        fontSize  = 11,
        textColor = COLOR_STEEL,
        alignment = TA_CENTER,
        spaceAfter = 2
    )

    # Section heading style — left-aligned navy bold text
    style_heading = ParagraphStyle(
        "CustomHeading",
        parent     = styles["Heading2"],
        fontSize   = 13,
        textColor  = COLOR_NAVY,
        spaceBefore = 14,
        spaceAfter  = 6
    )

    # Normal body text style
    style_body = ParagraphStyle(
        "CustomBody",
        parent    = styles["Normal"],
        fontSize  = 10,
        textColor = COLOR_NAVY,
        spaceAfter = 4,
        leading   = 16   # Line height
    )

    # Gray secondary text style — for labels and metadata
    style_gray = ParagraphStyle(
        "CustomGray",
        parent    = styles["Normal"],
        fontSize  = 9,
        textColor = COLOR_GRAY,
        spaceAfter = 2
    )

    # ── Start building PDF content ────────────────────────────
    story = []  # List of PDF elements — added top to bottom

    # ── HEADER SECTION ───────────────────────────────────────
    story.append(Paragraph("IdeaCheck", style_title))
    story.append(Paragraph("Faculty of Engineering — Graduation Project Similarity Report", style_subtitle))
    story.append(Paragraph(
        f"Generated on: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        style_gray
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_ACCENT))  # Horizontal line
    story.append(Spacer(1, 0.3 * cm))  # Small vertical space

    # ── STUDENT INFO SECTION ──────────────────────────────────
    story.append(Paragraph("Student Information", style_heading))

    # Info table — 2 columns: label | value
    student_data = [
        ["Student Name",  student_name                          ],
        ["Project Title", submission["title"]                   ],
        ["Department",    submission.get("department") or "N/A" ],
        ["Submitted on",  submission["created_at"].strftime("%d %B %Y") if submission.get("created_at") else "N/A"],
    ]

    # Style the info table
    info_table = Table(student_data, colWidths=[4.5 * cm, 13 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), COLOR_LIGHT),      # Light blue for label column
        ("TEXTCOLOR",   (0, 0), (0, -1), COLOR_STEEL),      # Steel blue text for labels
        ("TEXTCOLOR",   (1, 0), (1, -1), COLOR_NAVY),       # Navy text for values
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),  # Bold labels
        ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),       # Normal values
        ("FONTSIZE",    (0, 0), (-1, -1), 10),               # Font size 10 for all cells
        ("PADDING",     (0, 0), (-1, -1), 8),                # 8pt padding in all cells
        ("GRID",        (0, 0), (-1, -1), 0.5, COLOR_LIGHT), # Light grid lines
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COLOR_WHITE, colors.HexColor("#f4f7fb")]),  # Alternating rows
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3 * cm))

    # ── SIMILARITY SCORE SECTION ──────────────────────────────
    story.append(Paragraph("Similarity Score", style_heading))

    score       = submission["similarity_score"]   # The percentage score
    score_color = get_score_color(score)            # Color based on score range

    # Score display table — big score number with colored background
    score_data = [[
        Paragraph(
            f"<font size='28' color='{score_color.hexval()}'><b>{round(score, 1)}%</b></font>",
            ParagraphStyle("score", alignment=TA_CENTER)
        )
    ]]

    score_table = Table(score_data, colWidths=[17.5 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_LIGHT),  # Light blue background
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),      # Center the score
        ("PADDING",    (0, 0), (-1, -1), 16),            # Comfortable padding
        ("ROUNDEDCORNERS", [6]),                          # Rounded corners
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.2 * cm))

    # Suggestion title below the score
    story.append(Paragraph(f"<b>{suggestion['title']}</b>", style_body))
    story.append(Paragraph(suggestion["message"], style_gray))
    story.append(Spacer(1, 0.3 * cm))

    # ── IMPROVEMENT TIPS SECTION ──────────────────────────────
    story.append(Paragraph("Improvement Tips", style_heading))

    for tip in suggestion["tips"]:
        # Each tip as a bullet point
        story.append(Paragraph(f"• {tip}", style_body))

    story.append(Spacer(1, 0.3 * cm))

    # ── TOP SIMILAR PROJECTS SECTION ─────────────────────────
    if top_matches:
        story.append(Paragraph("Most Similar Previous Projects", style_heading))

        # Table headers
        matches_data = [["#", "Project Title", "Department", "Year", "Similarity"]]

        # Add each matching project as a row
        for i, match in enumerate(top_matches, 1):
            match_color = get_score_color(match["score"])  # Color for this match's score
            matches_data.append([
                str(i),                              # Row number
                match["title"],                      # Project title
                match.get("department") or "N/A",    # Department
                str(match.get("year") or "N/A"),     # Year
                f"{match['score']}%"                 # Similarity percentage
            ])

        # Style the matches table
        matches_table = Table(
            matches_data,
            colWidths=[0.8*cm, 8*cm, 4*cm, 1.8*cm, 2.5*cm]  # Column widths
        )
        matches_table.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0), COLOR_NAVY),    # Navy header row
            ("TEXTCOLOR",      (0, 0), (-1, 0), COLOR_WHITE),   # White text in header
            ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold header text
            ("FONTSIZE",       (0, 0), (-1, -1), 9),            # Font size 9 for all
            ("ALIGN",          (0, 0), (-1, -1), "CENTER"),     # Center all cells
            ("ALIGN",          (1, 0), (1, -1), "LEFT"),        # Left-align title column
            ("PADDING",        (0, 0), (-1, -1), 7),            # 7pt padding
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_WHITE, colors.HexColor("#f4f7fb")]),
            ("GRID",           (0, 0), (-1, -1), 0.5, COLOR_LIGHT),  # Light grid lines
        ]))
        story.append(matches_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── PROJECT DESCRIPTION SECTION ──────────────────────────
    story.append(Paragraph("Submitted Project Description", style_heading))
    story.append(Paragraph(submission["description"], style_body))  # Full description text

    # ── FOOTER ───────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_LIGHT))  # Thin footer line
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "This report was generated automatically by IdeaCheck — "
        "Faculty of Engineering Graduation Project Similarity Checker.",
        style_gray
    ))

    # ── Build the PDF and write to buffer ─────────────────────
    doc.build(story)   # Render all elements into the PDF

    buffer.seek(0)     # Reset buffer position to beginning so it can be read
    return buffer      # Return the in-memory PDF file
