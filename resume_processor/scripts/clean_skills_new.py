import re
from difflib import SequenceMatcher

import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict

DATA_DIR = Path(__file__).parent / "data"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def normalize(text: str) -> str:
    return text.lower().strip()


# -------------------------------------------------
# TECHNOLOGY / IT SKILLS (using it_job_roles_skills.csv)
# -------------------------------------------------

def load_technology_skills(data_dir: Path = DATA_DIR) -> Tuple[List[str], Dict[str, dict]]:
    tech_df = pd.read_csv(data_dir / "it_job_roles_skills.csv", encoding='latin-1')

    all_predefined_skills = []
    skill_to_category = {}

    for _, row in tech_df.iterrows():
        job_title = row["Job Title"]
        skills_str = row["Skills"]
        
        # Split skills by comma and process each skill
        skills_list = [skill.strip() for skill in str(skills_str).split(",")]
        
        for skill in skills_list:
            if skill and len(skill.strip()) > 0:
                key = normalize(skill)
                
                all_predefined_skills.append(key)
                skill_to_category[key] = {
                    "standardized_name": skill,
                    "category": job_title,
                    "skill_type": "technical",
                    "hot_technology": False,  # Default value since not in new data
                    "onet_soc_code": ""  # Not available in new data
                }

    return all_predefined_skills, skill_to_category


# -------------------------------------------------
# SOFT SKILLS
# -------------------------------------------------

def load_soft_skills(data_dir: Path = DATA_DIR) -> Tuple[List[str], Dict[str, dict]]:
    soft_df = pd.read_csv(data_dir / "soft_skills.csv", encoding='latin-1')

    all_predefined_soft_skills = []
    soft_skill_to_category = {}

    for _, row in soft_df.iterrows():
        skill = row["Skill"]
        key = normalize(skill)

        all_predefined_soft_skills.append(key)
        soft_skill_to_category[key] = {
            "standardized_name": skill,
            "category": "Soft Skill",
            "skill_type": "soft"
        }

    return all_predefined_soft_skills, soft_skill_to_category


# -------------------------------------------------
# LANGUAGE SKILLS  (ISO-based, no categories)
# -------------------------------------------------

def load_language_skills(data_dir: Path = DATA_DIR):
    lang_df = pd.read_csv(data_dir / "languages.csv", encoding='latin-1')

    all_predefined_languages = []
    language_to_category = {}

    for _, row in lang_df.iterrows():
        language_name = row["Language"]
        iso_code = row["ISO_code"]

        key = normalize(language_name)

        all_predefined_languages.append(key)
        language_to_category[key] = {
            "standardized_name": language_name,
            "iso_code": iso_code,
            "category": "language",
            "skill_type": "language"
        }

    return all_predefined_languages, language_to_category

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_skill_match(user_skill, all_predefined_skills, skill_to_category, threshold=0.8):
    """Find the best matching predefined IT skill for a user skill"""
    user_skill_clean = re.sub(r'[^a-zA-Z0-9\s\.#+]', '', user_skill.lower().strip())
    
    if not user_skill_clean or len(user_skill_clean) < 2:
        return None
    
    # Skip very short skills that are likely false positives
    if len(user_skill_clean) <= 2 and user_skill_clean not in ['ai', 'ml', 'ui', 'ux', 'qa', 'ci', 'cd']:
        return None
    
    # Direct match first
    if user_skill_clean in all_predefined_skills:
        return skill_to_category[user_skill_clean]
    
    # Partial matches
    best_match = None
    best_score = 0
    
    for predefined_skill in all_predefined_skills:
        # Skip single character matches unless they're exact matches
        if len(predefined_skill) == 1 and predefined_skill != user_skill_clean:
            continue
            
        # Check if user skill contains the predefined skill or vice versa
        # if predefined_skill in user_skill_clean or user_skill_clean in predefined_skill:
        #     score = max(len(predefined_skill) / len(user_skill_clean), 
        #                len(user_skill_clean) / len(predefined_skill))
        #     if score > best_score and score >= threshold:
        #         best_score = score
        #         best_match = skill_to_category[predefined_skill]
        
        # Similarity matching
        sim_score = similarity(user_skill_clean, predefined_skill)
        if sim_score > best_score and sim_score >= threshold:
            best_score = sim_score
            best_match = skill_to_category[predefined_skill]
    
    return best_match

def find_best_soft_skill_match(user_skill, all_predefined_soft_skills, soft_skill_to_category, threshold=0.65):
    """Find the best matching predefined soft skill for a user skill"""
    user_skill_clean = re.sub(r'[^a-zA-Z0-9\s\-]', '', user_skill.lower().strip())
    
    if not user_skill_clean or len(user_skill_clean) < 3:  # Increased minimum length
        return None
    
    # Direct match first
    if user_skill_clean in all_predefined_soft_skills:
        return soft_skill_to_category[user_skill_clean]
    
    # Partial matches
    best_match = None
    best_score = 0
    
    for predefined_skill in all_predefined_soft_skills:
        # For soft skills, require better word boundary matching
        words_in_skill = predefined_skill.split()
        words_in_user = user_skill_clean.split()
        
        # Check for whole word matches
        if len(words_in_skill) == 1 and len(words_in_user) == 1:
            if predefined_skill == user_skill_clean:
                return soft_skill_to_category[predefined_skill]
        
        # Check if user skill contains the predefined skill or vice versa
        # if predefined_skill in user_skill_clean or user_skill_clean in predefined_skill:
        #     score = max(len(predefined_skill) / len(user_skill_clean), 
        #                len(user_skill_clean) / len(predefined_skill))
        #     if score > best_score and score >= threshold:
        #         best_score = score
        #         best_match = soft_skill_to_category[predefined_skill]
        
        # Similarity matching
        sim_score = similarity(user_skill_clean, predefined_skill)
        if sim_score > best_score and sim_score >= threshold:
            best_score = sim_score
            best_match = soft_skill_to_category[predefined_skill]
    
    return best_match

