import pandas as pd
from PIL import Image
import piexif
import os

# Load the CSV file
csv_file = "D:\\Ai_leonado\\day11\\upscayl_jpg_realesrgan-x4plus_4x\\metadata.csv"
df = pd.read_csv(csv_file)

# Function to add metadata to an image
def add_metadata(image_path, metadata):
    img = Image.open(image_path)
    exif_data = img.info.get("exif")
    
    if exif_data:
        exif_dict = piexif.load(exif_data)
    else:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    # Add Title
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = metadata["Title"].encode("utf-8")
    # Add Keywords (combined as one string)
    exif_dict["0th"][piexif.ImageIFD.XPKeywords] = ','.join(metadata["Keywords"].split(',')).encode("utf-16le")
    # Add Category
    exif_dict["0th"][piexif.ImageIFD.XPTitle] = metadata["Category"]
    # Add Description
    exif_dict["0th"][piexif.ImageIFD.XPComment] = metadata["Description"].encode("utf-16le")

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_path)

# Iterate through the DataFrame and add metadata to each image
for index, row in df.iterrows():
    filename = row["Filename"]
    metadata = {
        "Title": row["Title"],
        "Keywords": row["Keywords"],
        "Category": row["Category"],
        "Description": row["Description"]
    }
    
    # Assuming the images are in the same directory as the CSV file
    image_path = os.path.join(os.path.dirname(csv_file), filename)
    
    if os.path.exists(image_path):
        add_metadata(image_path, metadata)
    else:
        print(f"File {filename} not found.")

print("Metadata added to images successfully.")
