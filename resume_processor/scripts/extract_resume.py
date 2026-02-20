import tempfile
import os
from resume_parser import resumeparse


def clean_unicode_text(text):
    if not isinstance(text, str):
        text = str(text)
    cleaned = text.encode('utf-8', errors='ignore').decode('utf-8')
    cleaned = cleaned.replace('\\ud83d', '').replace('\\udcxx', '')
    return cleaned

def safe_parse_resume_from_file(file_path, idx=0):
    """
    Processes a PDF/DOCX/TXT file path directly using resume_parser.
    """
    try:
        # resumeparse.read_file handles extraction based on file extension
        parsed = resumeparse.read_file(file_path)
        
        if not isinstance(parsed, dict):
            raise ValueError("Parser returned invalid data type")

        # Clean the extracted data
        cleaned_parsed = {}
        for key, value in parsed.items():
            if value is not None:
                if isinstance(value, list):
                    cleaned_list = [
                        (clean_unicode_text(v) if isinstance(v, str) else v)
                        for v in value if v is not None
                    ]
                    cleaned_parsed[key] = cleaned_list
                elif isinstance(value, str):
                    cleaned_parsed[key] = clean_unicode_text(value)
                else:
                    cleaned_parsed[key] = value
        return cleaned_parsed

    except Exception as e:
        print(f"Error parsing resume file at index {idx}: {e}")
        return None

def safe_parse_resume(text, idx):
    temp_file_path = None
    try:
        clean_text = clean_unicode_text(text)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8', errors='ignore') as temp_file:
            temp_file.write(clean_text)
            temp_file_path = temp_file.name

        parsed = resumeparse.read_file(temp_file_path)
        if not isinstance(parsed, dict):
            raise ValueError("Parser returned invalid data type")

        cleaned_parsed = {}
        for key, value in parsed.items():
            if value is not None:
                if isinstance(value, list):
                    cleaned_list = []
                    for v in value:
                        if v is not None:
                            cleaned_list.append(clean_unicode_text(v) if isinstance(v, str) else v)
                    cleaned_parsed[key] = cleaned_list
                elif isinstance(value, str):
                    cleaned_parsed[key] = clean_unicode_text(value)
                else:
                    cleaned_parsed[key] = value

        return cleaned_parsed

    except Exception as e:
        print(f"Error parsing resume at index {idx}: {e}")
        error_key = f"{type(e).__name__}: {str(e)[:50]}"
        return None

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass