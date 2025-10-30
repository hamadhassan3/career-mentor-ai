import tempfile
import os
import logging
import re
from difflib import SequenceMatcher

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from resume_parser import resumeparse

from .models import Resume
from .constants import IT_SKILLS, SOFT_SKILLS, LANGUAGE_SKILLS


class ResumeUploadView(APIView):
    """API view for uploading and processing resume PDFs."""
    parser_classes = (MultiPartParser, FormParser)

    def __init__(self):
        super().__init__()
        # Create flat lists for matching
        self.all_predefined_skills = []
        self.skill_to_category = {}

        for category, skills in IT_SKILLS.items():
            for skill in skills:
                self.all_predefined_skills.append(skill.lower())
                self.skill_to_category[skill.lower()] = {
                    'standardized_name': skill,
                    'category': category
                }

        self.all_predefined_soft_skills = []
        self.soft_skill_to_category = {}

        for category, skills in SOFT_SKILLS.items():
            for skill in skills:
                self.all_predefined_soft_skills.append(skill.lower())
                self.soft_skill_to_category[skill.lower()] = {
                    'standardized_name': skill,
                    'category': category
                }

        self.all_predefined_languages = []
        self.language_to_category = {}

        for category, languages in LANGUAGE_SKILLS.items():
            for language in languages:
                self.all_predefined_languages.append(language.lower())
                self.language_to_category[language.lower()] = {
                    'standardized_name': language,
                    'category': category
                }

    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def find_best_skill_match(self, user_skill, threshold=0.8):
        """Find the best matching predefined IT skill for a user skill"""
        user_skill_clean = re.sub(r'[^a-zA-Z0-9\s\.#+]', '', user_skill.lower().strip())
        
        if not user_skill_clean or len(user_skill_clean) < 2:
            return None
        
        if len(user_skill_clean) <= 2 and user_skill_clean not in ['ai', 'ml', 'ui', 'ux', 'qa', 'ci', 'cd']:
            return None
        
        # Direct match first
        if user_skill_clean in self.all_predefined_skills:
            return self.skill_to_category[user_skill_clean]
        
        # Partial matches
        best_match = None
        best_score = 0
        
        for predefined_skill in self.all_predefined_skills:
            if len(predefined_skill) == 1 and predefined_skill != user_skill_clean:
                continue
                
            if predefined_skill in user_skill_clean or user_skill_clean in predefined_skill:
                score = max(len(predefined_skill) / len(user_skill_clean), 
                           len(user_skill_clean) / len(predefined_skill))
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = self.skill_to_category[predefined_skill]
            
            sim_score = self.similarity(user_skill_clean, predefined_skill)
            if sim_score > best_score and sim_score >= threshold:
                best_score = sim_score
                best_match = self.skill_to_category[predefined_skill]
        
        return best_match

    def find_best_soft_skill_match(self, user_skill, threshold=0.75):
        """Find the best matching predefined soft skill for a user skill"""
        user_skill_clean = re.sub(r'[^a-zA-Z0-9\s\-]', '', user_skill.lower().strip())
        
        if not user_skill_clean or len(user_skill_clean) < 3:
            return None
        
        # Direct match first
        if user_skill_clean in self.all_predefined_soft_skills:
            return self.soft_skill_to_category[user_skill_clean]
        
        # Partial matches
        best_match = None
        best_score = 0
        
        for predefined_skill in self.all_predefined_soft_skills:
            if predefined_skill in user_skill_clean or user_skill_clean in predefined_skill:
                score = max(len(predefined_skill) / len(user_skill_clean), 
                           len(user_skill_clean) / len(predefined_skill))
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = self.soft_skill_to_category[predefined_skill]
            
            sim_score = self.similarity(user_skill_clean, predefined_skill)
            if sim_score > best_score and sim_score >= threshold:
                best_score = sim_score
                best_match = self.soft_skill_to_category[predefined_skill]
        
        return best_match

    def find_best_language_match(self, user_skill, threshold=0.85):
        """Find the best matching predefined language for a user skill"""
        user_skill_clean = re.sub(r'[^a-zA-Z0-9\s]', '', user_skill.lower().strip())
        
        if not user_skill_clean or len(user_skill_clean) < 3:
            return None
        
        # Direct match first
        if user_skill_clean in self.all_predefined_languages:
            return self.language_to_category[user_skill_clean]
        
        # Partial matches
        best_match = None
        best_score = 0
        
        for predefined_lang in self.all_predefined_languages:
            if predefined_lang == user_skill_clean:
                return self.language_to_category[predefined_lang]
            
            if f" {predefined_lang} " in f" {user_skill_clean} " or \
               user_skill_clean.startswith(f"{predefined_lang} ") or \
               user_skill_clean.endswith(f" {predefined_lang}"):
                score = 1.0
                if score > best_score:
                    best_score = score
                    best_match = self.language_to_category[predefined_lang]
            
            sim_score = self.similarity(user_skill_clean, predefined_lang)
            if sim_score > best_score and sim_score >= threshold:
                best_score = sim_score
                best_match = self.language_to_category[predefined_lang]
        
        return best_match

    def clean_skills(self, skills_list):
        """Clean and standardize a list of skills, separating IT, soft, and language skills"""
        if not isinstance(skills_list, list):
            return [], [], [], [], [], []
        
        cleaned_it_skills = []
        it_skill_categories = []
        cleaned_soft_skills = []
        soft_skill_categories = []
        cleaned_languages = []
        language_categories = []
        
        for skill in skills_list:
            if not skill or not isinstance(skill, str):
                continue
                
            skill_stripped = skill.strip()
            if len(skill_stripped) < 2 or len(skill_stripped) > 50:
                continue
            
            if skill_stripped.lower() in ['ltd', 'inc', 'com', 'www', 'http', 'https', 'email', 'e-mail', 'mail']:
                continue
                
            if len(skill_stripped) == 1 and skill_stripped.lower() not in ['r', 'c']:
                continue
            
            # Try to match language first
            language_match = self.find_best_language_match(skill)
            if language_match:
                cleaned_languages.append(language_match['standardized_name'])
                language_categories.append(language_match['category'])
            else:
                # Try to match IT skill
                it_match = self.find_best_skill_match(skill)
                if it_match:
                    cleaned_it_skills.append(it_match['standardized_name'])
                    it_skill_categories.append(it_match['category'])
                else:
                    # Try to match soft skill
                    soft_match = self.find_best_soft_skill_match(skill)
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

    def clean_unicode_text(self, text):
        """Clean unicode text from resumes"""
        if not isinstance(text, str):
            text = str(text)
        cleaned = text.encode('utf-8', errors='ignore').decode('utf-8')
        cleaned = cleaned.replace('\\ud83d', '').replace('\\udcxx', '')
        return cleaned

    def safe_parse_resume(self, file):
        """Safely parse resume using resumeparse library"""
        temp_file_path = None
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # Parse resume
            parsed = resumeparse.read_file(temp_file_path)
            if not isinstance(parsed, dict):
                raise ValueError("Parser returned invalid data type")

            # Clean parsed data
            cleaned_parsed = {}
            for key, value in parsed.items():
                if value is not None:
                    if isinstance(value, list):
                        cleaned_list = []
                        for v in value:
                            if v is not None:
                                cleaned_list.append(self.clean_unicode_text(v) if isinstance(v, str) else v)
                        cleaned_parsed[key] = cleaned_list
                    elif isinstance(value, str):
                        cleaned_parsed[key] = self.clean_unicode_text(value)
                    else:
                        cleaned_parsed[key] = value

            return cleaned_parsed

        except Exception as e:
            logging.error(f"Error parsing resume: {e}")
            return None

        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

    def post(self, request, *args, **kwargs):
        """Process uploaded resume PDF"""
        try:
            if 'file' not in request.FILES:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            
            if not file.name.lower().endswith('.pdf'):
                return Response({'error': 'Only PDF files are supported'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse resume
            parsed_data = self.safe_parse_resume(file)
            
            if not parsed_data:
                return Response({'error': 'Failed to parse resume'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Clean and categorize skills
            original_skills = parsed_data.get('skills', [])
            it_skills, it_categories, soft_skills, soft_categories, languages, lang_categories = self.clean_skills(original_skills)
            
            # Create resume data for saving (excluding PII)
            resume_data = {
                'total_exp': parsed_data.get('total_exp', 0),
                'university': parsed_data.get('university', []),
                'designition': parsed_data.get('designition', []),
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
            
            # Save to database
            resume = Resume.objects.create(**resume_data)
            
            # Return processed data
            response_data = {
                'id': resume.id,
                'total_exp': resume.total_exp,
                'university': resume.university,
                'designition': resume.designition,
                'degree': resume.degree,
                'skills': resume.skills,
                'companies_worked_at': resume.companies_worked_at,
                'skills_original': resume.skills_original,
                'it_skills': resume.it_skills,
                'it_skill_categories': resume.it_skill_categories,
                'soft_skills': resume.soft_skills,
                'soft_skill_categories': resume.soft_skill_categories,
                'languages': resume.languages,
                'language_categories': resume.language_categories,
                'created_at': resume.created_at,
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logging.error(f"Error processing resume: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ITSkillsView(APIView):
    """API view for fetching IT skills categories."""

    def get(self, request):
        """Return all IT skills categorized."""
        return Response(IT_SKILLS, status=status.HTTP_200_OK)


class SoftSkillsView(APIView):
    """API view for fetching soft skills categories."""

    def get(self, request):
        """Return all soft skills categorized."""
        return Response(SOFT_SKILLS, status=status.HTTP_200_OK)


class LanguageSkillsView(APIView):
    """API view for fetching language skills categories."""

    def get(self, request):
        """Return all language skills categorized."""
        return Response(LANGUAGE_SKILLS, status=status.HTTP_200_OK)


class AllSkillsView(APIView):
    """API view for fetching all skills categories."""

    def get(self, request):
        """Return all skills categorized by type."""
        return Response({
            'it_skills': IT_SKILLS,
            'soft_skills': SOFT_SKILLS,
            'language_skills': LANGUAGE_SKILLS
        }, status=status.HTTP_200_OK)
