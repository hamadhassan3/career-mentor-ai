import re
from difflib import SequenceMatcher
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Dict

DATA_DIR = Path(__file__).parent / "data"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def normalize(text: str) -> str:
    return text.lower().strip()


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# -------------------------------------------------
# LOAD JOB TITLES FROM NEW DATA FILE
# -------------------------------------------------

def load_occupation_titles(data_dir: Path = DATA_DIR) -> Tuple[List[str], Dict[str, dict]]:
    """
    Loads job titles from it_job_roles_skills.csv
    """
    
    job_roles_df = pd.read_csv(data_dir / "it_job_roles_skills.csv", encoding='latin-1')

    all_titles = []
    title_lookup = {}

    for _, row in job_roles_df.iterrows():
        job_title = row["Job Title"]
        job_description = row["Job Description"]
        
        key = normalize(job_title)

        all_titles.append(key)
        title_lookup[key] = {
            "standardized_name": job_title,
            "code": "",  # No codes in new data
            "category": job_title,  # Use job title as category
            "description": job_description,
            "type": "designation"
        }

    return all_titles, title_lookup


# -------------------------------------------------
# MATCH DESIGNATION
# -------------------------------------------------

def find_best_designation_match(
    user_title: str,
    all_titles: List[str],
    title_lookup: Dict[str, dict],
    threshold: float = 0.80
):
    """
    Find best job title match for a resume designation.
    """

    user_clean = re.sub(r'[^a-zA-Z0-9\s\-\(\)]', '', user_title.lower().strip())

    if not user_clean or len(user_clean) < 3:
        return None

    # Direct match first
    if user_clean in all_titles:
        return title_lookup[user_clean]

    best_match = None
    best_score = 0

    for predefined in all_titles:

        # Containment check
        if predefined in user_clean or user_clean in predefined:
            score = max(
                len(predefined) / len(user_clean),
                len(user_clean) / len(predefined)
            )
            if score > best_score and score >= threshold:
                best_score = score
                best_match = title_lookup[predefined]

        # Similarity score
        sim_score = similarity(user_clean, predefined)
        if sim_score > best_score and sim_score >= threshold:
            best_score = sim_score
            best_match = title_lookup[predefined]

    return best_match


# -------------------------------------------------
# CLEAN DESIGNATIONS
# -------------------------------------------------

def clean_designations(designation_list: List[str]):
    """
    Clean and standardize resume designations using new data file.

    Returns:
        standardized_titles
        occupation_codes
        occupation_categories
    """

    if not isinstance(designation_list, list):
        return [], [], []

    all_titles, title_lookup = load_occupation_titles()

    cleaned_titles = []
    codes = []
    categories = []

    for title in designation_list:

        if not title or not isinstance(title, str):
            continue

        title_stripped = title.strip()

        # Skip noise
        if len(title_stripped) < 3 or len(title_stripped) > 80:
            continue

        if title_stripped.lower() in [
            "ltd", "inc", "company", "consultant", "self-employed"
        ]:
            continue

        match = find_best_designation_match(
            title,
            all_titles,
            title_lookup
        )

        if match:
            cleaned_titles.append(match["standardized_name"])
            codes.append(match["code"])
            categories.append(match["category"])

    # Deduplicate while preserving order
    seen = set()
    unique_titles = []
    unique_codes = []
    unique_categories = []

    for t, c, cat in zip(cleaned_titles, codes, categories):
        if t not in seen:
            seen.add(t)
            unique_titles.append(t)
            unique_codes.append(c)
            unique_categories.append(cat)

    return unique_titles, unique_codes, unique_categories

def main():
    designations = [
        "Senior Software Developer",
        "DevOps Eng",
        "System Analyst",
        "Network Administrator",
    ]

    titles, codes, categories = clean_designations(designations)

    print(titles)
    print(codes)
    print(categories)

if __name__ == "__main__":
    main()