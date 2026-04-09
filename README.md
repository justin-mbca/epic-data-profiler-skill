
# Epic Data Profiler Skill

## Overview
This project implements a data-engineering skill for an LLM agent that ingests Epic-style data exports (CSV, JSON, or Parquet) and returns a structured data-quality profile. The skill summarizes the structure, statistics, and quality of the dataset, enabling the agent to reason about data readiness and recommend next steps without directly parsing large files.

## Features
- Ingests Epic data exports (CSV/JSON/Parquet)
- Computes column-wise statistics (min, max, mean, unique values, etc.)
- Detects missing values, schema drift, and potential data quality issues
- Returns a structured summary and explicit error/warning messages
- Tool-call compatible: exposes a clear function signature for LLM agent integration
- Includes tests for validation and edge cases

## Setup
1. Clone the repository or unzip the project files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the skill from the command line:
```bash
python -m skill.epic_data_profiler --file_path sample_data/sample_epic.csv
python -m skill.epic_data_profiler --file_path sample_data/sample_epic.json
python -m skill.epic_data_profiler --file_path sample_data/sample_epic.parquet
```

## Running Tests
```bash
PYTHONPATH=. pytest tests/
```

## Assignment Mapping: Part 1

**Skill selection & justification:**
- This skill enables an LLM agent to efficiently profile large or complex datasets (Epic exports) without reading the entire file into context. The agent uses the skill to obtain a concise, structured summary of data quality and schema, which is not feasible for the LLM alone.

**Data quality & trust:**
- Handles missing columns: Reports missing or unexpected columns in the `errors` field.
- Detects schema drift: Flags changes in expected schema if a reference is provided.
- Handles malformed rows or unreadable files: Returns clear error messages and partial results when possible.

**Interface design:**
- Input: `profile_epic_data(file_path, columns_to_profile=None)`
- Output: Structured dict with `summary` (per-column stats, warnings) and `errors` (critical issues). Warnings and errors are explicit, so the agent can reason about partial results and guide the user even if the data is imperfect.



## Alignment with the Take‑Home Exercise

This project is designed to fully address the “Data Engineering Take‑Home Exercise: Build a Skill for an LLM Agent” assignment.

**Part 1 — Design & Critical Thinking:**
- Includes a design document ([DESIGN.md](DESIGN.md)) that:
   - Explains why this Epic data profiler is a good fit for an LLM agent (LLMs can’t efficiently parse large files; this skill summarizes structure and quality for downstream reasoning).
   - Identifies at least three concrete data failure modes (e.g., missing columns, schema drift, malformed rows) and describes how the skill handles them (warnings, errors, partial results).
   - Describes the input/output contract: clear parameters, optional fields, and a structured response schema with explicit errors/warnings so the agent can always provide a useful response.

**Part 2 — Technical Implementation:**
- **Language:** Implemented in Python.
- **Runnable:** Install dependencies with `pip install -r requirements.txt` and invoke via CLI or Python import (see Usage section).
- **Tool‑call compatible:** Exposes a clear function signature `profile_epic_data(...)` that can be registered as an LLM tool/function (e.g., OpenAI‑style function calling or LangChain tools).
- **Tests:** Includes tests under `tests/` that validate parsing, missing‑value detection, and edge cases.
- **Data pipeline hygiene:** Uses schema‑aware parsing, type inference, missing‑value checks, and structured error/warning reporting for robust, trustworthy results.

**Assumptions made:**
- Data is assumed to be de‑identified Epic‑style exports (CSV/JSON/Parquet).
- The skill runs offline and does not store or transmit PHI.
- The LLM agent is expected to call the skill with a valid file path and handle the structured JSON output.

**Optional / nice‑to‑have:**
- The skill is designed so that an LLM agent can quickly inspect the profile and decide next steps (e.g., join, filter, enrich, or ask follow‑up questions).

## Design Document
See [DESIGN.md](DESIGN.md) for design rationale, interface, and data quality considerations.
