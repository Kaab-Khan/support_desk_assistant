"""
Convert .docx files to .txt files for ingestion.

This script reads all .docx files from data/docs/ and creates
corresponding .txt files in the same directory.
"""

import os
from pathlib import Path
from docx import Document


def convert_docx_to_txt(docx_path: str, txt_path: str) -> bool:
    """
    Convert a single .docx file to .txt format.
    
    Args:
        docx_path: Path to input .docx file
        txt_path: Path to output .txt file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load the Word document
        doc = Document(docx_path)
        
        # Extract all paragraphs
        full_text = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:  # Only add non-empty paragraphs
                full_text.append(text)
        
        # Join paragraphs with double newlines
        content = "\n\n".join(full_text)
        
        # Write to .txt file
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ Converted: {os.path.basename(docx_path)} → {os.path.basename(txt_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Error converting {os.path.basename(docx_path)}: {e}")
        return False


def convert_all_docx_in_directory(directory: str) -> None:
    """
    Convert all .docx files in a directory to .txt files.
    
    Args:
        directory: Path to directory containing .docx files
    """
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return
    
    # Find all .docx files
    docx_files = [f for f in os.listdir(directory) if f.endswith(".docx")]
    
    if not docx_files:
        print(f"⚠️  No .docx files found in {directory}")
        return
    
    print(f"📁 Found {len(docx_files)} .docx file(s) in {directory}\n")
    
    # Convert each file
    success_count = 0
    for docx_filename in docx_files:
        docx_path = os.path.join(directory, docx_filename)
        
        # Create .txt filename (replace .docx with .txt)
        txt_filename = docx_filename.replace(".docx", ".txt")
        txt_path = os.path.join(directory, txt_filename)
        
        # Convert
        if convert_docx_to_txt(docx_path, txt_path):
            success_count += 1
    
    print(f"\n✨ Conversion complete: {success_count}/{len(docx_files)} files converted successfully")


def main():
    """Main execution function."""
    # Default docs directory
    docs_dir = "data/docs"
    
    print("=" * 60)
    print("📄 DOCX to TXT Converter")
    print("=" * 60)
    print(f"Converting files in: {docs_dir}\n")
    
    convert_all_docx_in_directory(docs_dir)
    
    print("\n" + "=" * 60)
    print("✅ Done! You can now run: python scripts/ingest_docs.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
