import json
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

PROMPT = """
You are a data quality analyst writing a report for a business stakeholder.

Original dataset: {original_shape}
Cleaned dataset: {cleaned_shape}

Schema detected:
{schema}

Quality analysis:
{quality}

Transformation code applied:
{code}

Execution status: {status}

Write a professional data quality report in Markdown with these sections:
## Executive Summary
## Schema Overview (table with columns: Column | Inferred Type | Intent)
## Quality Issues Found
## Transformations Applied
## Before vs After Comparison
## Recommendations

Be specific. Mention actual column names and numbers. Keep it concise.
"""

def generate_report(
    original_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    schema: list,
    quality: dict,
    code: str,
    status: str
) -> str:
    prompt = PromptTemplate(
        input_variables=[
            "original_shape", "cleaned_shape",
            "schema", "quality", "code", "status"
        ],
        template=PROMPT
    )
    chain = prompt | llm
    result = chain.invoke({
        "original_shape": str(original_df.shape),
        "cleaned_shape": str(cleaned_df.shape),
        "schema": json.dumps(schema, indent=2),
        "quality": json.dumps(
            {k: v for k, v in quality.items() if k != "raw_checks"},
            indent=2
        ),
        "code": code,
        "status": status
    })
    return result.content