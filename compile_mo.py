#!/usr/bin/env python3
"""
Simple script to compile .mo files from .po files
"""
import os
import sys

def compile_mo_files():
    """Compile .mo files from .po files"""
    
    # Define the translation directories
    translation_dirs = [
        'translations/ru/LC_MESSAGES',
        'translations/tk/LC_MESSAGES'
    ]
    
    for lang_dir in translation_dirs:
        po_file = os.path.join(lang_dir, 'messages.po')
        mo_file = os.path.join(lang_dir, 'messages.mo')
        
        if os.path.exists(po_file):
            print(f"Compiling {po_file} to {mo_file}")
            
            try:
                # Try to compile using babel
                import babel.messages.pofile
                import babel.messages.mofile
                
                # Read the .po file
                with open(po_file, 'r', encoding='utf-8') as f:
                    catalog = babel.messages.pofile.read_po(f)
                
                # Write the .mo file
                with open(mo_file, 'wb') as f:
                    babel.messages.mofile.write_mo(f, catalog)
                
                print(f"Successfully created {mo_file}")
                
            except ImportError:
                print("Babel not available, trying alternative method")
                
                # Alternative: try to use msgfmt if available
                import subprocess
                try:
                    result = subprocess.run(['msgfmt', po_file, '-o', mo_file], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"Successfully created {mo_file}")
                    else:
                        print(f"Error: {result.stderr}")
                except FileNotFoundError:
                    print("msgfmt not available")
                    
            except Exception as e:
                print(f"Error creating {mo_file}: {e}")
        else:
            print(f"Warning: {po_file} not found")

if __name__ == '__main__':
    compile_mo_files()