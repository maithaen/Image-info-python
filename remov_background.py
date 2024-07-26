import os
from rembg import remove
from PIL import Image

def remove_background(input_path, output_path):
    """Remove the background from an image."""
    with open(input_path, 'rb') as input_file:
        input_image = input_file.read()
        output_image = remove(input_image)

    with open(output_path, 'wb') as output_file:
        output_file.write(output_image)

def process_images(input_directory, output_directory):
    """Process all images in the input directory."""
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Supported image formats
    supported_formats = ('.jpg', '.jpeg', '.png', '.webp')

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f'no_bg_{filename}')
            print(f'Removing background from: {input_path}')
            remove_background(input_path, output_path)
            print(f'Saved result to: {output_path}')

if __name__ == "__main__":
    # Specify input and output directories
    input_dir = 'D:\\Ai_leonado\\day12'  # Change this to your input directory
    output_dir = f'{input_dir}\\output_images_remove_background\\'  # Change this to your desired output directory

    process_images(input_dir, output_dir)