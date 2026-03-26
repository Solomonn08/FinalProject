#!/usr/bin/env python3
"""
Script to compile translation files from .po to .mo format
"""
import os
import subprocess
import sys

def compile_translations():
    """Compile .po files to .mo files"""
    translations_dir = "translations"
    
    if not os.path.exists(translations_dir):
        print(f"Translations directory '{translations_dir}' not found!")
        return False
    
    # Check if pybabel is available
    try:
        result = subprocess.run(['pybabel', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("pybabel command not found. Please install Babel:")
            print("pip install Babel")
            return False
    except FileNotFoundError:
        print("pybabel command not found. Please install Babel:")
        print("pip install Babel")
        return False
    
    # Compile each language
    languages = ['ru', 'tk']
    
    for lang in languages:
        po_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_file):
            print(f"Compiling {lang} translations...")
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(mo_file), exist_ok=True)
                
                # Compile .po to .mo
                result = subprocess.run(['pybabel', 'compile', '-d', translations_dir, '-l', lang], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✓ Successfully compiled {lang} translations")
                else:
                    print(f"✗ Error compiling {lang} translations:")
                    print(result.stderr)
                    return False
                    
            except Exception as e:
                print(f"✗ Error compiling {lang} translations: {e}")
                return False
        else:
            print(f"✗ .po file not found for {lang}: {po_file}")
            return False
    
    print("\n✓ All translations compiled successfully!")
    return True

if __name__ == "__main__":
    success = compile_translations()
    sys.exit(0 if success else 1)