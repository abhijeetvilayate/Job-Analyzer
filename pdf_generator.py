import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

def generate_pdf_report(result: Dict[str, Any], candidate_name: str = "Candidate") -> bytes:
    """
    Generates a professional, beautifully styled PDF report of the resume analysis.
    Returns the PDF file as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1e3a8a")     # Deep Indigo
    secondary_color = colors.HexColor("#3b82f6")   # Blue
    dark_text = colors.HexColor("#1f2937")         # Charcoal
    light_bg = colors.HexColor("#f8fafc")          # Off white
    border_color = colors.HexColor("#e2e8f0")

    # Typography styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b")
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_text
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_text,
        leftIndent=12,
        spaceAfter=3
    )

    score = result.get("match_score", 0)
    score_color = colors.HexColor("#16a34a") if score >= 80 else (colors.HexColor("#ea580c") if score >= 60 else colors.HexColor("#dc2626"))

    story = []

    # 1. Header Banner
    header_table = Table(
        [
            [
                Paragraph("<b>SMART RESUME & JOB FIT REPORT</b>", title_style),
                Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%b %d, %Y - %H:%M')}", subtitle_style)
            ]
        ],
        colWidths=[400, 140]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT')
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceAfter=10))

    # 2. Score & Executive Summary Card
    score_text = f"<font size=28 color='{score_color.hexval()}'><b>{score}%</b></font><br/><font size=8 color='#64748b'>ATS MATCH SCORE</font>"
    summary_text = f"<b>Executive Fit Summary:</b><br/>{result.get('summary', 'Analysis completed.')}<br/><br/><b>Seniority / Experience Fit:</b> {result.get('experience_alignment', 'N/A')}"

    summary_card = Table(
        [
            [
                Paragraph(score_text, ParagraphStyle("CenterScore", parent=body_style, alignment=1)),
                Paragraph(summary_text, body_style)
            ]
        ],
        colWidths=[120, 420]
    )
    summary_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('LINEAFTER', (0, 0), (0, 0), 1, border_color)
    ]))
    story.append(summary_card)
    story.append(Spacer(1, 10))

    # 3. Keywords & Competencies Gap Table
    story.append(Paragraph("Keyword & Skill Alignment", section_heading))
    
    matched_kws = result.get("matched_keywords", [])
    missing_kws = result.get("missing_keywords", [])

    matched_cell = "<br/>".join([f"• <font color='#16a34a'><b>✓</b></font> {kw}" for kw in matched_kws]) if matched_kws else "None identified"
    missing_cell = "<br/>".join([f"• <font color='#dc2626'><b>✕</b></font> {kw}" for kw in missing_kws]) if missing_kws else "None identified"

    kw_table = Table(
        [
            [
                Paragraph("<b>Matched Competencies & Keywords</b>", ParagraphStyle("H1", parent=body_style, textColor=colors.HexColor("#15803d"))),
                Paragraph("<b>Critical Missing Keywords / Requirements</b>", ParagraphStyle("H2", parent=body_style, textColor=colors.HexColor("#b91c1c")))
            ],
            [
                Paragraph(matched_cell, body_style),
                Paragraph(missing_cell, body_style)
            ]
        ],
        colWidths=[270, 270]
    )
    kw_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#f0fdf4")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#fef2f2")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(kw_table)
    story.append(Spacer(1, 10))

    # 4. Strengths & Gaps
    story.append(Paragraph("Strengths & Identified Gaps", section_heading))
    strengths_items = "<br/>".join([f"• <b>{s}</b>" for s in result.get("strengths", [])])
    gaps_items = "<br/>".join([f"• {g}" for g in result.get("areas_for_improvement", [])])

    sg_table = Table(
        [
            [
                Paragraph("<b>Key Candidate Strengths</b>", body_style),
                Paragraph("<b>Areas for Improvement</b>", body_style)
            ],
            [
                Paragraph(strengths_items or "None listed", body_style),
                Paragraph(gaps_items or "None listed", body_style)
            ]
        ],
        colWidths=[270, 270]
    )
    sg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(sg_table)
    story.append(Spacer(1, 10))

    # 5. Tailored Improvement Tips
    tips = result.get("tailored_improvement_tips", [])
    if tips:
        story.append(Paragraph("Actionable Optimization Steps", section_heading))
        for i, tip in enumerate(tips, 1):
            story.append(Paragraph(f"<b>{i}.</b> {tip}", bullet_style))
        story.append(Spacer(1, 8))

    # 6. Suggested Bullet Points
    bullet_points = result.get("suggested_bullet_points", [])
    if bullet_points:
        story.append(Paragraph("Tailored Resume Phrasing Recommendations", section_heading))
        story.append(Paragraph("<i>Incorporate or adapt these targeted phrasing suggestions into your resume's experience section:</i>", subtitle_style))
        story.append(Spacer(1, 4))
        for bp in bullet_points:
            story.append(Paragraph(f"• {bp}", bullet_style))

    # Build PDF Document
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
