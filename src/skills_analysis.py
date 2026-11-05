
import pandas as pd
from src.data_cleaning import load_job_data


# Load the job skills dataset
def get_data():
    df = load_job_data()
    return df


# Find the most common skills across all job roles
def get_top_skills(df, limit=10):
    top_skills = (
        df.groupby("skill")["job_role"]
        .nunique()
        .reset_index(name="job_count")
        .sort_values(by="job_count", ascending=False)
    )

    return top_skills.head(limit)


# Get all required skills for a selected job role
def get_role_skills(df, job_role):
    role_data = df[
        df["job_role"].str.lower() == job_role.strip().lower()
    ]

    role_skills = role_data[
        ["skill", "skill_category", "importance"]
    ]

    return role_skills.sort_values(
        by="importance",
        ascending=False
    )


# Count the number of skills required for each job role
def get_role_skill_count(df):
    role_count = (
        df.groupby("job_role")["skill"]
        .nunique()
        .reset_index(name="total_skills")
        .sort_values(by="total_skills", ascending=False)
    )

    return role_count


# Analyze skills by category
def get_category_analysis(df):
    category_data = (
        df.groupby("skill_category")["skill"]
        .nunique()
        .reset_index(name="total_skills")
        .sort_values(by="total_skills", ascending=False)
    )

    return category_data


# Main program
if __name__ == "__main__":

    df = get_data()

    print("\n========== TOP DEMANDED SKILLS ==========")
    print(get_top_skills(df))

    print("\n========== DATA ANALYST SKILLS ==========")
    print(get_role_skills(df, "Data Analyst"))

    print("\n========== SKILLS BY JOB ROLE ==========")
    print(get_role_skill_count(df))

    print("\n========== SKILL CATEGORY ANALYSIS ==========")
    print(get_category_analysis(df))


