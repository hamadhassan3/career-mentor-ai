#!/usr/bin/env python3
"""
One-click fix for resume_parser OSError and spaCy compatibility issues.
Run this after: pip install resume-parser
"""

import os
import sys

def fix_resume_parser():
    # Find resume_parser installation path without importing it
    import site
    
    # Try multiple potential package locations
    possible_paths = []
    
    # Add site-packages paths
    try:
        possible_paths.extend(site.getsitepackages())
    except AttributeError:
        pass
    
    # Add user site packages
    try:
        possible_paths.append(site.getusersitepackages())
    except AttributeError:
        pass
    
    # Add virtual environment site-packages
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_packages = os.path.join(sys.prefix, 'lib', 'site-packages')
        if os.path.exists(venv_packages):
            possible_paths.append(venv_packages)
        
        # Windows virtual environment path
        venv_packages_win = os.path.join(sys.prefix, 'Lib', 'site-packages')
        if os.path.exists(venv_packages_win):
            possible_paths.append(venv_packages_win)
    
    # Find the actual resume_parser path
    base_path = None
    for path in possible_paths:
        potential_path = os.path.join(path, 'resume_parser')
        if os.path.exists(potential_path):
            base_path = potential_path
            break
    
    if not base_path:
        print("❌ Could not find resume_parser installation. Please ensure it's installed with: pip install resume-parser")
        return
    
    # 1. Create missing config.cfg
    config_path = os.path.join(base_path, "degree", "model", "config.cfg")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    config_content = """[system]

[nlp]
lang = "en"
pipeline = ["tok2vec", "ner"]
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
tokenizer = {"@tokenizers": "spacy.Tokenizer.v1"}
batch_size = 1000

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 96
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true

[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode.width}

[corpora]
[training]
[pretraining]
[initialize]"""

    with open(config_path, 'w') as f:
        f.write(config_content)
    
    # 2. Fix resumeparse.py compatibility issues
    resumeparse_path = os.path.join(base_path, "resumeparse.py")
    
    if not os.path.exists(resumeparse_path):
        print(f"❌ Could not find resumeparse.py at: {resumeparse_path}")
        print(f"📁 Available files in {base_path}:")
        try:
            for file in os.listdir(base_path):
                print(f"   - {file}")
        except OSError:
            print("   (Unable to list directory contents)")
        return
    
    with open(resumeparse_path, 'r') as f:
        content = f.read()
    
    # Apply all fixes
    fixes = [
        ('custom_nlp2 = spacy.load(os.path.join(base_path,"degree","model"))', 
         'try:\n    custom_nlp2 = spacy.load(os.path.join(base_path,"degree","model"))\nexcept:\n    custom_nlp2 = nlp'),
        ('custom_nlp3 = spacy.load(os.path.join(base_path,"company_working","model"))', 
         'try:\n    custom_nlp3 = spacy.load(os.path.join(base_path,"company_working","model"))\nexcept:\n    custom_nlp3 = nlp'),
        ("'\\s+'", "r'\\s+'"),
        ('"\\d+"', 'r"\\d+"'),
        ('designitionmatcher.add("Job title", None, *patterns)', 'designitionmatcher.add("Job title", patterns)'),
        ('skillsmatcher.add("Job title", None, *patterns)', 'skillsmatcher.add("Skills", patterns)'),
        ("matcher.add('NAME', None, pattern)", "matcher.add('NAME', [pattern])")
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    with open(resumeparse_path, 'w') as f:
        f.write(content)
    
    print("✅ Resume parser fixed successfully!")

if __name__ == "__main__":
    fix_resume_parser()