def find_best_language_match(user_skill, all_predefined_languages, language_to_category, threshold=0.9):
    """Find the best matching predefined language for a user skill"""
    user_skill_clean = re.sub(r'[^a-zA-Z0-9\s]', '', user_skill.lower().strip())
    
    if not user_skill_clean or len(user_skill_clean) < 3:  # Increased minimum length
        return None
    
    # Direct match first
    if user_skill_clean in all_predefined_languages:
        return language_to_category[user_skill_clean]
    
    # Partial matches - more strict for languages
    best_match = None
    best_score = 0
    
    for predefined_lang in all_predefined_languages:
        # Check exact word match (for multi-word languages)
        if predefined_lang == user_skill_clean:
            return language_to_category[predefined_lang]
        
        # Check if the language name is contained as a whole word
        if f" {predefined_lang} " in f" {user_skill_clean} " or \
           user_skill_clean.startswith(f"{predefined_lang} ") or \
           user_skill_clean.endswith(f" {predefined_lang}"):
            score = 1.0
            if score > best_score:
                best_score = score
                best_match = language_to_category[predefined_lang]
        
        # Similarity matching with higher threshold for languages
        sim_score = similarity(user_skill_clean, predefined_lang)
        if sim_score > best_score and sim_score >= threshold:
            best_score = sim_score
            best_match = language_to_category[predefined_lang]
    
    return best_match

def clean_skills(skills_list):
    """Clean and standardize a list of skills, separating IT, soft, and language skills"""

    if not isinstance(skills_list, list):
        return [], [], [], [], [], []
    
    cleaned_it_skills = []
    it_skill_categories = []
    cleaned_soft_skills = []
    soft_skill_categories = []
    cleaned_languages = []
    language_categories = []

    technology_skills, technology_skill_to_category = load_technology_skills(data_dir=DATA_DIR)
    soft_skills, soft_skill_to_category = load_soft_skills(data_dir=DATA_DIR)
    language_skills, language_skill_to_category = load_language_skills(data_dir=DATA_DIR)
    
    for skill in skills_list:
        if not skill or not isinstance(skill, str):
            continue
            
        # Skip very short or very long skills (likely noise)
        skill_stripped = skill.strip()
        if len(skill_stripped) < 2 or len(skill_stripped) > 50:
            continue
        
        # Skip obvious noise patterns
        if skill_stripped.lower() in ['ltd', 'inc', 'com', 'www', 'http', 'https', 'email', 'e-mail', 'mail']:
            continue
            
        # Skip single characters except known abbreviations
        if len(skill_stripped) == 1 and skill_stripped.lower() not in ['r', 'c']:
            continue
        
        # Try to match language first (as they are often misclassified)
        language_match = find_best_language_match(skill, language_skills, language_skill_to_category)
        if language_match:
            cleaned_languages.append(language_match['standardized_name'])
            language_categories.append(language_match['category'])
        else:
            # Try to match IT skill
            it_match = find_best_skill_match(skill, technology_skills, technology_skill_to_category)
            if it_match:
                cleaned_it_skills.append(it_match['standardized_name'])
                it_skill_categories.append(it_match['category'])
            else:
                # Try to match soft skill
                soft_match = find_best_soft_skill_match(skill, soft_skills, soft_skill_to_category)
                if soft_match:
                    cleaned_soft_skills.append(soft_match['standardized_name'])
                    soft_skill_categories.append(soft_match['category'])
    
    # Remove duplicates while preserving order
    seen_it = set()
    unique_it_skills = []
    unique_it_categories = []
    
    for skill, category in zip(cleaned_it_skills, it_skill_categories):
        if skill not in seen_it:
            seen_it.add(skill)
            unique_it_skills.append(skill)
            unique_it_categories.append(category)
    
    seen_soft = set()
    unique_soft_skills = []
    unique_soft_categories = []
    
    for skill, category in zip(cleaned_soft_skills, soft_skill_categories):
        if skill not in seen_soft:
            seen_soft.add(skill)
            unique_soft_skills.append(skill)
            unique_soft_categories.append(category)
    
    seen_lang = set()
    unique_languages = []
    unique_language_categories = []
    
    for lang, category in zip(cleaned_languages, language_categories):
        if lang not in seen_lang:
            seen_lang.add(lang)
            unique_languages.append(lang)
            unique_language_categories.append(category)
    
    return (unique_it_skills, unique_it_categories, 
            unique_soft_skills, unique_soft_categories,
            unique_languages, unique_language_categories)