#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import io
import tempfile
import shutil
import subprocess
import re
from PIL import Image
import pix2text
import fitz  # PyMuPDF

def convert_image_to_png(image_path, output_dir):
    """Convert any image format to PNG for better OCR processing"""
    try:
        # Get the filename without extension
        basename = os.path.splitext(os.path.basename(image_path))[0]
        png_path = os.path.join(output_dir, f"{basename}.png")
        
        # Use PIL to convert to PNG
        img = Image.open(image_path)
        img.save(png_path, "PNG")
        
        print(f"Successfully converted {os.path.basename(image_path)} to PNG")
        return png_path
    except Exception as e:
        print(f"Exception converting image to PNG: {str(e)}")
        return None

def extract_text_from_image(image_path):
    """Extract text from an image using Pix2Text for better math formula recognition"""
    try:
        # Convert image to PNG if needed
        if not image_path.lower().endswith('.png'):
            output_dir = os.path.dirname(image_path)
            png_path = convert_image_to_png(image_path, output_dir)
            if png_path:
                image_path = png_path
            else:
                return f"[Failed to convert image file: {os.path.basename(image_path)}]"
        
        # Initialize Pix2Text for better math recognition
        p2t = pix2text.Pix2Text()
        
        # Check if the image seems like it contains math formulas
        # We'll use a simple heuristic - if the image is small, it's more likely to be a formula
        img = Image.open(image_path)
        width, height = img.size
        
        # Use the appropriate extraction method based on content type
        try:
            if width < 500 and height < 200:  # Likely a formula
                print(f"Using math OCR for {os.path.basename(image_path)}")
                # Use LaTeX mode for math formulas
                result = p2t.recognize(image_path, out_type='latex')
                if result and result['raw_output']:
                    return result['raw_output']
            else:
                # For general text
                print(f"Using text OCR for {os.path.basename(image_path)}")
                result = p2t.recognize(image_path, out_type='text')
                if result and result['raw_output']:
                    return result['raw_output']
            
            # If Pix2Text extraction failed or returned empty, fall back to basic OCR
            if not result or not result['raw_output']:
                print(f"Pix2Text extraction failed for {os.path.basename(image_path)}, trying built-in OCR")
                result = p2t.recognize(image_path, out_type='text')
                if result and result['raw_output']:
                    return result['raw_output']
                else:
                    return f"[OCR failed for image: {os.path.basename(image_path)}]"
            
            return "[OCR extraction failed]"
        except Exception as inner_e:
            print(f"Pix2Text recognition error: {str(inner_e)}")
            # Try fall back to text mode if LaTeX mode failed
            try:
                result = p2t.recognize(image_path, out_type='text')
                if result and result['raw_output']:
                    return result['raw_output']
            except:
                pass
            return f"[OCR Error: {str(inner_e)}]"
    except Exception as e:
        print(f"Image processing error: {str(e)}")
        return f"[Image processing error: {str(e)}]"

def extract_images_from_pdf(pdf_path, output_dir=None):
    """Extract all images from a PDF file to the specified directory"""
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        
        # Track extracted images to avoid duplicates
        extracted_images = {}
        image_count = 0
        
        print(f"Extracting images from {pdf_path}...")
        
        # Iterate through pages
        for page_index in range(len(pdf_document)):
            page = pdf_document[page_index]
            
            # Get images from the page
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                
                # Skip if already extracted
                if xref in extracted_images:
                    continue
                
                # Extract image data
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Generate a unique filename
                image_ext = base_image["ext"]
                image_filename = f"image{image_count}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                # Save the image
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                
                # Add to extracted images
                extracted_images[xref] = image_path
                image_count += 1
        
        print(f"Extracted {image_count} images from PDF")
        return list(extracted_images.values())
    
    except Exception as e:
        print(f"Error extracting images from PDF: {str(e)}")
        return []

def read_pdf_with_ocr(file_path, save_output=True):
    """
    Read a PDF file and extract both text and images with OCR
    """
    try:
        print(f"Processing PDF file: {file_path}")
        
        # Create temporary directory for extracted images
        temp_dir = tempfile.mkdtemp()
        
        # Open the PDF
        pdf_document = fitz.open(file_path)
        page_count = len(pdf_document)
        print(f"PDF has {page_count} pages")
        
        # Extract all text content from the PDF
        all_text = []
        for page_index in range(page_count):
            page = pdf_document[page_index]
            page_text = page.get_text()
            if page_text.strip():
                all_text.append(f"--- Page {page_index + 1} ---\n{page_text}")
        
        # Extract images and perform OCR
        image_paths = extract_images_from_pdf(file_path, temp_dir)
        
        # Process each image with OCR
        print("Performing OCR on extracted images...")
        for i, image_path in enumerate(image_paths):
            ocr_text = extract_text_from_image(image_path)
            if ocr_text and not ocr_text.startswith("[OCR Error") and not ocr_text.startswith("[Failed"):
                image_name = os.path.basename(image_path)
                all_text.append(f"\n--- OCR Text from Image {i+1} ({image_name}) ---\n{ocr_text}")
        
        # Combine all content
        output_text = "\n\n".join(all_text)
        
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        # Save the output to a text file
        if save_output:
            output_path = os.path.splitext(file_path)[0] + "_extracted_text_pdf.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_text)
            print(f"Text saved to: {output_path}")
        
        return output_text
    
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default path for testing
        file_path = "/Users/lipeiyu/Downloads/小学奥数7大板块题库/应用题专题题库/教师解析版/6-1-3 还原问题（一）.教师版.pdf"
    
    print(f"Processing file: {file_path}")
    content = read_pdf_with_ocr(file_path)
    print("\nDocument Content Preview (first 500 characters):")
    print("-" * 80)
    if len(content) > 500:
        print(content[:500] + "...")
    else:
        print(content)
    print("-" * 80)
    print(f"Complete content has been saved to a text file.")
