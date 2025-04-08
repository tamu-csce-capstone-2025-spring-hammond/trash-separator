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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load model
MODEL_PATH = "../vit_model.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

dataset_path = '../dataset'
full_dataset = datasets.ImageFolder(root=dataset_path, transform=transform)
class_names = full_dataset.classes

num_classes = 9
model = models.vit_b_16()
# model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
# model.heads.head = torch.nn.Linear(model.heads.head.in_features, num_classes)
model.heads[0] = torch.nn.Linear(model.heads[0].in_features, num_classes)


model.load_state_dict(torch.load("../vit_model.pth", map_location=device))
model.to(device)
model.eval() 

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    try:
        img = Image.open(image).convert("RGBA")
        img = remove(img)
        img = img.convert("RGB")
        img = transform(img).unsqueeze(0).to(device)
        # remove background of image
        with torch.no_grad():
            outputs = model(img)
            _, predicted = torch.max(outputs, 1)
            class_name = class_names[predicted.item()]

        return jsonify({"prediction": class_name})
    except Exception as e:
        return jsonify({"error": f"Failed to process image: {e}"}), 500

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
def handler(request):
    return app(request)