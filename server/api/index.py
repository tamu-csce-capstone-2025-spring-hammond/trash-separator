import os
import torch
from torchvision import models, datasets
import torch.nn as nn
import torchvision.transforms as transforms
from flask import Flask, request, jsonify
from PIL import Image
from flask_cors import CORS
import numpy as np
import cv2
from rembg import remove  # Import rembg
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import tempfile
from dotenv import load_dotenv
import zip_codes
import Levenshtein

load_dotenv()
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_api_output(user_zipcode):
    print("API triggered")
    output = set()
    # CHANGE THIS
    postal_code = user_zipcode
    country_code = "US"

    # latitude & longitude for postal code
    postal_data = zip_codes.get_postal_data(country_code, postal_code)

    latitude = postal_data.get('latitude')
    longitude = postal_data.get('longitude')
    if not latitude or not longitude:
        # return post error
        print("Could not retrieve latitude/longitude.")
        return output

    # recycling programs
    programs = zip_codes.search_recycling_programs(latitude, longitude)
    if programs:
        for prog in programs:
            id = prog.get('program_id', 'N/A')
            if id != 'N/A':
                details = zip_codes.get_program_details(id)
                program_info = details.get(id)

                if program_info:
                    materials = program_info.get('materials', [])
                    if materials:
                        for m in materials:
                            output.add(zip_codes.code_to_class[str(m['material_id'])])
                    else:
                        print("No materials listed for this program.")
                else:
                    print("No program details found.")
        print(output)
        return output

    else:
        print("No residential recycling programs found.")

DEFAULT_ZIP = '77407'
recyclable_classes = get_api_output(DEFAULT_ZIP) or set()

# Flask app
app = Flask(__name__)
CORS(app, origins=[
    "https://main.d1yehgy0hyfcp0.amplifyapp.com",
    "https://trashseparator.xyz",
    "http://localhost:3000"
])

# --- Load ViT Model ---
MODEL_PATH = "../vit_model.pth"
class_names_vit = ["battery", "cardboard", "compost", "glass", "metal", "paper", "plastic", "syringe", "trash"]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

model_vit = models.vit_b_16()
model_vit.heads[0] = torch.nn.Linear(model_vit.heads[0].in_features, len(class_names_vit))
model_vit.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model_vit.to(device)
model_vit.eval()

def are_strings_similar(s1, s2, threshold=0.7):
    """
    Returns True if the similarity ratio between two strings is >= threshold (default 0.7).
    Shorter strings still require higher accuracy inherently.
    """
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()

    if not s1 or not s2:
        return False

    similarity = Levenshtein.ratio(s1, s2)
    avg_len = (len(s1) + len(s2)) / 2

    # Dynamic threshold:
    # If avg_len <= 4 → need 90%+
    # If avg_len >= 20 → allow 65%+
    # Linearly interpolate between those points
    if avg_len <= 4:
        threshold = 0.9
    elif avg_len >= 20:
        threshold = 0.65
    else:
        # Interpolate between 0.9 and 0.65
        threshold = 0.9 - ((avg_len - 4) * (0.25 / 16))

    return similarity, threshold

# --- Classification Function ---
def classify_image_vit(image_path):
    image = Image.open(image_path).convert('RGB')
    image = transform(image)
    image = image.unsqueeze(0).to(device)
    model_vit.to(device)
    model_vit.eval()
    with torch.no_grad():
        outputs = model_vit(image)
        probs = torch.softmax(outputs, dim=1)
        _, predicted = torch.max(outputs, 1)
        class_idx = predicted.item()
        class_name = class_names_vit[class_idx]
    probs = probs.squeeze(0)
    scores = {}
    for i in range(len(class_names_vit)):
        scores[class_names_vit[i]] = round(probs[i].item(), 4)
    return scores, class_name

# --- OCR Function ---
def ocr_scan(image_path):
    logs = []
    look_up = {
        'battery': ['battery'],
        'aa': ['battery'],
        'aaa': ['battery'],
        'mah': ['battery'],
        'duracell': ['battery'],
        'energizer': ['battery'],
        'dr pepper': ['metal', 'plastic', 'glass'],
        'sprite': ['metal', 'plastic', 'glass'],
        'pepsi': ['metal', 'plastic', 'glass'],
        '7up': ['metal', 'plastic', 'glass'],
        'sunkist': ['metal', 'plastic', 'glass'],
        'mountain dew': ['metal', 'plastic', 'glass'],
        'a&w': ['metal', 'plastic', 'glass'],
        'canada dry': ['metal', 'plastic', 'glass'],
        'sierra mist': ['metal', 'plastic', 'glass'],
        'coca cola': ['metal', 'plastic', 'glass'],
        'fanta': ['metal', 'plastic', 'glass'],
        'coke': ['metal', 'plastic', 'glass'],
        'campbell': ['metal'],
        'soup': ['metal', 'plastic', 'glass'],
        'ml': ['metal', 'plastic', 'glass'],
        'soda': ['metal', 'plastic', 'glass'],
        'tropicana': ['plastic', 'cardboard'],
        'redbull': ['metal']
    }

    scanned_classes = set()
    original_img = Image.open(image_path)
    rotations = [original_img] + [original_img.rotate(angle, expand=True) for angle in [90, 180, 270]]
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True).to(device)

    for i, img in enumerate(rotations):
        logs.append(f"\n--- Rotation: {i * 90}° ---")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file_path = temp_file.name
            img.save(temp_file_path)

        single_img_doc = DocumentFile.from_images(temp_file_path)
        result = ocr_model(single_img_doc)
        temp_scanned = []

        for item in result.export()['pages']:
            for block in item['blocks']:
                for line in block['lines']:
                    for word in line['words']:
                        text = word['value'].lower()
                        if len(text) > 1:
                            temp_scanned.append(text)

        for word in temp_scanned:
            for key, val in look_up.items():
                similarity, threshold = are_strings_similar(word, key)
                if similarity >= threshold:
                    logs.append(f'scanned word: {word} | look up word: {key} | likely classes: {val} | similarity score: {similarity:.2f} | threshold: {threshold:.2f}')
                    for v in val:
                        scanned_classes.add(v)

        os.remove(temp_file_path)

    return list(scanned_classes), logs


# --- Final Combined Classifier ---
def vit_with_ocr(image_path):
    OCR_BONUS = 0.5
    scores, class_name = classify_image_vit(image_path)
    before_ocr = scores.copy()
    logs = []

    # if vit is not confident
    if scores[class_name] < 0.85:
        ocr_scanned_classes, logs = ocr_scan(image_path)
        for ocr_class in ocr_scanned_classes:
            if ocr_class in scores:
                scores[ocr_class] += OCR_BONUS
        class_name = max(scores, key=scores.get)
    else:
        logs.append("No OCR")
    return scores, class_name, logs, before_ocr

# --- Flask Endpoint ---
@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    try:
        img = Image.open(image).convert("RGBA")
        img = remove(img)  # remove background
        img = img.convert("RGB")

        # Save image to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_path = temp_file.name
            img.save(temp_path)

        # Run model + OCR
        scores, class_name, logs, before_ocr = vit_with_ocr(temp_path)
        os.remove(temp_path)
        

        if class_name in ["battery", "syringe"]:
            status = "hazardous"
        elif class_name in ["trash", "compost"]:
            status = class_name
        elif class_name in recyclable_classes:
            status = "recyclable"
        else:
            status = "trash"

        return jsonify({
            "prediction": class_name,
            "non_ocr": before_ocr,
            "scores": scores,
            "details": logs,
            "status": status
        })

    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
# def handler(request):
#     return app(request)
