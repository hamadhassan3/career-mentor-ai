import json
import os
import tempfile
from flask import Flask, request, jsonify
import datetime
import numpy as np
from pathlib import Path

# Import utilities from scripts folder
from scripts.extract_resume import safe_parse_resume_from_file
from scripts.clean_skills import clean_skills, load_technology_skills, load_soft_skills, load_language_skills
from scripts.clean_designations import clean_designations, load_occupation_titles
from scripts.extract_occupations import get_matching_occupations
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences

import logging
logging.basicConfig(level=logging.DEBUG)

# -----------------------------
# Paths
# -----------------------------
MODEL_PATH = "./model/lstm_model.keras"
IT_TOKENIZER_PATH = "./model/it_tokenizer.json"
SOFT_TOKENIZER_PATH = "./model/soft_tokenizer.json"
DES_TOKENIZER_PATH = "./model/designation_tokenizer.json"
CONFIG_PATH = "./model/config.json"
DATA_DIR = Path(__file__).parent / "scripts" / "data"

# -----------------------------
# Load Data using functions from scripts
# -----------------------------
try:
    all_tech_skills, _ = load_technology_skills(DATA_DIR)
    skills = sorted(list(set([skill['standardized_name'] for skill in _.values()])))
except Exception as e:
    skills = []
    logging.error(f"Could not load technology skills: {e}")

try:
    all_occupations, _ = load_occupation_titles(DATA_DIR)
    designations = sorted(list(set([occ['standardized_name'] for occ in _.values()])))
except Exception as e:
    designations = []
    logging.error(f"Could not load designations: {e}")

try:
    it_occupations = get_matching_occupations(
        DATA_DIR / "acs_it_occupations.csv",
        DATA_DIR / "anzsco_occupations.csv"
    )
    it_categories = sorted(list(set([occ["name"] for occ in it_occupations])))
except Exception as e:
    it_categories = []
    logging.error(f"Could not load IT categories: {e}")

try:
    all_languages, _ = load_language_skills(DATA_DIR)
    languages = sorted(list(set([lang['standardized_name'] for lang in _.values()])))
except Exception as e:
    languages = []
    logging.error(f"Could not load languages: {e}")

try:
    all_soft_skills, _ = load_soft_skills(DATA_DIR)
    soft_skills_list = sorted(list(set([skill['standardized_name'] for skill in _.values()])))
except Exception as e:
    soft_skills_list = []
    logging.error(f"Could not load soft skills: {e}")


# -----------------------------
# Load Model
# -----------------------------
model = load_model(MODEL_PATH)

# -----------------------------
# Load Tokenizers
# -----------------------------
with open(IT_TOKENIZER_PATH) as f:
    it_tokenizer = tokenizer_from_json(json.load(f))

with open(SOFT_TOKENIZER_PATH) as f:
    soft_tokenizer = tokenizer_from_json(json.load(f))

with open(DES_TOKENIZER_PATH) as f:
    des_tokenizer = tokenizer_from_json(json.load(f))

# Reverse lookup dictionaries
it_index_word = {v: k for k, v in it_tokenizer.word_index.items()}
soft_index_word = {v: k for k, v in soft_tokenizer.word_index.items()}

# -----------------------------
# Load Config (MAX LENGTHS)
# -----------------------------
with open(CONFIG_PATH) as f:
    config = json.load(f)

MAX_IT_LEN = config["MAX_IT_LEN"]
MAX_SOFT_LEN = config["MAX_SOFT_LEN"]

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "resume-processor-api",
    }), 200

@app.route('/skills/all', methods=['GET'])
def get_skills():
    return jsonify(skills)

@app.route('/designations', methods=['GET'])
def get_designations():
    return jsonify(designations)

@app.route('/skills/it', methods=['GET'])
def get_it_categories():
    return jsonify(it_categories)

@app.route('/skills/languages', methods=['GET'])
def get_languages():
    return jsonify(languages)

@app.route('/skills/soft', methods=['GET'])
def get_soft_skills():
    return jsonify(soft_skills_list)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        it_skills = data.get("it_skill_categories", [])
        soft_skills = data.get("soft_skills", [])
        designation = data.get("desired_designation", "")

        # -----------------------------
        # Normalization helpers (same as training)
        # -----------------------------
        def normalize_text(text: str):
            return text.lower().strip()

        def normalize_skill(skill: str):
            # convert multi-word skills into single tokens
            return normalize_text(skill).replace(" ", "_")

        # Normalize incoming data
        it_skills_norm = [normalize_skill(s) for s in it_skills if s.strip()]
        soft_skills_norm = [normalize_skill(s) for s in soft_skills if s.strip()]
        designation_norm = normalize_skill(designation)

        # Join into tokenizer-friendly strings
        it_text = " ".join(it_skills_norm)
        soft_text = " ".join(soft_skills_norm)

        # -----------------------------
        # Convert to sequences
        # -----------------------------
        it_seq = it_tokenizer.texts_to_sequences([it_text])
        soft_seq = soft_tokenizer.texts_to_sequences([soft_text])
        des_seq = des_tokenizer.texts_to_sequences([designation_norm])

        # Pad sequences
        X_it = pad_sequences(it_seq, maxlen=MAX_IT_LEN, padding="post")
        X_soft = pad_sequences(soft_seq, maxlen=MAX_SOFT_LEN, padding="post")
        X_des = np.array([[des_seq[0][0] - 1]]) if len(des_seq[0]) > 0 else np.array([[0]])

        # -----------------------------
        # Predict
        # -----------------------------
        it_pred, soft_pred = model.predict([X_it, X_soft, X_des])

        # -----------------------------
        # Convert predictions to readable labels
        # -----------------------------
        threshold = 0.5

        predicted_it = [
            it_index_word[i]
            for i, prob in enumerate(it_pred[0])
            if prob > threshold and i in it_index_word
        ]

        predicted_soft = [
            soft_index_word[i]
            for i, prob in enumerate(soft_pred[0])
            if prob > threshold and i in soft_index_word
        ]

        return jsonify({
            "predicted_next_it_skills": predicted_it,
            "predicted_next_soft_skills": predicted_soft
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/resumes/upload', methods=['POST'])
def process_resume():

    # 1. Validate file upload
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    temp_path = None
    try:
        # 2. Save uploaded PDF to a temporary file
        extension = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        # 3. Use utility to parse the file directly
        parsed_data = safe_parse_resume_from_file(temp_path)
        
        if not parsed_data:
            return jsonify({"error": "Failed to parse resume"}), 500

        # 4. Process Skills using clean_skills.py
        original_skills = parsed_data.get('skills', [])
        (
            it_skills, it_categories, 
            soft_skills, soft_categories, 
            languages, lang_categories
        ) = clean_skills(original_skills)

        # 5. Process Designations using clean_designations.py
        # Note: 'designition' is the key used by the parser library
        raw_designations = parsed_data.get('designition', [])
        cleaned_designations, _, _ = clean_designations(raw_designations)

        # 6. Construct the exact output format requested
        resume_data = {
            'total_exp': parsed_data.get('total_exp', 0),
            'university': parsed_data.get('university', []),
            'designition': cleaned_designations, 
            'degree': parsed_data.get('degree', []),
            'skills': it_skills,  # IT skills as main skills
            'companies_worked_at': parsed_data.get('Companies worked at', []),
            'skills_original': original_skills,
            'it_skills': it_skills,
            'it_skill_categories': it_categories,
            'soft_skills': soft_skills,
            'soft_skill_categories': soft_categories,
            'languages': languages,
            'language_categories': lang_categories,
        }

        return jsonify(resume_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Cleanup: Remove the temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)