import pandas as pd
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

PROMPT = """
You are a senior data engineer. You have been given a dataset sample and the unique
values of every text column. Your job is to write Python Pandas code that standardizes
any inconsistencies you find.

Dataset shape: {shape}
Column names: {columns}

Unique values per text column:
{unique_values}

Sample rows:
{sample}

Look for ANY inconsistencies you can spot — do not limit yourself to a fixed list.
This includes but is not limited to:
- Same concept written differently (XL vs Extra Large)
- Inconsistent casing (active vs Active vs ACTIVE)
- Inconsistent formatting (in_stock vs in-stock vs "In Stock")
- Mixed abbreviations and full words
- Typos and near-duplicates
- Mixed units
- Anything else that looks inconsistent to a data engineer

Write a Python function called `normalize_dataframe(df)` that:
1. Fixes every inconsistency you find using .replace() or .map() or .apply()
2. Uses the most logical standard form for each group of inconsistent values
3. Only touches columns and values where you are confident about the normalization
4. Leaves ambiguous or unknown values unchanged
5. Returns the cleaned DataFrame

Rules:
- Only use pandas — no other libraries
- Add a comment above each normalization explaining what you found and what you chose
- Never hardcode row indices — use column-level operations only
- The function must be safe to run on the full dataset

Respond ONLY with the Python function. No explanation, no markdown, no backticks.
"""

def run_normalization(df: pd.DataFrame) -> tuple[pd.DataFrame, str, str]:
    # Build unique values profile for all text columns
    unique_values = {}
    for col in df.columns:
        if df[col].dtype == object:
            unique_values[col] = sorted(df[col].dropna().unique().tolist())[:60]

    prompt = PromptTemplate(
        input_variables=["shape", "columns", "unique_values", "sample"],
        template=PROMPT
    )
    chain = prompt | llm
    result = chain.invoke({
        "shape": str(df.shape),
        "columns": str(list(df.columns)),
        "unique_values": json.dumps(unique_values, indent=2),
        "sample": df.head(10).to_string(index=False)
    })

    code = result.content.strip().replace("```python", "").replace("```", "").strip()

    # Execute the generated code
    try:
        local_vars = {"df": df.copy(), "pd": pd}
        exec(code, {"pd": pd}, local_vars)
        normalize_fn = local_vars.get("normalize_dataframe")
        if normalize_fn is None:
            return df, code, "Error: normalize_dataframe function not found"
        normalized_df = normalize_fn(df.copy())
        return normalized_df, code, "success"
    except Exception as e:
        return df, code, f"Error: {str(e)}"