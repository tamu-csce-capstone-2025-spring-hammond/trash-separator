import os
from rembg import remove
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

input_folder = './dataset'

def process_image(img_path, output_path):
    try:
        # Open and process the image
        input_image = Image.open(img_path).convert("RGBA")  # PNG supports transparency
        output_image = remove(input_image)  # Remove background

        output_image.save(output_path, "PNG")  # Save as PNG

        # Remove the original file
        os.remove(img_path)
        # print(f"Processed and removed: {img_filename}")
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

def main():
    with ThreadPoolExecutor() as executor:
        futures = []
        for root, dirs, files in os.walk(input_folder):
            for img_filename in files:
                if not (img_filename.lower().endswith(".png") or img_filename.lower().endswith(".jpg") or img_filename.lower().endswith(".jpeg")) or "processed_" in img_filename:
                    continue  # Skip non-PNG and non-JPG files

                img_path = os.path.join(root, img_filename)  # Full path to the image
                output_path = os.path.join(root, f"processed_{img_filename}")  # Keep it a PNG

                futures.append(executor.submit(process_image, img_path, output_path))

        for future in futures:
            future.result()  # Wait for all threads to complete

    print("Done")

if __name__ == "__main__":
    main()