import pandas as pd
from pathlib import Path

def get_matching_occupations(file1_path=None, file2_path=None):
    """
    Extract job titles from it_job_roles_skills.csv as a list of dictionaries.
    The file1_path and file2_path parameters are kept for compatibility but ignored.

    Returns a list of dictionaries, each containing:
        - code: empty string (no codes in new data)
        - category: job title (used as category)
        - name: job title
    """

    # Get path relative to script location
    script_dir = Path(__file__).parent
    data_file = script_dir / "data" / "it_job_roles_skills.csv"
    
    # Load IT job roles data
    job_roles_df = pd.read_csv(data_file, dtype=str, encoding='latin-1')

    occupations = []

    for _, row in job_roles_df.iterrows():
        job_title = row["Job Title"]
        job_description = row["Job Description"]

        occupations.append({
            "code": "",  # No codes in the new data
            "category": job_title,  # Use job title as category
            "name": job_title,
            "description": job_description
        })

    return occupations

def main():
    matches = get_matching_occupations()

    for m in matches[:10]:
        print(m)

    print(f"Total occupations: {len(matches)}")

if __name__ == "__main__":
    main()