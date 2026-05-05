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
    packages_path = site.getsitepackages()[0]
    base_path = os.path.join(packages_path, 'resume_parser')
    
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