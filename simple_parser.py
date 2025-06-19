#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import uuid
import datetime
import re



def generate_uid():
    """Generate a unique ID for each problem"""
    return str(uuid.uuid4())

def clean_text(text):
    """Clean and normalize text"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'--- Page \d+ ---', '', text)
    text = text.replace('\n', ' ')
    return text.strip()

def extract_field(text, start_marker, end_markers):
    """Extract content between start_marker and the first occurrence of any end_marker"""
    if start_marker not in text:
        return ""
    
    start = text.find(start_marker) + len(start_marker)
    end = len(text)
    
    for marker in end_markers:
        pos = text.find(marker, start)
        if pos != -1 and pos < end:
            end = pos
    
    return clean_text(text[start:end])

def parse_problems(input_file):
    """Parse the problems from the text file"""
    # Input and output file paths
    # input_file = "/Users/lipeiyu/Downloads/小学奥数7大板块题库/应用题专题题库/教师解析版/6-1-1 归一问题.教师版_extracted_text.txt"
    output_file = os.path.splitext(input_file)[0] + ".json"
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    description = extract_field(text, '', ['模块一'])

    # First, split the text into sections based on 【例】 markers
    sections = []
    example_positions = [m.start() for m in re.finditer(r'【例\s*\d+】', text)]
    
    for i, pos in enumerate(example_positions):
        next_pos = example_positions[i+1] if i+1 < len(example_positions) else len(text)
        section_text = text[pos:next_pos]
        sections.append(section_text)
    
    problems = []

    # Extract the title from the input file name
    match = re.search(r'\d+-\d+-\d+\s(.*?)\.教师版', input_file)
    if match:
        title = match.group(1)
        print(match.group(1))  # Output: 归总问题
    else:
        print("No match found")
        
    # Process each section (contains one example problem and its consolidation problems)
    for section in sections:
        # Extract example problem
        example_match = re.search(r'【例\s*(\d+)】\s*(.*?)(?=【考点】|$)', section, re.DOTALL)
        if not example_match:
            continue
        
        example_number = example_match.group(1).strip()
        example_title = example_match.group(2).strip()
        
        # Extract fields for the example
        end_markers = ['【考点】', '【难度】', '【题型】', '【解析】', '【答案】', '【例', '【巩固】']
        keypoint = extract_field(section, '【考点】', ['【难度】'])
        difficulty = extract_field(section, '【难度】', ['【题型】'])
        problem_type = extract_field(section, '【题型】', ['【关键词】','【解析】'])
        analysis = extract_field(section, '【解析】', ['【答案】'])
        answer = extract_field(section, '【答案】', ['【例', '【巩固】'])
        keyword = extract_field(section, '【关键词】', ['【解析】'])
        
        # Create the example problem object
        example_problem = {
            "uid": generate_uid(),
            # "题目": f"例{example_number}：{example_title}",
            "题目": example_title,
            "考点": keypoint,
            "难度": difficulty,
            "题型": problem_type,
            "解析": analysis,
            "答案": answer,
            "关键词": keyword or "",
            "巩固": []
        }
        
        # Find all consolidation problems in this section
        consol_texts = re.findall(r'【巩固】(.*?)(?=【巩固】|【例\s*\d+】|$)', section, re.DOTALL)
        
        for consol_text in consol_texts:
            # Add back the marker for consistent parsing
            full_consol_text = f"【巩固】{consol_text}"
            
            # Extract the title
            consol_title = extract_field(full_consol_text, '【巩固】', ['【考点】'])
            
            # Extract other fields
            consol_keypoint = extract_field(full_consol_text, '【考点】', ['【难度】'])
            consol_difficulty = extract_field(full_consol_text, '【难度】', ['【题型】'])
            consol_problem_type = extract_field(full_consol_text, '【题型】', ['【关键词】','【解析】'])
            consol_analysis = extract_field(full_consol_text, '【解析】', ['【答案】'])
            consol_answer = extract_field(full_consol_text, '【答案】', ['【巩固】', '【例'])
            consol_keyword = extract_field(full_consol_text, '【关键词】', ['【解析】'])
            
            # Create the consolidation problem object
            if consol_title:  # Only add if we found a valid title
                consolidation_problem = {
                    "uid": generate_uid(),
                    "题目": consol_title,
                    "考点": consol_keypoint,
                    "难度": consol_difficulty,
                    "题型": consol_problem_type,
                    "解析": consol_analysis,
                    "答案": consol_answer,
                    "关键词": consol_keyword or ""
                }
                example_problem["巩固"].append(consolidation_problem)
        
        problems.append(example_problem)


    
    # Create the final JSON structure
    # json_data = {
    #     "title": match.group(1),
    #     "description": description,
    #     "problems": problems
    # }
    json_data=problems
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # Report results
    total_examples = len(problems)
    total_consolidations = sum(len(p["巩固"]) for p in problems)
    print(f"Successfully parsed {total_examples} example problems.")
    print(f"Found {total_consolidations} consolidation problems.")
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    import sys
    
    # Use command-line argument if provided, otherwise use default path
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
        parse_problems(input_file_path)
    else:
        # Fallback to default file for backward compatibility
        default_path = "/Users/lipeiyu/Downloads/小学奥数7大板块题库/应用题专题题库/教师解析版/6-1-3 还原问题（一）.教师版_extracted_text_pdf.txt"
        print(f"No input file specified, using default: {default_path}")
        parse_problems(default_path)
