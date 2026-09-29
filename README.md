# Vehicle Service RCA & Professional Report Generator

A Streamlit application for vehicle service engineers to document failures using a first-principles workflow and generate professional PDF reports.

## Features
- Vehicle/customer/job details
- Failure reported and failure observed
- First-principles system analysis
- Diagnostic measurements
- DTC records
- 5-Why root cause analysis
- Root-cause category and failure mode
- Corrective/preventive action
- Parts and labour records
- Before/after evidence
- Photo evidence
- Professional PDF report
- JSON report archive

## Run
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

The generated PDF and JSON files are saved under `reports/`.
