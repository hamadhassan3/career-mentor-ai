#!/usr/bin/env python3
"""
Cross-platform script to apply resume parser patch.
Handles both Windows and Unix-like systems (Mac, Linux).
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def detect_platform():
    """Detect the current platform."""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system in ['darwin', 'linux']:
        return 'unix'
    else:
        return 'unknown'

def find_resume_parser_package():
    """Find the resume parser package installation directory."""
    possible_locations = []
    
    # Check pip show output first (avoids importing broken module)
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'resume-parser'], 
                              capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if line.startswith('Location:'):
                location = line.split(':', 1)[1].strip()
                resume_parser_dir = Path(location) / 'resume_parser'
                if resume_parser_dir.exists():
                    possible_locations.append(resume_parser_dir)
    except Exception:
        pass
    
    # Check site-packages directories
    try:
        import site
        for site_dir in site.getsitepackages():
            resume_parser_dir = Path(site_dir) / 'resume_parser'
            if resume_parser_dir.exists():
                possible_locations.append(resume_parser_dir)
    except Exception:
        pass
    
    # Try to import and get the module path (only if other methods failed)
    if not possible_locations:
        try:
            import resume_parser
            module_path = Path(resume_parser.__file__).parent
            possible_locations.append(module_path)
        except Exception:
            pass
    
    # Return the first valid location found
    for location in possible_locations:
        resumeparse_file = location / 'resumeparse.py'
        if resumeparse_file.exists():
            return location
    
    return None

def backup_original_file(target_file):
    """Create a backup of the original file."""
    backup_file = target_file.with_suffix('.py.backup')
    if not backup_file.exists():
        shutil.copy2(target_file, backup_file)
        print(f"Created backup: {backup_file}")
    else:
        print(f"Backup already exists: {backup_file}")

def apply_patch():
    """Apply the resume parser patch."""
    print(f"Running on {detect_platform()} platform")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    patch_file = script_dir / 'resume-parser-patch.txt'
    
    if not patch_file.exists():
        print(f"Error: Patch file not found: {patch_file}")
        return False
    
    # Find the resume parser installation
    resume_parser_dir = find_resume_parser_package()
    if not resume_parser_dir:
        print("Error: Could not locate resume_parser package installation.")
        print("Please ensure resume-parser is installed via pip:")
        print("  pip install resume-parser")
        return False
    
    target_file = resume_parser_dir / 'resumeparse.py'
    print(f"Found resume parser at: {resume_parser_dir}")
    print(f"Target file: {target_file}")
    
    if not target_file.exists():
        print(f"Error: Target file does not exist: {target_file}")
        return False
    
    # Create backup
    backup_original_file(target_file)
    
    # Read the patch content (skip the first line which is a Jupyter cell marker)
    try:
        with open(patch_file, 'r', encoding='utf-8') as f:
            patch_lines = f.readlines()
        
        # Skip the first line (%%writefile command) and extract the actual Python code
        python_code_lines = []
        skip_jupyter_commands = True
        
        for line in patch_lines:
            if skip_jupyter_commands and (line.startswith('#') or line.strip() == ''):
                continue
            elif line.startswith('from __future__'):
                skip_jupyter_commands = False
                python_code_lines.append(line)
            elif not skip_jupyter_commands:
                python_code_lines.append(line)
        
        patched_content = ''.join(python_code_lines)
        
        # Apply the patch
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        print(f"✓ Successfully applied patch to {target_file}")
        
        # Copy required data files to the package directory
        copy_data_files(script_dir, resume_parser_dir)
        
        return True
        
    except Exception as e:
        print(f"Error applying patch: {e}")
        return False

def copy_data_files(script_dir, resume_parser_dir):
    """Copy required data files to the resume parser directory."""
    data_files = [
        'titles_combined.txt',
        'LINKEDIN_SKILLS_ORIGINAL.txt',
        'world-universities.csv'
    ]
    
    # Look for data files in common locations
    search_dirs = [
        script_dir,
        script_dir / 'data',
        script_dir / 'scripts' / 'data',
        script_dir.parent / 'data'
    ]
    
    for data_file in data_files:
        found = False
        for search_dir in search_dirs:
            source_file = search_dir / data_file
            if source_file.exists():
                target_file = resume_parser_dir / data_file
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"✓ Copied {data_file} to package directory")
                    found = True
                    break
                except Exception as e:
                    print(f"Warning: Could not copy {data_file}: {e}")
        
        if not found:
            print(f"Warning: Could not find required data file: {data_file}")
            print(f"Please ensure this file exists in the resume_parser package directory.")

def verify_patch():
    """Verify that the patch was applied correctly."""
    try:
        # Try to import the module to check for syntax errors
        import importlib
        if 'resume_parser.resumeparse' in sys.modules:
            importlib.reload(sys.modules['resume_parser.resumeparse'])
        else:
            import resume_parser.resumeparse
        
        print("✓ Patch verification successful - module imports correctly")
        return True
    except Exception as e:
        print(f"✗ Patch verification failed: {e}")
        return False

def main():
    """Main function."""
    print("Resume Parser Patch Application Script")
    print("=" * 40)
    
    if apply_patch():
        print("\nVerifying patch...")
        if verify_patch():
            print("\n✓ Resume parser patch applied successfully!")
            print("The resume parser should now work correctly with the required config files.")
        else:
            print("\n⚠ Patch applied but verification failed. Manual review may be needed.")
    else:
        print("\n✗ Failed to apply patch.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())