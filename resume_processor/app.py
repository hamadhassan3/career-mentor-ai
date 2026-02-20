import os
import tempfile
from flask import Flask, request, jsonify
import datetime

# Import utilities from scripts folder
from scripts.extract_resume import safe_parse_resume_from_file
from scripts.clean_skills import clean_skills
from scripts.clean_designations import clean_designations

import logging
logging.basicConfig(level=logging.DEBUG)


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
    app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=False, threaded=False)