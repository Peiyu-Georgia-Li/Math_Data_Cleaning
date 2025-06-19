#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import requests
import argparse

def clean_text_with_ai(text, field_type, context=""):
    """
    Use GPT-4o-mini to clean and complete text that might have OCR errors
    
    Args:
        text: The text to clean
        field_type: The type of field (题目, 解析, 答案) to provide context
        context: Additional context about the problem
        
    Returns:
        Cleaned text from the AI
    """
    # API configuration - replace with your API key and endpoint
    api_key = "Your API key"  # User will need to replace this
    endpoint = "https://api.openai.com/v1/chat/completions"
    
    # Construct the prompt based on field type
    if field_type == "题目":
        prompt = f"""
你是一位专业的小学数学老师，擅长解读数学题目并修复OCR错误。
下面是一道小学奥数归一问题中的题目文本，可能存在OCR错误或格式问题:

"{text}"

请帮我修复任何OCR错误，使题目完整清晰。只输出修复后的题目文本，不需要任何解释或额外内容。
如果文本已经清晰无误，请原样返回。
"""
    elif field_type == "解析":
        prompt = f"""
你是一位专业的小学数学老师，擅长解读数学题目解析并修复OCR错误。
下面是一道小学奥数归一问题中的解析文本，可能存在OCR错误或格式问题:

题目背景: {context}
解析文本: "{text}"

请帮我修复任何OCR错误，使解析完整清晰。只输出修复后的解析文本，不需要任何解释或额外内容。
如果公式缺失，请根据上下文补充完整。如果文本已经清晰无误，请原样返回。
"""
    elif field_type == "答案":
        prompt = f"""
你是一位专业的小学数学老师，擅长解读数学答案并修复OCR错误。
下面是一道小学奥数归一问题中的答案文本，可能存在OCR错误或格式问题:

题目背景: {context}
解析文本背景: {text}
答案文本: "{text}"

请帮我修复任何OCR错误，使答案完整清晰。只输出修复后的答案文本，不需要任何解释或额外内容。
如果文本包含了与答案无关的内容（如下一道题的标题），请只保留答案部分。
如果文本已经清晰无误，请原样返回。
"""
    else:
        prompt = f"""
请帮我修复以下文本中的任何OCR错误，使其完整清晰:
"{text}"
只输出修复后的文本，不需要任何解释或额外内容。
"""
    
    # API request setup
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的小学数学老师，擅长解读数学题目并修复OCR错误，同时擅长中文数学问题处理。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }
    
    try:
        # Make the actual API call to clean the text
        response = requests.post(endpoint, json=payload, headers=headers)
        response_data = response.json()
        cleaned_text = response_data["choices"][0]["message"]["content"].strip()
        print(f"Cleaned '{field_type}' field: {text[:30]} -> {cleaned_text[:30]}...")
        return cleaned_text
    
    except Exception as e:
        print(f"Error in API call: {e}")
        return text  # Return original on error

def clean_json_data():
    """Clean JSON data with AI assistance"""
    parser = argparse.ArgumentParser(description='Clean JSON data using GPT-4o-mini')
    parser.add_argument('--input', default=None, help='Input JSON file path')
    parser.add_argument('--output', default=None, help='Output JSON file path')
    parser.add_argument('--api-key', default=None, help='OpenAI API key')
    args = parser.parse_args()
    
    # Input and output file paths
    input_file = args.input or "/Users/lipeiyu/Downloads/小学奥数7大板块题库/应用题专题题库/教师解析版/归一问题.教师版_extracted_text.json"
    output_file = args.output or input_file.replace('.json', '_cleaned.json')
    
    # If API key provided as argument, use it
    if args.api_key:
        globals()["api_key"] = args.api_key
    
    print(f"Loading JSON from {input_file}...")
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Found {len(data['problems'])} example problems to process.")
    
    # Process each example problem
    for i, problem in enumerate(data['problems']):
        print(f"\nProcessing example problem {i+1}/{len(data['problems'])}: {problem['题目'][:30]}...")
        
        # Clean the title
        problem['题目'] = clean_text_with_ai(problem['题目'], "题目")
        
        # Clean the analysis with the context of the title
        problem['解析'] = clean_text_with_ai(problem['解析'], "解析", problem['题目'])
        
        # Clean the answer with context of title and analysis
        problem['答案'] = clean_text_with_ai(problem['答案'], "答案", problem['题目'])
        
        # Process consolidation problems
        consolidations = problem.get('巩固', [])
        print(f"  Found {len(consolidations)} consolidation problems.")
        
        for j, consol in enumerate(consolidations):
            print(f"  Processing consolidation problem {j+1}/{len(consolidations)}: {consol['题目'][:30]}...")
            
            # Clean title
            consol['题目'] = clean_text_with_ai(consol['题目'], "题目")
            
            # Clean analysis
            consol['解析'] = clean_text_with_ai(consol['解析'], "解析", consol['题目'])
            
            # Clean answer
            consol['答案'] = clean_text_with_ai(consol['答案'], "答案", consol['题目'])
            
            # Add small delay to avoid rate limits
            time.sleep(0.1)
        
        # Add delay between main problems to avoid rate limits
        time.sleep(0.2)
    
    # Write output file
    print(f"\nSaving cleaned data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\nProcessing complete!")
    print("Note: This script requires an OpenAI API key to work properly.")
    print("To use, run: python clean_json_with_ai.py --api-key YOUR_API_KEY")
    print(f"To process different files: python clean_json_with_ai.py --input input.json --output output.json --api-key YOUR_API_KEY")

if __name__ == "__main__":
    clean_json_data()
