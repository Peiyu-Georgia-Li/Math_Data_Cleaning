#!/usr/bin/env python3
"""
DOC to PDF Converter

This script converts Microsoft Word documents (DOC/DOCX) to PDF format
using Microsoft Word's "Save as PDF" functionality on macOS.

Requirements:
- macOS
- Microsoft Word installed
- Python 3.x
"""

import os
import subprocess
import argparse
from glob import glob


def doc_to_pdf_with_word(input_file, output_file=None):
    """
    Convert a DOC file to PDF using Microsoft Word on macOS
    
    Args:
        input_file (str): Path to the DOC/DOCX file
        output_file (str, optional): Path for the output PDF file. If None, 
                                     will use the same name with .pdf extension
    
    Returns:
        str: Path to the created PDF file or None if conversion failed
    """
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        return None

    # Get absolute paths
    input_file = os.path.abspath(input_file)
    # input_dir = "/Users/lipeiyu/Downloads/小学奥数7大板块题库/应用题专题题库/教师解析版/6-1-1 归一问题.教师版.doc"
    
    # If output file is not specified, use the same name with pdf extension
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + ".pdf"
    else:
        output_file = os.path.abspath(output_file)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # AppleScript to open the document in Word and save as PDF
    applescript = f'''
    tell application "Microsoft Word"
        set visible of application "Microsoft Word" to false
        open "{input_file}"
        set theDoc to active document
        save as theDoc file name "{output_file}" file format format PDF
        close theDoc saving no
        if (count of documents) is 0 then
            quit
        end if
    end tell
    '''
    
    try:
        # Execute the AppleScript
        subprocess.run(['osascript', '-e', applescript], check=True)
        print(f"Successfully converted {os.path.basename(input_file)} to {os.path.basename(output_file)}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        return None


def batch_convert(input_pattern, output_dir=None):
    """
    Convert multiple files matching a pattern
    
    Args:
        input_pattern (str): Glob pattern for input files
        output_dir (str, optional): Directory to save PDF files
    
    Returns:
        int: Number of successfully converted files
    """
    files = glob(input_pattern)
    if not files:
        print(f"No files found matching '{input_pattern}'")
        return 0
    
    success_count = 0
    for file_path in files:
        if output_dir:
            filename = os.path.basename(file_path)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{base_name}.pdf")
        else:
            output_path = None
        
        if doc_to_pdf_with_word(file_path, output_path):
            success_count += 1
    
    return success_count


def main():
    parser = argparse.ArgumentParser(description='Convert DOC/DOCX files to PDF using Microsoft Word')
    parser.add_argument('input', help='Input file path or glob pattern (e.g., "*.docx")')
    parser.add_argument('-o', '--output', help='Output file path (for single file) or directory (for multiple files)')
    parser.add_argument('-b', '--batch', action='store_true', help='Process multiple files')
    
    # Handle filenames with spaces by using raw args before argparse processing
    import sys
    if len(sys.argv) > 1:
        # Check if the first argument after script name contains spaces and is a valid path
        full_path = sys.argv[1]
        if ' ' in full_path and os.path.exists(full_path):
            # Handle case with space in filename but without quotes
            args = parser.parse_args([full_path] + sys.argv[2:])
        else:
            # Normal processing
            args = parser.parse_args()
    else:
        args = parser.parse_args()
    
    # Print input file for debugging
    print(f"Processing input file: {args.input}")
    
    if args.batch:
        if args.output and not os.path.isdir(args.output):
            os.makedirs(args.output)
        count = batch_convert(args.input, args.output)
        print(f"Converted {count} file(s) successfully.")
    else:
        doc_to_pdf_with_word(args.input, args.output)


if __name__ == '__main__':
    main()
