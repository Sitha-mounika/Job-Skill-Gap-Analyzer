

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "job_skills.csv"


def load_job_data():
    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "job_role",
        "skill",
        "skill_category",
        "importance"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing CSV columns: {missing_columns}"
        )

    df = df.dropna(subset=["job_role", "skill"]).copy()

    for column in ["job_role", "skill", "skill_category"]:
        df[column] = df[column].fillna("").astype(str).str.strip()

    df["importance"] = pd.to_numeric(
        df["importance"], errors="coerce"
    ).fillna(1).astype(int)

    df = df.drop_duplicates(
        subset=["job_role", "skill"],
        keep="first"
    )

    return df


if __name__ == "__main__":
    data = load_job_data()

    print("Dataset loaded successfully!")
    print(data.head())
    print("\nDataset shape:", data.shape)
    print("\nAvailable roles:")
    print(data["job_role"].unique())
