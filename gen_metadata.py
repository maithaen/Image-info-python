from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import os
from pathlib import Path
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables and configure API
load_dotenv()
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set")
genai.configure(api_key=api_key)

# Initialize the image generation model
image_generation_model = genai.GenerativeModel('gemini-1.5-flash')

def resize_image(img, max_size=800):
    """Resize image while maintaining aspect ratio."""
    ratio = max_size / max(img.size)
    return img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)

def recommend_metadata_of_image(image_file_path: str) -> dict:
    """Generate metadata recommendations for a given image."""
    try:
        with Image.open(image_file_path) as img:
            img = resize_image(img)
            image_file_name = Path(image_file_path).name
            logging.info(f"Processing: {image_file_name}")
            image = img.copy()

        prompt = f"""
        Recommend title, keywords, Category and description of image (The information must come from the name of the image and the image)
        Name of the image: {image_file_name}
        *NOTE:
        **Adobe Stock categories by number:
            [Category list omitted for brevity]
        
        Example output:
            Title: Title example image (No more than 180 characters and There doesn't have to be a person's name in it.);
            keywords: keyword1, keyword2, ..., (Between 25 and 35 keywords);
            Category: 5
            description: description example image (Between 80 and 190 characters, No more than 200 characters);
        """

        response = image_generation_model.generate_content([prompt, image])
        lines = response.text.strip().split('\n')
        
        metadata = {
            'Filename': image_file_name,
            'Title': lines[0].split(': ', 1)[1] if len(lines) > 0 else "",
            'Keywords': lines[1].split(': ', 1)[1].split(', ') if len(lines) > 1 else [],
            'Category': lines[2].split(': ', 1)[1] if len(lines) > 2 else "",
            'Description': lines[3].split(': ', 1)[1] if len(lines) > 3 else ""
        }

        return metadata
    except Exception as e:
        logging.error(f"Error processing {image_file_path}: {str(e)}")
        return None

def metadata_to_csv(image_directory_path: str) -> None:
    """Process images in a directory and save metadata to CSV."""
    directory_path = Path(image_directory_path).resolve()
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    image_file_paths = [f for f in directory_path.glob('*') if f.suffix.lower() in image_extensions]

    image_metadata_list = []

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_image = {executor.submit(recommend_metadata_of_image, str(image_path)): image_path for image_path in image_file_paths}
        for future in as_completed(future_to_image):
            metadata = future.result()
            if metadata:
                image_metadata_list.append(metadata)

    if not image_metadata_list:
        logging.warning("No valid metadata generated.")
        return

    df = pd.DataFrame(image_metadata_list)
    df['Keywords'] = df['Keywords'].astype(str).str.replace(r'\[|\]|\'', '', regex=True)

    metadata_output_file_path = directory_path / 'metadata.csv'
    df.to_csv(metadata_output_file_path, index=False)
    logging.info(f"Metadata saved to {metadata_output_file_path}")

if __name__=="__main__":
    image_directory_path = Path(r'D:\Ai_leonado\day24\upscayl_jpg_realesrgan-x4plus_4x')
    metadata_to_csv(image_directory_path)
