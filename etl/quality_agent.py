import pandas as pd
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def run_quality_checks(df: pd.DataFrame) -> dict:
    checks = {}

    # Nulls
    null_counts = df.isnull().sum()
    checks["null_counts"] = {
        col: int(count)
        for col, count in null_counts.items()
        if count > 0
    }

    # Duplicates
    checks["duplicate_rows"] = int(df.duplicated().sum())

    # Type mismatches — numeric columns with non-numeric values
    type_issues = {}
    for col in df.columns:
        if df[col].dtype == object:
            numeric_attempt = pd.to_numeric(df[col], errors="coerce")
            failed = numeric_attempt.isna().sum() - df[col].isna().sum()
            if failed > 0:
                type_issues[col] = int(failed)
    checks["type_mismatches"] = type_issues

    # Outliers in numeric columns (IQR method)
    outliers = {}
    for col in df.select_dtypes(include=["number"]).columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outlier_count = int(
            ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
        )
        if outlier_count > 0:
            outliers[col] = outlier_count
    checks["outliers"] = outliers

    # Empty strings
    empty_strings = {}
    for col in df.select_dtypes(include="object").columns:
        count = int((df[col].str.strip() == "").sum())
        if count > 0:
            empty_strings[col] = count
    checks["empty_strings"] = empty_strings

    return checks

PROMPT = """
You are a data quality analyst. Given these data quality check results for a dataset,
provide a clear analysis of what needs to be fixed.

Quality check results (JSON):
{checks}

Schema info:
{schema}

Respond with a JSON object with these keys:
- "severity": "low", "medium", or "high"
- "summary": 2 sentence plain English summary of the overall data quality
- "issues": list of objects, each with:
    - "issue": name of the issue
    - "affected_columns": list of column names
    - "fix_strategy": what should be done to fix it (specific, not vague)
- "confidence_score": integer 0-100 representing overall data quality

Respond ONLY with valid JSON. No markdown, no backticks, no explanation.
"""

def analyze_quality(df: pd.DataFrame, schema: list) -> dict:
    checks = run_quality_checks(df)

    prompt = PromptTemplate(
        input_variables=["checks", "schema"],
        template=PROMPT
    )
    chain = prompt | llm
    result = chain.invoke({
        "checks": json.dumps(checks, indent=2),
        "schema": json.dumps(schema, indent=2)
    })

    text = result.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        analysis = json.loads(text)
        analysis["raw_checks"] = checks
        return analysis
    except json.JSONDecodeError:
        return {"error": "Quality analysis failed", "raw": text, "raw_checks": checks}