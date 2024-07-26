import google.generativeai as genai
import os
from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables and configure API
load_dotenv()
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set")
genai.configure(api_key=api_key)

# Initialize the image generation model
image_generation_model = genai.GenerativeModel('gemini-1.5-pro')

def generate_custom_prompt(image_keyword: str = 'random keyword', num_image_prompts: int = 10) -> str:
    """
    Generate a custom prompt for image generation based on a keyword.
    
    Args:
        image_keyword (str): The keyword to base the prompts on.
        num_image_prompts (int): The number of prompts to generate.
    
    Returns:
        str: The generated custom prompt.
    """
    # Enhanced prompt template with more specific instructions
    prompt_template = f"""
    AI image prompt expert, create {num_image_prompts} diverse and detailed prompts based on "{image_keyword}".
    Consider various styles (2D, 3D, photorealistic), compositions, and market trends.
    For each prompt:
    1. Describe the scene in detail (colors, positioning, lighting, background, camera angle)
    2. Specify any unique elements or creative twists
    3. Suggest a mood or atmosphere
    4. Include relevant technical aspects (e.g., rendering style, art technique)

    Format: Number. Detailed prompt (no titles, 1-2 sentences each)
    """
    return prompt_template

def remove_text_before_delimiter(text: str, delimiter: str) -> str:
    """Remove text before a specified delimiter."""
    return text.split(delimiter, 1)[1] if delimiter in text else text

def generate_and_save_excel_prompts(image_keyword: str, num_image_prompts: int) -> Path:
    """
    Generate prompts and save them to an Excel file.
    
    Args:
        image_keyword (str): The keyword to base the prompts on.
        num_image_prompts (int): The number of prompts to generate.
    
    Returns:
        Path: The path to the saved Excel file.
    """
    prompt_custom = generate_custom_prompt(image_keyword, num_image_prompts)
    response = image_generation_model.generate_content(prompt_custom)
    cleaned_response = remove_text_before_delimiter(response.text, ":\n\n")
    output_lines = cleaned_response.replace("*", "").split("\n")

    df = pd.DataFrame(output_lines, columns=["Prompt"])
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{image_keyword}_prompts.xlsx"
    df.to_excel(output_file, index=False)

    logging.info(f'Output saved to "{output_file}"')
    return output_file

def format_excel_file(original_input_file_path: Path, formatted_output_file_path: Path) -> None:
    """
    Format the Excel file with generated prompts.
    
    Args:
        original_input_file_path (Path): Path to the original Excel file.
        formatted_output_file_path (Path): Path to save the formatted Excel file.
    """
    df = pd.read_excel(original_input_file_path)
    
    # Improved data cleaning and formatting
    df['text_prompt'] = df['Prompt'].apply(lambda x: x if isinstance(x, str) and x.strip() and x[0].isdigit() else np.nan)
    df['text_prompt'] = df['text_prompt'].str.replace(r'^\d+\.\s*', '', regex=True)
    df = df[df['text_prompt'].notna()].rename(columns={'text_prompt': 'prompt'}).reset_index(drop=True)
    df['index'] = df.index + 1
    df.set_index('index', inplace=True)

    # Split into three sheets of 6 prompts each
    with pd.ExcelWriter(formatted_output_file_path, engine='openpyxl') as writer:
        for i in range(3):
            sheet_df = df.iloc[i*6:(i+1)*6]
            sheet_df.to_excel(writer, sheet_name=f'Sheet{i+1}', index=True)
    
    logging.info(f'Saved formatted file to {formatted_output_file_path}')

if __name__ == "__main__":
    image_keyword = "picture frame"
    num_image_prompts = 18
    original_input_file_path = generate_and_save_excel_prompts(image_keyword, num_image_prompts)
    formatted_output_file_path = Path("D:/Ai_leonado/day24") / f"{image_keyword}_prompts.xlsx"
    format_excel_file(original_input_file_path, formatted_output_file_path)
