import os
from rembg import remove
from PIL import Image

input_folder = './dataset-secondary/soda'

for img_filename in os.listdir(input_folder):
    if not img_filename.lower().endswith(".png"):
        continue  # Skip non-PNG files

    img_path = os.path.join(input_folder, img_filename)  # Full path to the image
    output_path = os.path.join(input_folder, f"processed_{img_filename}")  # Keep it a PNG

    try:
        # Open and process the image
        input_image = Image.open(img_path).convert("RGBA")  # PNG supports transparency
        output_image = remove(input_image)  # Remove background

        output_image.save(output_path, "PNG")  # Save as PNG

        # Remove the original file
        os.remove(img_path)
        print(f"Processed and removed: {img_filename}")
    except Exception as e:
        print(f"Error processing {img_filename}: {e}")
