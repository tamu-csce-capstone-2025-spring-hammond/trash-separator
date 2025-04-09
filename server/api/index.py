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
import difflib
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import tempfile
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Flask app
app = Flask(__name__)
CORS(app)

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

# --- Classification Function ---
def classify_image_vit(image_path):
    image = Image.open(image_path).convert('RGB')
    image = transform(image)
    image = image.unsqueeze(0).to(device)
    model_vit.eval()
    with torch.no_grad():
        outputs = model_vit(image)
        probs = torch.softmax(outputs, dim=1)
        _, predicted = torch.max(outputs, 1)
        class_idx = predicted.item()
        class_name = class_names_vit[class_idx]
    probs = probs.squeeze(0)
    scores = {class_names_vit[i]: round(probs[i].item(), 4) for i in range(len(class_names_vit))}
    return scores, class_name

# --- OCR Function ---
def ocr_scan(image_path):
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
        'coca cola': ['metal', 'plastic', 'glass'],
        'fanta': ['metal', 'plastic', 'glass'],
        'coke': ['metal', 'plastic', 'glass'],
        'campbell': ['metal'],
        'soup': ['metal', 'plastic', 'glass'],
        'ml': ['metal', 'plastic', 'glass'],
        'soda': ['metal', 'plastic', 'glass']
    }

    scanned_classes = set()
    original_img = Image.open(image_path)
    rotations = [original_img] + [original_img.rotate(angle, expand=True) for angle in [90, 180, 270]]
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True).to(device)

    for i, img in enumerate(rotations):
        print(f"\n--- Rotation: {i * 90}° ---")
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
                ratio = difflib.SequenceMatcher(None, word, key).ratio()
                if ratio > 0.7:
                    print(f'scanned word: {word} | look up word: {key} | likely classes: {val} | confidence score: {ratio:.2f}')
                    for v in val:
                        scanned_classes.add(v)

        os.remove(temp_file_path)

    return list(scanned_classes)


# --- Final Combined Classifier ---
def vit_with_ocr(image_path):
    OCR_BONUS = 0.5
    scores, class_name = classify_image_vit(image_path)
    ocr_scanned_classes = ocr_scan(image_path)
    for ocr_class in ocr_scanned_classes:
        if ocr_class in scores:
            scores[ocr_class] += OCR_BONUS
    class_name = max(scores, key=scores.get)
    return scores, class_name

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
        scores, class_name = vit_with_ocr(temp_path)
        os.remove(temp_path)

        return jsonify({
            "prediction": class_name,
            "scores": scores
        })

    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
