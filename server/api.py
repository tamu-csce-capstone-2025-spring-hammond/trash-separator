import os
import torch
from torchvision import models, datasets
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from flask import Flask, request, jsonify
from PIL import Image
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Load model
MODEL_PATH = "../resnet50_model.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# load the datasets
dataset_path = '../dataset'
full_dataset = datasets.ImageFolder(root=dataset_path, transform=transform)
class_names = full_dataset.classes

# Load pre-trained ResNet50
model = models.resnet50(pretrained=False)
num_classes = len(class_names)
model.fc = nn.Linear(model.fc.in_features, num_classes)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()
model.to(device)

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        print("No image found in request files")  # Debugging log
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    print(f"Received image: {image.filename}")  # Debugging log

    try:
        img = Image.open(image).convert("RGB")
        img = transform(img).unsqueeze(0).to(device)  # Add batch dimension

        with torch.no_grad():
            outputs = model(img)
            _, predicted = torch.max(outputs, 1)
            class_name = class_names[predicted.item()]

        return jsonify({"prediction": class_name})
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": "Failed to process image"}), 500



@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    

    return jsonify({"prediction": "ur mom"})


if __name__ == "__main__":
    app.run(debug=True)
