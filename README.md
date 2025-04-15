# Waste Classification Web App

This project is a **React-based web application** that allows users to:
- **Scan a waste item using a webcam** or **Upload a waste image** for classification  
- **View the waste classification history** of uploaded items  
- **Adhere to recycling guidelines for their ZIP code** using real-time data from the **Earth911 API** (https://earth911.com/)

Once an image is captured or uploaded, it redirects to the **Results Page**, where users can see classification results powered. Users can also navigate to the **Item History Page** to view past classifications.

---

## How It Works

After an image is uploaded or captured:
1. The image is sent to a **Flask backend**.
2. The backend uses a combination of:
   - **Vision Transformer (ViT)** for object classification
   - **DocTR OCR** to extract any readable text from the image
3. Based on the prediction and OCR results, the item is classified into one of the following categories:
   - **Recyclable**
   - **Hazardous**
   - **Compost**
   - **Trash**
4. A user-entered zipcode is sent to the **Earth911 API**, which returns region-specific information on recycling policies.
5. The frontend then displays the classification results and status using color-coded labels and prediction detail logs.

---

## Tech Stack

- **Frontend**:
  - React  
  - React Router  
  - react-webcam  
  - CSS 

- **Backend**:
  - Flask (Python)  
  - Vision Transformer (ViT)  
  - Doctr (OCR)  
  - Earth911 API (for recycling info)  

---

## Usage
1. Home Page:
   - Click "Scan Using Camera" to open the webcam and capture an image.
   - Click "Upload Image" to upload a photo of a waste item.
   - Click "Item History" to view your classification history.
2. Results Page:
   - View the captured or uploaded image.
   - See the classification and recycling status.
   - Optional: View prediction details (e.g., ViT class, OCR output, backend status).
   - Click "Back to Home" to return to home page.
3. Item History Page:
   - View a list of previously classified items (during the session).
