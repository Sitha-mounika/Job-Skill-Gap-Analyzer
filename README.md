# Job Skill Gap Analyzer

A Python-based application that helps users identify their existing skills, discover missing skills for a target job role, and build a prioritized learning roadmap.

## Project Overview

The Job Skill Gap Analyzer compares a user's current skills with the required skills for a selected job role. It identifies matching, missing, and additional skills and calculates basic skill coverage.

## Features

- Select from multiple job roles.
- Compare existing skills with required skills.
- Identify matching, missing, and extra skills.
- Calculate basic skill coverage percentage.
- Get prioritized learning recommendations.
- Download analysis reports as CSV.
- Save and manage previous reports.
- Store job skill data and analysis history using SQLite.
- Interactive application built with Streamlit.

## Technologies Used

- Python
- Pandas
- SQL
- SQLite
- Streamlit
- CSV

## Project Structure

```text
Job-Skill-Gap-Analyzer/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── job_skills.csv
├── database/
│   ├── __init__.py
│   └── database.py
└── src/
    ├── __init__.py
    ├── data_cleaning.py
    ├── skill_matching.py
    └── recommendation.py
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sitha-mounika/Job-Skill-Gap-Analyzer.git
```

### 2. Open the project folder

```bash
cd Job-Skill-Gap-Analyzer
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

## How to Use

1. Select your target job role.
2. Select your existing skills.
3. View matching, missing, and additional skills.
4. Check your basic skill coverage.
5. Explore the recommended learning roadmap.
6. Download or save your analysis report.
7. View previous reports in the History section.

## Supported Job Roles

- Data Analyst
- Business Analyst
- Data Scientist
- BI Developer
- Power BI Analyst
- Data Engineer
- Python Developer
- Software Developer
- Cloud Engineer
- Machine Learning Engineer

## Future Enhancements

- Resume skill extraction.
- NLP-based skill matching.
- Real-time job description analysis.
- Personalized learning resource recommendations.

## Author

**Mounika Sitha**

GitHub: https://github.com/Sitha-mounika

---

*Portfolio project demonstrating Python, data analysis, SQL, SQLite database integration, and Streamlit application development.*
