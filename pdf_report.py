from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from pathlib import Path
import os

def esc(value):
    if value is None:
        return ""
    s = str(value)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")

def build_pdf(r, output_path, photo_paths=None):
    output_path = str(output_path)
    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title2", parent=styles["Title"], fontSize=18, leading=22,
        alignment=TA_CENTER, spaceAfter=8
    )
    h1 = ParagraphStyle(
        "H1x", parent=styles["Heading1"], fontSize=12, leading=15,
        spaceBefore=8, spaceAfter=5
    )
    body = ParagraphStyle(
        "Bodyx", parent=styles["BodyText"], fontSize=8.5, leading=12,
        spaceAfter=4
    )
    small = ParagraphStyle(
        "Smallx", parent=styles["BodyText"], fontSize=7.5, leading=10
    )
    center = ParagraphStyle(
        "Centerx", parent=body, alignment=TA_CENTER
    )

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=14*mm, leftMargin=14*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    story = []
    story.append(Paragraph("ASHOK LT ENGINEERING SERVICES PVT LTD", title))
    story.append(Paragraph("FAILURE ANALYSIS & ROOT CAUSE ANALYSIS REPORT", title))
    story.append(Spacer(1, 3))
    meta = [
        [Paragraph("<b>Report No.</b>", small), esc(r["report_id"]),
         Paragraph("<b>Date</b>", small), esc(r["report_date"])],
        [Paragraph("<b>Service Engineer</b>", small), esc(r["engineer"]),
         Paragraph("<b>Workshop / Branch</b>", small), esc(r["branch"])],
        [Paragraph("<b>Customer / Fleet</b>", small), esc(r["customer"]),
         Paragraph("<b>Job Card</b>", small), esc(r["job_card"])],
    ]
    t = Table(meta, colWidths=[30*mm, 65*mm, 35*mm, 50*mm])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
        ("BACKGROUND", (2,0), (2,-1), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [t, Spacer(1, 7)]

    def section(title_text):
        story.append(Paragraph(title_text, h1))

    def para(label, value):
        story.append(Paragraph(f"<b>{esc(label)}</b><br/>{esc(value) or '—'}", body))

    section("1. Vehicle Identification")
    vehicle = [
        ["Registration", r["registration"], "VIN / Chassis", r["vin"]],
        ["Model", r["model"], "Engine", r["engine"]],
        ["Emission", r["emission"], "Odometer", r["mileage"]],
        ["Engine Hours", r["engine_hours"], "Application", r["application"]],
    ]
    vt = Table([[Paragraph(f"<b>{esc(x)}</b>", small) if i in (0,2) else esc(x)
                 for i,x in enumerate(row)] for row in vehicle],
               colWidths=[28*mm, 58*mm, 30*mm, 64*mm])
    vt.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), .4, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
        ("BACKGROUND", (2,0), (2,-1), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    story.append(vt)
    para("Operating Condition", r["operating_condition"])

    section("2. Failure Definition")
    para("Failure Reported", r["failure_reported"])
    para("Failure Observed", r["failure_observed"])
    para("Occurrence", f'{r["occurrence"]} | Severity: {r["severity"]} | System: {r["system"]}')
    para("Warning / DTC", f'{r["warning_lamp"]} | {r["dtc_initial"]}')

    section("3. First-Principles System Analysis")
    para("System Principle", r["first_principle"])

    section("4. Diagnostic Investigation")
    checks = [["Check", "Expected", "Actual", "Result"]]
    for x in r["checks"]:
        if any(str(v).strip() for v in x.values()):
            checks.append([x.get("Check",""), x.get("Expected",""), x.get("Actual",""), x.get("Result","")])
    ct = Table([[Paragraph(f"<b>{esc(v)}</b>", small) for v in row] if i == 0
                else [esc(v) for v in row] for i,row in enumerate(checks)],
               colWidths=[45*mm, 45*mm, 45*mm, 35*mm])
    ct.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),.35,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("FONTSIZE",(0,0),(-1,-1),7),
    ]))
    story.append(ct)

    measures = [["Parameter","Unit","Expected","Measured","Assessment"]]
    for x in r["measurements"]:
        if any(str(v).strip() for v in x.values()):
            measures.append([x.get("Parameter",""), x.get("Unit",""), x.get("Expected / Specification",""),
                             x.get("Measured Value",""), x.get("Assessment","")])
    mt = Table([[Paragraph(f"<b>{esc(v)}</b>", small) for v in row] if i == 0
                else [esc(v) for v in row] for i,row in enumerate(measures)],
               colWidths=[39*mm, 18*mm, 43*mm, 40*mm, 40*mm])
    mt.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),.35,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("FONTSIZE",(0,0),(-1,-1),7),
    ]))
    story.append(Spacer(1,4))
    story.append(mt)
    para("Diagnostic Findings", r["diagnostic_findings"])
    para("Possible Causes Considered / Eliminated", r["suspected_causes"])

    section("5. 5-Why Root Cause Analysis")
    whys = []
    for i, value in enumerate(r["why"], 1):
        whys.append([f"Why {i}", value or "—"])
    wt = Table([[Paragraph(f"<b>{esc(a)}</b>", small), esc(b)] for a,b in whys],
               colWidths=[22*mm, 158*mm])
    wt.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),.35,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.whitesmoke),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("FONTSIZE",(0,0),(-1,-1),8),
    ]))
    story.append(wt)
    para("Failure Mode", r["failure_mode"])
    para("Confirmed Root Cause", r["root_cause"])
    para("Root Cause Category", r["root_category"])
    para("RCA Status", r["root_confidence"])

    section("6. Corrective / Preventive Action")
    para("Corrective Action", r["corrective"])
    para("Preventive Action", r["preventive"])
    para("Repair Verification / Road Test", r["verification"])
    para("Parts Replaced / Repaired", r["replaced_parts"])
    para("Labour / Workshop Work", r["labour"])

    section("7. Warranty Assessment")
    para("Warranty Recommendation", r["warranty"])
    para("Technical Justification", r["warranty_justification"])

    if r.get("supporting_notes"):
        section("8. Additional Technical Notes")
        para("Notes", r["supporting_notes"])

    photo_paths = photo_paths or []
    valid_photos = [p for p in photo_paths if os.path.exists(p)]
    if valid_photos:
        section("9. Photographic Evidence")
        for i in range(0, len(valid_photos), 2):
            row = []
            for p in valid_photos[i:i+2]:
                try:
                    img = Image(p, width=82*mm, height=58*mm)
                    img.hAlign = "CENTER"
                    row.append(img)
                except Exception:
                    row.append(Paragraph("Photo unavailable", body))
            while len(row) < 2:
                row.append("")
            pt = Table([row], colWidths=[88*mm, 88*mm])
            pt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
            story.append(pt)
            story.append(Spacer(1, 5))

    section("10. Service Engineer Declaration")
    story.append(Paragraph(
        "The above findings are based on the inspection, diagnostic measurements, "
        "available vehicle data, and verification performed during the investigation. "
        "The root cause should be considered confirmed only where supporting evidence "
        "has been documented and the repair has been verified under the relevant operating condition.",
        body
    ))
    sig = Table([
        ["Prepared By", "Reviewed / Approved By"],
        [f'{r["engineer"]}\n{r["designation"]}', ""],
        ["Signature: ____________________", "Signature: ____________________"],
        ["Date: __________________________", "Date: __________________________"],
    ], colWidths=[90*mm, 90*mm])
    sig.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),.35,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ]))
    story += [Spacer(1,8), sig]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.drawString(14*mm, 8*mm, f'RCA Report: {r["report_id"]}')
        canvas.drawRightString(A4[0]-14*mm, 8*mm, f'Page {doc.page}')
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
