# Epic Data Profiler Skill — Design Document

## 1. Skill Selection & Justification

**Skill:** Data profiling for Epic EHR exports (CSV/JSON/Parquet).

**Justification:**
- Epic is a leading EHR system; data exports are common in healthcare analytics.
- Data analysts need to quickly assess the quality and structure of new data drops before deeper analysis.
- LLM agents can use this skill to automate data quality checks, summarize findings, and recommend next steps, saving analysts time and reducing manual errors.
- The skill adds value by standardizing profiling, surfacing issues early, and providing structured output for downstream reasoning.
- Supporting CSV, JSON, and Parquet formats ensures compatibility with common data export and analytics workflows.

## 2. Data Quality & Trust

**Failure Modes & Handling:**
1. **Missing Fields/Columns:**
   - If expected columns are missing, the skill logs a warning and includes it in the output `errors` list.
2. **Invalid or Ambiguous Values:**
   - If data contains unexpected types (e.g., text in numeric columns), the skill flags the column and summarizes the issue in `warnings`.
3. **Schema Drift:**
   - If the schema differs from previous runs (optional: if a reference schema is provided), the skill reports the drift in the output.

Other possible issues (not exhaustive):
- File not found or unreadable: returns a clear error message.
- Large files: processes in chunks or returns a warning if row count exceeds a threshold.
- Ambiguous units: flags columns with unclear units if detected.

## 3. Interface Design

**Input:**
- `file_path` (str): Path to the Epic data export (CSV, JSON, or Parquet).
- `columns_to_profile` (Optional[List[str]]): Subset of columns to profile (default: all).

**Output:**
- `summary` (dict):
    - Per-column stats: type, min, max, mean (if numeric), unique count, missing count, sample values.
    - Data quality warnings (list).
- `errors` (list of str): Any critical errors encountered (e.g., file not found, unreadable file).

**Schema Example:**
```json
{
  "summary": {
    "PatientID": {"type": "int", "unique": 1000, "missing": 0, "sample": ["123", "456"]},
    "Age": {"type": "int", "min": 0, "max": 99, "mean": 45.2, "missing": 2},
    "LabResult": {"type": "float", "min": 0.1, "max": 9.8, "mean": 4.2, "missing": 10, "warnings": ["Possible outliers"]}
  },
  "errors": ["Column 'DOB' missing"]
}
```

**Justification:**
- Flat, per-column stats are easy for LLMs and analysts to interpret.
- Warnings and errors are explicit, enabling the agent to reason about partial results and next steps.
- Optional columns parameter allows focused profiling for large datasets.

---

This design balances clarity, extensibility, and practical value for Habitat Health’s analytics workflows.
