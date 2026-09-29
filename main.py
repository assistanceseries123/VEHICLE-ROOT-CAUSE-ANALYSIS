import streamlit as st
from pathlib import Path
from datetime import datetime
import json, uuid, os, re
import pandas as pd

from pdf_report import build_pdf

BASE = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE / "reports"
REPORT_DIR.mkdir(exist_ok=True)
ASSET_DIR = BASE / "assets"
ASSET_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Vehicle Service RCA",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "report_id" not in st.session_state:
    st.session_state.report_id = f"RCA-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:5].upper()}"

def safe_filename(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)

def text_area(label, key, help=None):
    return st.text_area(label, key=key, height=110, help=help)

st.title("Root cause Analysis & Professional Report Generator")
st.caption("First principles diagnosis • 5-Why RCA • Diagnostic evidence • Professional PDF")

with st.sidebar:
    st.header("Report Control")
    st.session_state.report_id = st.text_input("Report No.", st.session_state.report_id)
    report_date = st.date_input("Report Date", datetime.now().date())
    engineer = st.text_input("Service Engineer", "")
    designation = st.text_input("Designation", "Service Engineer")
    branch = st.text_input("Workshop / Branch", "")
    st.divider()
    st.info("Tip: Record measured values and evidence before concluding the root cause.")

tabs = st.tabs([
    "1. Vehicle", "2. Complaint", "3. Diagnosis",
    "4. 5-Why RCA", "5. Actions", "6. Evidence", "7. Generate"
])

with tabs[0]:
    st.subheader("Vehicle & Customer Information")
    c1, c2, c3 = st.columns(3)
    customer = c1.text_input("Customer / Fleet", "")
    registration = c2.text_input("Registration No.", "")
    vin = c3.text_input("VIN / Chassis No.", "")
    c1, c2, c3 = st.columns(3)
    model = c1.text_input("Vehicle Model", "")
    engine = c2.text_input("Engine Model / Type", "")
    emission = c3.selectbox("Emission Standard", ["BS4", "BS6", "Other / N/A"])
    c1, c2, c3 = st.columns(3)
    mileage = c1.text_input("Odometer (km)", "")
    engine_hours = c2.text_input("Engine Hours", "")
    job_card = c3.text_input("Job Card / Service Order No.", "")
    application = st.text_input("Vehicle Application / Body Type", "")
    operating_condition = st.text_area("Operating Condition at Failure", height=90,
        placeholder="Loaded/unloaded, uphill/flat road, ambient condition, speed/RPM, traffic, duty cycle...")

with tabs[1]:
    st.subheader("Failure Definition")
    failure_reported = text_area("Failure Reported / Customer Complaint", "failure_reported")
    failure_observed = text_area("Failure Observed During Inspection / Road Test", "failure_observed")
    c1, c2 = st.columns(2)
    symptom_duration = c1.text_input("Failure Occurrence / Duration", "")
    occurrence = c2.selectbox("Occurrence Type", ["Continuous", "Intermittent", "Occasional", "One-time", "Unknown"])
    c1, c2, c3 = st.columns(3)
    warning_lamp = c1.text_input("Warning Lamp / Indicator", "")
    dtc_initial = c2.text_input("Initial DTC(s)", "")
    severity = c3.selectbox("Severity", ["Low", "Medium", "High", "Vehicle Immobilized"])
    system = st.selectbox("Primary System", [
        "Engine", "Cooling System", "Fuel System", "Air Intake / Turbo",
        "Exhaust / EGR / SCR / DPF", "Clutch", "Transmission / Gearbox",
        "Driveline / Differential", "Brake System", "Steering / Suspension",
        "Electrical / Charging", "Starting System", "HVAC / AC", "Body / Other"
    ])
    first_principle = text_area(
        "First-Principles System Explanation",
        "first_principle",
    )
    st.caption("Example: heat generation → coolant absorbs heat → coolant circulation → radiator rejects heat → fan provides airflow.")

with tabs[2]:
    st.subheader("Diagnostic Investigation")
    st.markdown("### Diagnostic Checks")
    default_rows = [
        ["Visual inspection", "", "", ""],
        ["Electrical supply / ground", "", "", ""],
        ["Sensor / actuator signal", "", "", ""],
        ["Pressure / flow", "", "", ""],
        ["Mechanical condition", "", "", ""],
        ["Scan tool / DTC", "", "", ""],
    ]
    df_checks = pd.DataFrame(default_rows, columns=["Check", "Expected", "Actual", "Result"])
    df_checks = st.data_editor(df_checks, num_rows="dynamic", use_container_width=True, key="checks")

    st.markdown("### DTC / Diagnostic Data")
    dtc_rows = [["", "", "", ""]]
    df_dtc = pd.DataFrame(dtc_rows, columns=["DTC", "Description", "Live Data / Condition", "Finding"])
    df_dtc = st.data_editor(df_dtc, num_rows="dynamic", use_container_width=True, key="dtcs")

    st.markdown("### Measured Parameters")
    measure_rows = [["", "", "", "", ""]]
    df_measure = pd.DataFrame(
        measure_rows,
        columns=["Parameter", "Unit", "Expected / Specification", "Measured Value", "Assessment"]
    )
    df_measure = st.data_editor(df_measure, num_rows="dynamic", use_container_width=True, key="measurements")

    diagnostic_findings = text_area("Diagnostic Findings / Evidence", "diagnostic_findings")
    suspected_causes = text_area(
        "Possible Causes Considered and Eliminated",
        "suspected_causes",
        "List hypotheses and the evidence that ruled them in/out."
    )

