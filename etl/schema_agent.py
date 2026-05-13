import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

PROMPT = """
You are a senior data engineer. Analyze this dataset sample and infer the schema.

Dataset sample:
{sample}

For each column, return a JSON array where each element has:
- "column": original column name
- "inferred_type": one of [integer, float, string, date, boolean, email, phone, currency, id]
- "intent": what this column represents in plain English (1 sentence)
- "issues": list of potential data quality issues you can already spot (empty list if none)

Respond ONLY with a valid JSON array. No explanation, no markdown, no backticks.
"""

def detect_schema(sample: str) -> list:
    prompt = PromptTemplate(input_variables=["sample"], template=PROMPT)
    chain = prompt | llm
    result = chain.invoke({"sample": sample})

    text = result.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [{"error": "Schema detection failed", "raw": text}]