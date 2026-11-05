
import json
import streamlit as st
import pandas as pd

from database.database import (
    create_connection,
    create_tables,
    insert_job_data,
    load_job_data_from_db,
    save_analysis_report,
    get_report_history,
    delete_report
)

from src.skill_matching import generate_skill_report
from src.recommendation import get_learning_recommendations


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Job Skill Gap Analyzer",
    page_icon="🎯",
    layout="wide"
)


# ==================================================
# 2. CUSTOM CSS
# ==================================================

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #2563eb;
    }

    .subtitle {
        font-size: 16px;
        color: #94a3b8;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetric"] label {
        color: #475569 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #17365d !important;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. DATABASE INITIALIZATION
# ==================================================

try:
    connection = create_connection()

    create_tables(connection)

    count = connection.execute(
        "SELECT COUNT(*) FROM job_skills"
    ).fetchone()[0]

    connection.close()

    if count == 0:
        connection = create_connection()
        try:
            insert_job_data(connection)
        finally:
            connection.close()

    df = load_job_data_from_db()

    if df.empty:
        st.error("No job skill data found in the database.")
        st.stop()

except Exception as error:
    st.error(f"Database error: {error}")
    st.stop()


# ==================================================
# 4. SESSION STATE
# ==================================================

if "last_report" not in st.session_state:
    st.session_state.last_report = None

if "last_recommendations" not in st.session_state:
    st.session_state.last_recommendations = None

if "saved_report_key" not in st.session_state:
    st.session_state.saved_report_key = None


# ==================================================
# 5. HELPER FUNCTIONS
# ==================================================

def get_priority(importance):

    if importance >= 4:
        return "High"

    elif importance >= 3:
        return "Medium"

    return "Low"


def create_csv_report(report):

    rows = []

    for skill in report["matching_skills"]:
        rows.append({
            "Skill": skill,
            "Status": "Matching"
        })

    for skill in report["missing_skills"]:
        rows.append({
            "Skill": skill,
            "Status": "Missing"
        })

    for skill in report["extra_skills"]:
        rows.append({
            "Skill": skill,
            "Status": "Extra"
        })

    csv_df = pd.DataFrame(
        rows,
        columns=["Skill", "Status"]
    )

    return csv_df.to_csv(index=False).encode("utf-8")


def safe_json_list(value):

    try:
        result = json.loads(value)

        if isinstance(result, list):
            return result

        return []

    except (TypeError, json.JSONDecodeError):
        return []


# ==================================================
# 6. SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("🎯 Skill Analyzer")

st.sidebar.caption(
    "Your Career Skill Development Companion"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📊 Skill Analysis",
        "📚 Learning Roadmap",
        "📁 History"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Select a job role, enter your existing skills "
    "and discover the skills you need to develop."
)


# ==================================================
# 7. HOME PAGE
# ==================================================

if page == "🏠 Home":

    st.markdown(
        '<p class="main-title">🎯 Job Skill Gap Analyzer</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Understand your current skills '
        'and identify what you need to learn for your target career.</p>',
        unsafe_allow_html=True
    )

    st.divider()

    total_roles = df["job_role"].nunique()
    total_skills = df["skill"].nunique()
    total_records = len(df)

    st.subheader("📊 Project Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💼 Available Job Roles",
            total_roles
        )

    with col2:
        st.metric(
            "🎯 Unique Skills",
            total_skills
        )

    with col3:
        st.metric(
            "📁 Total Skill Records",
            total_records
        )

    st.divider()

    st.subheader("👋 Welcome!")

    st.write(
        """
        Job Skill Gap Analyzer helps candidates understand
        the difference between their current skills and the
        skills required for a selected job role.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 1. Select a Role")
        st.write("Choose your target job role.")

    with col2:
        st.markdown("### 2. Enter Your Skills")
        st.write("Select the skills you already know.")

    with col3:
        st.markdown("### 3. Analyze Your Gap")
        st.write("Find matching and missing skills.")

    st.divider()

    st.subheader("💼 Available Job Roles")

    role_list = sorted(
        df["job_role"].dropna().unique()
    )

    role_columns = st.columns(2)

    for index, role in enumerate(role_list):

        with role_columns[index % 2]:
            st.write(f"• {role}")

    st.divider()

    st.info(
        "Note: This project uses a sample skill dataset. "
        "Results depend on the skills and importance values "
        "provided in that dataset. They are not a live job-market "
        "assessment or a guarantee of job readiness."
    )


# ==================================================
# 8. SKILL ANALYSIS PAGE
# ==================================================

elif page == "📊 Skill Analysis":

    st.title("📊 Skill Gap Analysis")

    st.write(
        "Select your target job role and the skills you currently have."
    )

    st.divider()

    available_roles = sorted(
        df["job_role"].dropna().unique()
    )

    selected_role = st.selectbox(
        "Select Your Target Job Role",
        available_roles
    )

    available_skills = sorted(
        df["skill"].dropna().astype(str).str.strip().unique()
    )

    selected_skills = st.multiselect(
        "Select Your Current Skills",
        available_skills,
        placeholder="Search and select your skills..."
    )

    analyze_button = st.button(
        "🔍 Analyze My Skills",
        type="primary",
        use_container_width=True
    )

    if analyze_button:

        if not selected_skills:

            st.warning(
                "Please select at least one skill before analyzing."
            )

        else:

            try:

                report = generate_skill_report(
                    df,
                    selected_role,
                    selected_skills
                )

                recommendations = get_learning_recommendations(
                    df,
                    selected_role,
                    selected_skills
                )

                st.session_state.last_report = report

                st.session_state.last_recommendations = (
                    recommendations
                )

                st.session_state.saved_report_key = None

            except Exception as error:

                st.error(
                    f"Skill analysis failed: {error}"
                )

    # Display the latest analysis

    report = st.session_state.last_report

    if report is not None:

        st.divider()

        st.subheader("📈 Your Analysis Results")

        st.write(
            f"**Selected Job Role:** {report['job_role']}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Basic Skill Coverage",
                f"{report['skill_coverage']:.2f}%"
            )

        with col2:
            st.metric(
                "Matching Skills",
                len(report["matching_skills"])
            )

        with col3:
            st.metric(
                "Missing Skills",
                len(report["missing_skills"])
            )

        # BASIC SKILL COVERAGE

        st.divider()

        st.subheader("📊 Skill Coverage")

        coverage = float(report["skill_coverage"])

        coverage = max(0.0, min(100.0, coverage))

        st.progress(
            int(round(coverage))
        )

        st.write(
            f"**Your Basic Skill Coverage: {coverage:.2f}%**"
        )

        st.caption(
            "Coverage = Matching Skills / Total Required Skills × 100"
        )

        # MATCHING SKILLS

        st.divider()

        st.subheader("✅ Matching Skills")

        if report["matching_skills"]:

            for skill in report["matching_skills"]:
                st.write(f"✓ {skill}")

        else:

            st.info("No matching skills found.")

        # MISSING SKILLS

        st.subheader("❌ Missing Skills")

        if report["missing_skills"]:

            for skill in report["missing_skills"]:
                st.write(f"• {skill}")

        else:

            st.success(
                "You have all the listed required skills!"
            )

        # EXTRA SKILLS

        st.subheader("⭐ Additional Skills")

        if report["extra_skills"]:

            for skill in report["extra_skills"]:
                st.write(f"• {skill}")

        else:

            st.write(
                "No additional skills outside this role's requirements."
            )

        # SKILL IMPORTANCE TABLE

        st.divider()

        st.subheader("📌 Skill Importance Analysis")

        role_data = df[
            df["job_role"].str.strip().str.lower()
            == report["job_role"].strip().lower()
        ].copy()

        matching_set = {
            str(skill).strip().lower()
            for skill in report["matching_skills"]
        }

        role_data["Status"] = role_data["skill"].apply(
            lambda skill: (
                "Matching"
                if str(skill).strip().lower() in matching_set
                else "Missing"
            )
        )

        role_data["Priority"] = (
            role_data["importance"].apply(get_priority)
        )

        display_df = role_data[
            [
                "skill",
                "skill_category",
                "importance",
                "Status",
                "Priority"
            ]
        ].rename(
            columns={
                "skill": "Skill",
                "skill_category": "Category",
                "importance": "Importance"
            }
        )

        display_df = display_df.sort_values(
            by="Importance",
            ascending=False
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # PRIORITY RECOMMENDATIONS

        st.divider()

        st.subheader(
            "🎯 Priority-Based Skill Recommendations"
        )

        recommendations = (
            st.session_state.last_recommendations
        )

        if (
            recommendations is not None
            and not recommendations.empty
        ):

            recommendation_display = recommendations.copy()

            recommendation_display["Priority"] = (
                recommendation_display["importance"].apply(
                    get_priority
                )
            )

            recommendation_display = (
                recommendation_display.rename(
                    columns={
                        "skill": "Recommended Skill",
                        "skill_category": "Category",
                        "importance": "Importance"
                    }
                )
            )

            st.dataframe(
                recommendation_display,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No missing skills found for this role."
            )

        # DOWNLOAD CSV REPORT

        st.divider()

        st.subheader("📥 Download Your Report")

        csv_data = create_csv_report(report)

        st.download_button(
            label="⬇️ Download Skill Analysis CSV",
            data=csv_data,
            file_name="skill_gap_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )

        # SAVE REPORT TO HISTORY

        st.divider()

        if st.button(
            "💾 Save Analysis to History",
            use_container_width=True
        ):

            report_key = (
                report["job_role"],
                tuple(report["matching_skills"]),
                tuple(report["missing_skills"]),
                tuple(report["extra_skills"])
            )

            if (
                st.session_state.saved_report_key
                == report_key
            ):

                st.info(
                    "This analysis has already been saved."
                )

            else:

                try:

                    save_analysis_report(report)

                    st.session_state.saved_report_key = (
                        report_key
                    )

                    st.success(
                        "Analysis saved successfully!"
                    )

                except Exception as error:

                    st.error(
                        f"Could not save report: {error}"
                    )


# ==================================================
# 9. LEARNING ROADMAP PAGE
# ==================================================

elif page == "📚 Learning Roadmap":

    st.title("📚 Your Learning Roadmap")

    st.write(
        "Follow your recommended learning priorities "
        "to improve your skills for your target job role."
    )

    st.divider()

    report = st.session_state.last_report

    recommendations = (
        st.session_state.last_recommendations
    )

    if report is None:

        st.info(
            "Please complete a Skill Analysis first. "
            "Your learning roadmap will appear here."
        )

    else:

        st.subheader(
            f"Target Role: {report['job_role']}"
        )

        st.metric(
            "Current Skill Coverage",
            f"{report['skill_coverage']:.2f}%"
        )

        if (
            recommendations is not None
            and not recommendations.empty
        ):

            roadmap = recommendations.copy()

            roadmap["Priority"] = (
                roadmap["importance"].apply(get_priority)
            )

            roadmap = roadmap.sort_values(
                by="importance",
                ascending=False
            ).reset_index(drop=True)

            st.subheader("Your Recommended Learning Steps")

            for index, row in roadmap.iterrows():

                st.markdown(
                    f"### Step {index + 1}: {row['skill']}"
                )

                st.write(
                    f"**Category:** {row['skill_category']}"
                )

                st.write(
                    f"**Importance:** {row['importance']} / 5"
                )

                priority = row["Priority"]

                st.write(
                    f"**Priority:** {priority}"
                )

                if priority == "High":

                    st.warning(
                        "Focus on learning this skill first."
                    )

                elif priority == "Medium":

                    st.info(
                        "Learn this after high-priority skills."
                    )

                else:

                    st.success(
                        "Learn this as an additional improvement."
                    )

                st.divider()

        else:

            st.success(
                "No missing skills found for this job role."
            )


# ==================================================
# 10. HISTORY PAGE
# ==================================================

elif page == "📁 History":

    st.title("📁 Analysis History")

    st.write(
        "View and manage your previously saved skill analysis reports."
    )

    st.divider()

    try:

        history_df = get_report_history()

        if history_df.empty:

            st.info(
                "No saved reports yet. Complete a skill analysis "
                "and click Save Analysis to History."
            )

        else:

            st.metric(
                "Total Saved Reports",
                len(history_df)
            )

            st.subheader("Saved Reports")

            display_history = history_df[
                [
                    "id",
                    "job_role",
                    "skill_coverage",
                    "created_at"
                ]
            ].copy()

            display_history = display_history.rename(
                columns={
                    "id": "Report ID",
                    "job_role": "Job Role",
                    "skill_coverage": "Basic Coverage (%)",
                    "created_at": "Created At"
                }
            )

            st.dataframe(
                display_history,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("🔎 View Saved Report")

            selected_id = st.selectbox(
                "Select Report ID",
                history_df["id"].tolist()
            )

            selected_report = history_df[
                history_df["id"] == selected_id
            ].iloc[0]

            st.write(
                f"**Job Role:** {selected_report['job_role']}"
            )

            st.write(
                f"**Basic Coverage:** "
                f"{selected_report['skill_coverage']:.2f}%"
            )

            matching = safe_json_list(
                selected_report["matching_skills"]
            )

            missing = safe_json_list(
                selected_report["missing_skills"]
            )

            extra = safe_json_list(
                selected_report["extra_skills"]
            )

            st.write("**Matching Skills:**")

            st.write(
                ", ".join(matching) if matching else "None"
            )

            st.write("**Missing Skills:**")

            st.write(
                ", ".join(missing) if missing else "None"
            )

            st.write("**Additional Skills:**")

            st.write(
                ", ".join(extra) if extra else "None"
            )

            st.divider()

            st.subheader("🗑️ Delete Saved Report")

            confirm_delete = st.checkbox(
                f"Confirm deletion of report #{selected_id}"
            )

            if st.button(
                "Delete Selected Report",
                disabled=not confirm_delete
            ):

                try:

                    delete_report(int(selected_id))

                    st.success(
                        "Report deleted successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Could not delete report: {error}"
                    )

    except Exception as error:

        st.error(
            f"Could not load report history: {error}"
        )


# ==================================================
# 11. FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#94a3b8;">
        <p><b>🎯 Job Skill Gap Analyzer</b></p>
        <p>Built with Python | Pandas | SQLite | Streamlit</p>
        <p>Analyze Your Skills • Identify Your Gaps • Build Your Career</p>
    </div>
    """,
    unsafe_allow_html=True
)