with tabs[3]:
    st.subheader("5-Why Root Cause Analysis")
    st.caption("Do not stop at the failed part. Continue asking why until the physical/system cause is supported by evidence.")
    why1 = st.text_input("Why 1 — Why did the failure occur?", "")
    why2 = st.text_input("Why 2 — Why did that condition occur?", "")
    why3 = st.text_input("Why 3 — Why did that condition occur?", "")
    why4 = st.text_input("Why 4 — Why was the previous cause present?", "")
    why5 = st.text_input("Why 5 — What underlying cause allowed it to happen?", "")
    c1, c2 = st.columns(2)
    failure_mode = c1.text_area("Failure Mode", height=100,
        placeholder="Example: cooling fan clutch failed to engage when commanded.")
    root_cause = c2.text_area("Confirmed Root Cause", height=100,
        placeholder="State the physical/system cause supported by inspection and measurements.")
    root_category = st.selectbox("Root Cause Category", [
        "Manufacturing / Material",
        "Assembly / Installation",
        "Maintenance",
        "Operation / Application",
        "External / Environmental",
        "Electrical / Wiring",
        "Sensor / Actuator",
        "ECU / Control / Communication",
        "Lubrication / Fluid",
        "Unknown / Further Investigation Required"
    ])
    root_confidence = st.selectbox("RCA Status", [
        "Confirmed by evidence",
        "Probable — further confirmation required",
        "Not confirmed — investigation ongoing"
    ])

with tabs[4]:
    st.subheader("Corrective & Preventive Actions")
    corrective = text_area("Corrective Action", "corrective")
    preventive = text_area("Preventive Action / Recommendation", "preventive")
    verification = text_area("Repair Verification / Road Test Result", "verification")
    replaced_parts = st.text_area("Parts Replaced / Repaired", height=100)
    labour = st.text_area("Labour / Workshop Work Performed", height=100)
    warranty = st.selectbox("Warranty Recommendation", [
        "Not applicable",
        "Recommended for warranty",
        "Not recommended for warranty",
        "Subject to warranty team evaluation"
    ])
    warranty_justification = text_area("Warranty Technical Justification", "warranty_justification")

with tabs[5]:
    st.subheader("Photo & Supporting Evidence")
    photos = st.file_uploader(
        "Upload failure / component / diagnostic photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    supporting_notes = text_area("Additional Technical Notes", "supporting_notes")
    st.caption("Use clear photos showing the failed component, damage mechanism, DTC/scan data, and relevant surrounding parts.")

with tabs[6]:
    st.subheader("Report Preview & Generation")
    st.markdown("### Quality Gate")
    quality = {
        "Vehicle identification": bool(vin or registration),
        "Failure reported": bool(failure_reported.strip()),
        "Failure observed": bool(failure_observed.strip()),
        "Diagnostic evidence": bool(diagnostic_findings.strip()),
        "Root cause": bool(root_cause.strip()),
        "Corrective action": bool(corrective.strip()),
        "Verification": bool(verification.strip()),
    }
    for item, ok in quality.items():
        st.write(("✅ " if ok else "⚠️ ") + item)

    st.divider()
    st.markdown("### Generate Professional PDF")
    if st.button("🚀 Generate RCA Report", type="primary", use_container_width=True):
        report = {
            "report_id": st.session_state.report_id,
            "report_date": str(report_date),
            "engineer": engineer,
            "designation": designation,
            "branch": branch,
            "customer": customer,
            "registration": registration,
            "vin": vin,
            "model": model,
            "engine": engine,
            "emission": emission,
            "mileage": mileage,
            "engine_hours": engine_hours,
            "job_card": job_card,
            "application": application,
            "operating_condition": operating_condition,
            "failure_reported": failure_reported,
            "failure_observed": failure_observed,
            "symptom_duration": symptom_duration,
            "occurrence": occurrence,
            "warning_lamp": warning_lamp,
            "dtc_initial": dtc_initial,
            "severity": severity,
            "system": system,
            "first_principle": first_principle,
            "checks": df_checks.to_dict("records"),
            "dtcs": df_dtc.to_dict("records"),
            "measurements": df_measure.to_dict("records"),
            "diagnostic_findings": diagnostic_findings,
            "suspected_causes": suspected_causes,
            "why": [why1, why2, why3, why4, why5],
            "failure_mode": failure_mode,
            "root_cause": root_cause,
            "root_category": root_category,
            "root_confidence": root_confidence,
            "corrective": corrective,
            "preventive": preventive,
            "verification": verification,
            "replaced_parts": replaced_parts,
            "labour": labour,
            "warranty": warranty,
            "warranty_justification": warranty_justification,
            "supporting_notes": supporting_notes,
        }

        json_path = REPORT_DIR / f"{safe_filename(report['report_id'])}.json"
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        photo_paths = []
        for i, photo in enumerate(photos or []):
            p = ASSET_DIR / f"{safe_filename(report['report_id'])}_{i+1}_{safe_filename(photo.name)}"
            p.write_bytes(photo.getbuffer())
            photo_paths.append(str(p))

        pdf_path = REPORT_DIR / f"{safe_filename(report['report_id'])}.pdf"
        build_pdf(report, pdf_path, photo_paths)

        st.success("Professional RCA report generated successfully.")
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 Download PDF Report",
                f,
                file_name=pdf_path.name,
                mime="application/pdf",
                use_container_width=True
            )
        with open(json_path, "rb") as f:
            st.download_button(
                "🗂️ Download Report Data (JSON)",
                f,
                file_name=json_path.name,
                mime="application/json",
                use_container_width=True
            )
