import pandas as pd
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

PROMPT = """
You are a senior data engineer. Write Python Pandas code to clean this dataset.

Dataset info:
- Shape: {shape}
- Columns: {columns}

Schema (with inferred types and issues):
{schema}

Quality issues to fix:
{issues}

Write a Python function called `clean_dataframe(df)` that:
1. Fixes all identified quality issues
2. Standardizes column names (lowercase, underscores)
3. Converts columns to their correct types
4. Handles nulls appropriately for each column type
5. Removes duplicate rows
6. Returns the cleaned DataFrame

Rules:
- Only use pandas — no other libraries
- Handle errors gracefully with try/except
- Add a comment above each fix explaining what it does
- The function must work on the EXACT columns provided

Respond ONLY with the Python function. No explanation, no markdown, no backticks.
"""

def generate_cleaning_code(df: pd.DataFrame, schema: list, quality: dict) -> str:
    issues = quality.get("issues", [])
    prompt = PromptTemplate(
        input_variables=["shape", "columns", "schema", "issues"],
        template=PROMPT
    )
    chain = prompt | llm
    result = chain.invoke({
        "shape": str(df.shape),
        "columns": str(list(df.columns)),
        "schema": json.dumps(schema, indent=2),
        "issues": json.dumps(issues, indent=2)
    })

    code = result.content.strip()
    code = code.replace("```python", "").replace("```", "").strip()
    return code

def execute_cleaning_code(df: pd.DataFrame, code: str) -> tuple[pd.DataFrame, str]:
    local_vars = {"df": df.copy(), "pd": pd}
    try:
        exec(code, {"pd": pd}, local_vars)
        clean_fn = local_vars.get("clean_dataframe")
        if clean_fn is None:
            return df, "Error: clean_dataframe function not found in generated code."
        cleaned_df = clean_fn(df.copy())
        return cleaned_df, "success"
    except Exception as e:
        return df, f"Error executing generated code: {str(e)}"

def run_codegen(df: pd.DataFrame, schema: list, quality: dict) -> tuple[pd.DataFrame, str, str]:
    code = generate_cleaning_code(df, schema, quality)
    cleaned_df, status = execute_cleaning_code(df, code)
    return cleaned_df, code, status