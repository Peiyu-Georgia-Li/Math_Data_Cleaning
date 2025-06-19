#!/usr/bin/env python3
"""
PDF to JSON Conversion Pipeline

This script automates the process of:
1. Converting PDF files to text using OCR (via read_pdf_with_ocr.py)
2. Parsing the extracted text into structured JSON (via simple_parser.py)

Usage:
    python run_pdf_to_json_pipeline.py
"""

import os
import subprocess
import glob
import time
import sys
from datetime import datetime

# Configuration
PDF_DIRECTORY = "/Users/lipeiyu/Downloads/小学奥数7大板块题库/应用题专题题库/教师解析版"
OCR_SCRIPT = "/Users/lipeiyu/Downloads/小学奥数7大板块题库/read_pdf_with_ocr.py"
PARSER_SCRIPT = "/Users/lipeiyu/Downloads/小学奥数7大板块题库/simple_parser.py"


def log_message(message, error=False):
    """Print a timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "[ERROR]" if error else "[INFO]"
    print(f"{prefix} {timestamp} - {message}")


def run_ocr(pdf_path):
    """Run the OCR script on a PDF file"""
    log_message(f"Starting OCR process for: {os.path.basename(pdf_path)}")
    try:
        result = subprocess.run(
            ["python", OCR_SCRIPT, pdf_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            log_message(f"OCR completed successfully")
            # The expected output file path from the OCR script
            base_name = os.path.splitext(pdf_path)[0]
            return f"{base_name}_extracted_text_pdf.txt"
        else:
            log_message(f"OCR failed with code {result.returncode}: {result.stderr}", error=True)
            return None
    except subprocess.CalledProcessError as e:
        log_message(f"OCR process error: {str(e)}", error=True)
        return None
    except Exception as e:
        log_message(f"Unexpected error during OCR: {str(e)}", error=True)
        return None


def run_parser(text_file_path):
    """Run the parser script on a text file"""
    log_message(f"Starting parser for: {os.path.basename(text_file_path)}")
    try:
        result = subprocess.run(
            ["python", PARSER_SCRIPT, text_file_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            log_message(f"Parsing completed successfully")
            # The expected JSON output file
            base_name = os.path.splitext(text_file_path)[0]
            return f"{base_name}.json"
        else:
            log_message(f"Parsing failed with code {result.returncode}: {result.stderr}", error=True)
            return None
    except subprocess.CalledProcessError as e:
        log_message(f"Parser process error: {str(e)}", error=True)
        return None
    except Exception as e:
        log_message(f"Unexpected error during parsing: {str(e)}", error=True)
        return None


def process_file(pdf_path):
    """Process a single PDF file through the entire pipeline"""
    log_message(f"Processing file: {os.path.basename(pdf_path)}")
    
    # Step 1: Run OCR to convert PDF to text
    text_file_path = run_ocr(pdf_path)
    if not text_file_path or not os.path.exists(text_file_path):
        log_message(f"OCR did not produce a valid text file for {pdf_path}", error=True)
        return False
    
    # Allow a small delay between processes
    time.sleep(1)
    
    # Step 2: Run parser to convert text to structured JSON
    json_file_path = run_parser(text_file_path)
    if not json_file_path or not os.path.exists(json_file_path):
        log_message(f"Parser did not produce a valid JSON file for {text_file_path}", error=True)
        return False
    
    log_message(f"Successfully converted {os.path.basename(pdf_path)} to {os.path.basename(json_file_path)}")
    return True


def main():
    """Main function to process all PDF files in the directory"""
    log_message("Starting PDF to JSON conversion pipeline")
    
    # Get all PDF files in the directory
    pdf_files = glob.glob(os.path.join(PDF_DIRECTORY, "*.pdf"))
    
    if not pdf_files:
        log_message("No PDF files found in the specified directory", error=True)
        return
    
    log_message(f"Found {len(pdf_files)} PDF files to process")
    
    # Track statistics
    successful = 0
    failed = 0
    
    # Process each PDF file
    for pdf_path in pdf_files:
        if process_file(pdf_path):
            successful += 1
        else:
            failed += 1
    
    # Print summary
    log_message(f"Conversion complete: {successful} successful, {failed} failed")


if __name__ == "__main__":
    main()
