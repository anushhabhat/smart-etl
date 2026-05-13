import pandas as pd

def load_file(file) -> pd.DataFrame:
    name = file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(file, encoding="utf-8", on_bad_lines="skip")
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        raise ValueError("Only CSV and Excel files are supported.")
    return df

def get_sample(df: pd.DataFrame, rows: int = 5) -> str:
    sample = df.head(rows).to_string(index=False)
    dtypes = df.dtypes.to_string()
    shape = f"Shape: {df.shape[0]} rows x {df.shape[1]} columns"
    nulls = df.isnull().sum().to_string()
    return f"{shape}\n\nColumn types:\n{dtypes}\n\nNull counts:\n{nulls}\n\nSample rows:\n{sample}"