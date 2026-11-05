
from src.skill_matching import generate_skill_report


def get_learning_recommendations(df, job_role, user_skills):

    report = generate_skill_report(
        df,
        job_role,
        user_skills
    )

    missing_skills = report["missing_skills"]

    if not missing_skills:
        return df.iloc[0:0][
            ["skill", "skill_category", "importance"]
        ]

    role_data = df[
        df["job_role"].str.strip().str.lower()
        == job_role.strip().lower()
    ].copy()

    recommendations = role_data[
        role_data["skill"].str.strip().str.lower().isin(
            missing_skills
        )
    ]

    recommendations = recommendations.sort_values(
        by="importance",
        ascending=False
    )

    return recommendations[
        ["skill", "skill_category", "importance"]
    ]

