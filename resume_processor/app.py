import json
import os
import tempfile
from flask import Flask, request, jsonify
import datetime
import numpy as np
from pathlib import Path

# Import utilities from scripts folder
from scripts.extract_resume import safe_parse_resume_from_file
from scripts.clean_skills_new import clean_skills, load_technology_skills, load_soft_skills, load_language_skills
from scripts.clean_designations_new import clean_designations, load_occupation_titles
from scripts.extract_occupations_new import get_matching_occupations
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
    return jsonify(skills)

@app.route('/skills/languages', methods=['GET'])
def get_languages():
    return jsonify(languages)

@app.route('/skills/soft', methods=['GET'])
def get_soft_skills():
    return jsonify(soft_skills_list)


@app.route("/predict_next_skill", methods=["POST"])
def predict_next_skill():
    """Predict single best next skill using XGBoost model"""
    try:
        import pandas as pd
        import pickle
        import xgboost as xgb
        
        data = request.json
        it_skills = set(data.get("it_skill_categories", []))
        soft_skills = set(data.get("soft_skills", []))
        profession = data.get("desired_designation", "")
        
        # Normalization function (same as in training)
        def normalize_skill(skill):
            return skill.lower().strip().replace(" ", "_")
        
        # Load single skill model
        try:
            with open("./model/single_skill_xgboost.pkl", 'rb') as f:
                model_data = pickle.load(f)
                
            xgb_model = model_data['xgboost_model']
            label_encoder = model_data['label_encoder']
            feature_columns = model_data['feature_columns']
            all_skills = set(model_data['all_skills'])
            all_soft_skills = set(model_data['all_soft_skills'])
            all_professions = set(model_data['all_professions'])
            
        except FileNotFoundError:
            return jsonify({"error": "Single skill model not found. Please train the model first."}), 500
        
        # Create feature vector
        features = {}
        
        # IT skill features
        for skill in sorted(all_skills):
            features[f"has_it_{skill}"] = 1 if skill in it_skills else 0
            
        # Soft skill features  
        for skill in sorted(all_soft_skills):
            features[f"has_soft_{skill}"] = 1 if skill in soft_skills else 0
            
        # Profession features
        for prof in sorted(all_professions):
            features[f"prof_{prof}"] = 1 if prof == profession else 0
            
        # Count features
        features["it_skill_count"] = len(it_skills)
        features["soft_skill_count"] = len(soft_skills)
        features["total_skill_count"] = len(it_skills) + len(soft_skills)
        
        # Add interaction features (simplified)
        prof_col = f"prof_{profession}"
        for skill in it_skills:
            it_col = f"has_it_{skill}"
            interaction_name = f"int_{prof_col}_{it_col}"
            if interaction_name in feature_columns:
                features[interaction_name] = 1
        
        # Create DataFrame with same columns as training data
        feature_df = pd.DataFrame([features])
        
        # Ensure all columns exist
        for col in feature_columns:
            if col not in feature_df.columns:
                feature_df[col] = 0
                
        # Reorder columns to match training data
        feature_df = feature_df[feature_columns]
        
        # Predict
        dtest_single = xgb.DMatrix(feature_df)
        probabilities = xgb_model.predict(dtest_single)[0]
        
        # Get all predictions and sort by probability
        sorted_indices = np.argsort(probabilities)[::-1]
        all_skills = label_encoder.inverse_transform(sorted_indices)
        all_probs = probabilities[sorted_indices]
        
        # Filter out current skills
        current_skills_normalized = set()
        for skill in list(it_skills) + list(soft_skills):
            # Add various normalizations to catch different formats
            current_skills_normalized.add(f"IT_{normalize_skill(skill)}")
            current_skills_normalized.add(f"SOFT_{normalize_skill(skill)}")
            current_skills_normalized.add(f"IT_{skill.upper().replace(' ', '_')}")
            current_skills_normalized.add(f"SOFT_{skill.upper().replace(' ', '_')}")
        
        # Get top NEW skills (excluding current ones)
        new_predictions = []
        for skill, prob in zip(all_skills, all_probs):
            if skill not in current_skills_normalized:
                skill_clean = skill.replace('IT_', '').replace('SOFT_', '').replace('_', ' ')
                skill_type = 'IT' if skill.startswith('IT_') else 'Soft'
                new_predictions.append({
                    "skill": skill_clean,
                    "type": skill_type,
                    "confidence": float(prob)
                })
                if len(new_predictions) >= 3:  # Get top 3 NEW skills
                    break
        
        predictions = new_predictions
        
        return jsonify({
            "best_next_skill": predictions[0] if predictions else None,
            "top_3_skills": predictions,
            "note": "Predictions exclude skills you already have"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        # Convert predictions to readable labels with dynamic thresholding
        # -----------------------------
        def get_profession_based_threshold(pred_scores, base_threshold=0.005):
            """Dynamic threshold based on prediction confidence - fixed for actual model output"""
            max_score = np.max(pred_scores)
            if max_score > 0.2:  # High confidence (top 20%)
                return base_threshold * 0.5  # Lower threshold 
            elif max_score > 0.05:  # Medium confidence 
                return base_threshold
            else:
                return base_threshold * 2.0  # Higher threshold for uncertain predictions

        it_threshold = get_profession_based_threshold(it_pred[0], base_threshold=0.005)
        soft_threshold = get_profession_based_threshold(soft_pred[0], base_threshold=0.005)

        # EXCLUDE CURRENT SKILLS - Get current skill indices to exclude
        current_it_indices = set()
        current_soft_indices = set()
        
        for skill in it_skills_norm:
            idx = it_tokenizer.word_index.get(skill)
            if idx:
                current_it_indices.add(idx)
                
        for skill in soft_skills_norm:
            idx = soft_tokenizer.word_index.get(skill)
            if idx:
                current_soft_indices.add(idx)

        # Get predictions above threshold, EXCLUDING current skills
        predicted_it_with_scores = [
            (it_index_word[i], prob)
            for i, prob in enumerate(it_pred[0])
            if prob > it_threshold and i in it_index_word and i not in current_it_indices
        ]
        
        predicted_soft_with_scores = [
            (soft_index_word[i], prob)
            for i, prob in enumerate(soft_pred[0])
            if prob > soft_threshold and i in soft_index_word and i not in current_soft_indices
        ]

        # Sort by confidence and limit results
        predicted_it_with_scores.sort(key=lambda x: x[1], reverse=True)
        predicted_soft_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        predicted_it = [skill for skill, _ in predicted_it_with_scores[:10]]  # Top 10 NEW skills
        predicted_soft = [skill for skill, _ in predicted_soft_with_scores[:8]]  # Top 8 NEW skills

        return jsonify({
            "predicted_next_it_skills": predicted_it,
            "predicted_next_soft_skills": predicted_soft,
            "note": "Predictions exclude skills you already have"
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
            'created_at': datetime.datetime.now().isoformat(),
        }

        return jsonify(resume_data), 200

    except Exception as e:
        logging.exception("Error processing resume upload")
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Cleanup: Remove the temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)