# AI Smart ETL Pipeline

An intelligent data cleaning and transformation system that accepts any messy CSV or Excel file, automatically understands the schema, detects quality issues, semantically normalizes inconsistent values, generates and executes custom Pandas cleaning code, and produces a professional data quality report — all powered by LLM reasoning.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![LangChain](https://img.shields.io/badge/LangChain-latest-green) ![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-orange) ![Streamlit](https://img.shields.io/badge/Streamlit-latest-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Demo

Upload any CSV or Excel → watch 5 AI stages run → download a clean dataset and a quality report.

**Works on any dataset** — product catalogs, customer records, financial data, HR data, sales exports, survey responses. No configuration required.

---

## The Problem This Solves

Traditional ETL pipelines require engineers to manually write cleaning rules for every dataset. A rule written for one dataset is useless for the next. This system uses an LLM to read the actual data, understand what it means, and write the correct cleaning code on the fly — for any dataset it has never seen before.

---

## How It Works

### Pipeline

```
Upload CSV/Excel
      ↓
Stage 1 — AI Schema Detection
  LLM reads sample rows and infers column types, intent, and likely issues
      ↓
Stage 2 — Quality Analysis
  Pandas profiling (nulls, dupes, type mismatches, outliers) + LLM interpretation
      ↓
Stage 3 — Semantic Normalization
  LLM reads all unique values per column, spots inconsistencies,
  writes and executes a normalize_dataframe() function
      ↓
Stage 4 — Transformation Code Generation
  LLM writes and executes a clean_dataframe() function for structural fixes
      ↓
Stage 5 — Report Generation
  LLM writes a professional data quality report in Markdown
      ↓
Download clean CSV + quality report
```

### The Key Insight — LLM-Generated Code

Most AI data tools classify problems into fixed categories and apply hardcoded rules. This system takes a fundamentally different approach:

**The LLM reads the actual data and writes the fix itself.**

For semantic normalization, instead of trying to predict every possible inconsistency pattern, the system sends the unique values of every text column to the LLM and asks it to write a `normalize_dataframe()` function. The LLM acts as the pattern-recognition engine — finding things like `XL` vs `Extra Large` vs `extra-large`, `in_stock` vs `In Stock` vs `in-stock`, mixed units, typos, casing issues — without any hardcoded rules. This works for any dataset because the LLM adapts to whatever it finds.

---

## Example — What It Fixes

Given a messy product catalog with 1000 rows:

| Issue | Before | After |
|---|---|---|
| Size inconsistency | `XL`, `Extra Large`, `extra-large`, `xl` | `XL` |
| Availability format | `in_stock`, `In Stock`, `in-stock`, `IN_STOCK` | `in_stock` |
| Casing inconsistency | `Active`, `active`, `ACTIVE` | `Active` |
| Null values | 47 missing entries | Filled or flagged |
| Duplicate rows | 12 exact duplicates | Removed |
| Type mismatches | Age column containing `"abc"` | Coerced or nulled |
| Outliers | Salary of `-5000` | Flagged in report |

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| LLM | Groq LLaMA 3.3 70b | Fast inference, large context, free tier |
| LLM orchestration | LangChain Core | Prompt templates, chain composition |
| Data processing | Pandas | Industry-standard DataFrame operations |
| Excel support | openpyxl | Read `.xlsx` and `.xls` files |
| UI | Streamlit | Live pipeline progress, download buttons |

---

## Project Structure

```
smart-etl/
├── app.py                    # Streamlit UI with live stage progress
├── etl/
│   ├── __init__.py
│   ├── loader.py             # CSV/Excel → DataFrame + sample extraction
│   ├── schema_agent.py       # LLM infers column types and intent
│   ├── quality_agent.py      # Pandas profiling + LLM quality analysis
│   ├── normalize_agent.py    # LLM generates semantic normalization code
│   ├── codegen_agent.py      # LLM generates structural cleaning code
│   └── report_agent.py       # LLM writes data quality report
├── requirements.txt
└── .env                      # API keys (never committed)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Free [Groq API key](https://console.groq.com) — no credit card needed

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/smart-etl.git
cd smart-etl

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your-groq-key-here
```

### Run

```bash
streamlit run app.py
```

Open http://localhost:8501, upload any CSV or Excel file, and click **Run AI ETL Pipeline**.

---

## Key Concepts Demonstrated

- **LLM code generation and execution** — generates and runs real Python code dynamically, adapting to the specific dataset provided
- **Adaptive AI pipelines** — no hardcoded rules anywhere; the LLM reads the data and decides what to fix
- **Multi-stage ETL architecture** — schema inference → quality profiling → semantic normalization → structural cleaning → reporting
- **Pandas profiling** — automated detection of nulls, duplicates, type mismatches, outliers, and empty strings
- **Safe code execution** — generated code runs in an isolated local scope with error handling and fallback to original data
- **Data quality scoring** — every run produces a confidence score and severity rating with actionable recommendations

---

## Limitations & Future Improvements

- [ ] Support for JSON and Parquet file formats
- [ ] Persist cleaning rules — save rules from one run and reuse on similar datasets
- [ ] Column-level confidence scores — flag columns where the AI is uncertain
- [ ] Streaming output — show live token-by-token generation as the LLM writes code
- [ ] Database connectors — connect directly to PostgreSQL, MySQL, or Snowflake
- [ ] Scheduled pipeline runs — auto-clean new data drops on a schedule
- [ ] Diff view — side-by-side comparison of original vs cleaned values per column

---

## License

MIT
