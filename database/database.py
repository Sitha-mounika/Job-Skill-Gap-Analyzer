
import sqlite3
from pathlib import Path
import pandas as pd
import json

from src.data_cleaning import load_job_data

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "job_skill_analyzer.db"


def create_connection():
    return sqlite3.connect(DB_PATH)


def create_tables(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS job_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_role TEXT NOT NULL,
            skill TEXT NOT NULL,
            skill_category TEXT,
            importance INTEGER,
            UNIQUE(job_role, skill)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_role TEXT NOT NULL,
            skill_coverage REAL,
            matching_skills TEXT,
            missing_skills TEXT,
            extra_skills TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()


def insert_job_data(connection):
    df = load_job_data()

    # Refresh only the reference skills table.
    connection.execute("DELETE FROM job_skills")

    df.to_sql(
        "job_skills",
        connection,
        if_exists="append",
        index=False
    )

    connection.commit()
    print("Job skills data inserted successfully!")


def load_job_data_from_db():
    connection = create_connection()

    try:
        query = """
            SELECT job_role, skill, skill_category, importance
            FROM job_skills
            ORDER BY job_role, importance DESC
        """
        return pd.read_sql_query(query, connection)

    finally:
        connection.close()


def get_job_roles():
    connection = create_connection()

    try:
        query = """
            SELECT DISTINCT job_role
            FROM job_skills
            ORDER BY job_role
        """
        return pd.read_sql_query(query, connection)

    finally:
        connection.close()


def save_analysis_report(report):
    connection = create_connection()

    try:
        connection.execute("""
            INSERT INTO analysis_history (
                job_role,
                skill_coverage,
                matching_skills,
                missing_skills,
                extra_skills
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            report["job_role"],
            report["skill_coverage"],
            json.dumps(report["matching_skills"]),
            json.dumps(report["missing_skills"]),
            json.dumps(report["extra_skills"])
        ))

        connection.commit()

    finally:
        connection.close()


def get_report_history():
    connection = create_connection()

    try:
        query = """
            SELECT
                id,
                job_role,
                skill_coverage,
                matching_skills,
                missing_skills,
                extra_skills,
                created_at
            FROM analysis_history
            ORDER BY created_at DESC, id DESC
        """

        return pd.read_sql_query(query, connection)

    finally:
        connection.close()


def delete_report(report_id):
    connection = create_connection()

    try:
        connection.execute(
            "DELETE FROM analysis_history WHERE id = ?",
            (report_id,)
        )
        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    connection = create_connection()

    try:
        create_tables(connection)
        insert_job_data(connection)
        print("\nDatabase initialized successfully!")

    finally:
        connection.close()



