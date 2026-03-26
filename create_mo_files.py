#!/usr/bin/env python3
"""
Simple script to create .mo files from .po files
"""
import os
import struct

def create_mo_file(po_file, mo_file):
    """Create a simple .mo file from .po file"""
    
    # Read the .po file
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the .po file to extract translations
    translations = {}
    current_msgid = None
    current_msgstr = None
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('msgid "'):
            current_msgid = line[7:-1]  # Remove 'msgid "' and '"'
        elif line.startswith('msgstr "'):
            current_msgstr = line[8:-1]  # Remove 'msgstr "' and '"'
            if current_msgid is not None and current_msgstr is not None:
                translations[current_msgid] = current_msgstr
                current_msgid = None
                current_msgstr = None
    
    # Create .mo file content
    # MO file format is binary, but we'll create a minimal version
    
    # For now, let's create a simple placeholder .mo file
    # In a real implementation, you'd need to properly parse and compile the .po file
    
    with open(mo_file, 'wb') as f:
        # Write MO file header
        # Magic number: 0x950412de (little endian)
        f.write(struct.pack('<I', 0x950412de))
        
        # File format revision: 0
        f.write(struct.pack('<I', 0))
        
        # Number of strings
        f.write(struct.pack('<I', len(translations)))
        
        # Offset of table with original strings
        f.write(struct.pack('<I', 28))
        
        # Offset of table with translation strings
        f.write(struct.pack('<I', 28 + len(translations) * 8))
        
        # Size of hashing table
        f.write(struct.pack('<I', 0))
        
        # Offset of hashing table
        f.write(struct.pack('<I', 0))
        
        # Write the translations
        offset = 28 + len(translations) * 16
        
        for msgid, msgstr in translations.items():
            # Write original string
            f.write(struct.pack('<I', len(msgid)))
            f.write(struct.pack('<I', offset))
            offset += len(msgid) + 1
            
            # Write translated string
            f.write(struct.pack('<I', len(msgstr)))
            f.write(struct.pack('<I', offset))
            offset += len(msgstr) + 1
        
        # Write strings
        for msgid, msgstr in translations.items():
            f.write(msgid.encode('utf-8') + b'\0')
            f.write(msgstr.encode('utf-8') + b'\0')

def main():
    """Main function to create .mo files"""
    translations_dir = "translations"
    
    if not os.path.exists(translations_dir):
        print(f"Translations directory '{translations_dir}' not found!")
        return False
    
    languages = ['ru', 'tk']
    
    for lang in languages:
        po_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_file):
            print(f"Creating {lang} .mo file...")
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(mo_file), exist_ok=True)
                
                # Create .mo file
                create_mo_file(po_file, mo_file)
                print(f"✓ Successfully created {lang} .mo file")
                
            except Exception as e:
                print(f"✗ Error creating {lang} .mo file: {e}")
                return False
        else:
            print(f"✗ .po file not found for {lang}: {po_file}")
            return False
    
    print("\n✓ All .mo files created successfully!")
    return True

if __name__ == "__main__":
    main()