
import pandas as pd


# --------------------------------------------------
# 1. NORMALIZE USER SKILLS
# --------------------------------------------------

def normalize_skills(skills):
    return {
        skill.strip().lower()
        for skill in skills
        if skill and skill.strip()
    }


# --------------------------------------------------
# 2. GET REQUIRED SKILLS FOR A JOB ROLE
# --------------------------------------------------

def get_required_skills(df, job_role):

    role_data = df[
        df["job_role"].str.strip().str.lower()
        == job_role.strip().lower()
    ]

    return set(
        role_data["skill"].str.strip().str.lower()
    )


# --------------------------------------------------
# 3. COMPARE USER SKILLS WITH REQUIRED SKILLS
# --------------------------------------------------

def compare_skills(user_skills, required_skills):

    matching_skills = user_skills.intersection(
        required_skills
    )

    missing_skills = required_skills.difference(
        user_skills
    )

    extra_skills = user_skills.difference(
        required_skills
    )

    return matching_skills, missing_skills, extra_skills


# --------------------------------------------------
# 4. CALCULATE BASIC SKILL COVERAGE
# --------------------------------------------------

def calculate_coverage(matching_skills, required_skills):

    if not required_skills:
        return 0

    coverage = (
        len(matching_skills) / len(required_skills)
    ) * 100

    return round(coverage, 2)


# --------------------------------------------------
# 5. NEW FEATURE: WEIGHTED SKILL COVERAGE
# --------------------------------------------------

def calculate_weighted_coverage(
    df,
    job_role,
    matching_skills
):

    role_data = df[
        df["job_role"].str.strip().str.lower()
        == job_role.strip().lower()
    ].copy()

    role_data["skill_normalized"] = (
        role_data["skill"].str.strip().str.lower()
    )

    role_data["importance"] = pd.to_numeric(
        role_data["importance"],
        errors="coerce"
    ).fillna(1).clip(lower=0)

    total_importance = role_data["importance"].sum()

    if total_importance == 0:
        return 0

    matching_importance = role_data[
        role_data["skill_normalized"].isin(matching_skills)
    ]["importance"].sum()

    weighted_coverage = (
        matching_importance / total_importance
    ) * 100

    return round(weighted_coverage, 2)


# --------------------------------------------------
# 6. GENERATE COMPLETE SKILL GAP REPORT
# --------------------------------------------------

def generate_skill_report(df, job_role, user_skills):

    required_skills = get_required_skills(
        df,
        job_role
    )

    if not required_skills:
        raise ValueError(
            f"Job role not found: {job_role}"
        )

    normalized_user_skills = normalize_skills(
        user_skills
    )

    matching, missing, extra = compare_skills(
        normalized_user_skills,
        required_skills
    )

    # Basic coverage
    coverage = calculate_coverage(
        matching,
        required_skills
    )

    # Weighted coverage
    weighted_coverage = calculate_weighted_coverage(
        df,
        job_role,
        matching
    )

    report = {
        "job_role": job_role,
        "total_required_skills": len(required_skills),
        "matching_skills": sorted(matching),
        "missing_skills": sorted(missing),
        "extra_skills": sorted(extra),
        "skill_coverage": coverage,
        "weighted_skill_coverage": weighted_coverage
    }

    return report


# --------------------------------------------------
# 7. TEST THE PROJECT
# --------------------------------------------------

if __name__ == "__main__":

    from src.data_cleaning import load_job_data

    print("Loading dataset...")

    df = load_job_data()

    user_skills = ["Python", "SQL", "Excel"]

    report = generate_skill_report(
        df,
        "Data Analyst",
        user_skills
    )

    print("\n========== SKILL GAP REPORT ==========")

    print("\nJob Role:")
    print(report["job_role"])

    print("\nTotal Required Skills:")
    print(report["total_required_skills"])

    print("\nBasic Skill Coverage:")
    print(str(report["skill_coverage"]) + "%")

    print("\nWeighted Skill Coverage:")
    print(str(report["weighted_skill_coverage"]) + "%")

    print("\nMatching Skills:")
    print(report["matching_skills"])

    print("\nMissing Skills:")
    print(report["missing_skills"])

    print("\nAdditional Skills:")
    print(report["extra_skills"])

    print("\n======================================")
