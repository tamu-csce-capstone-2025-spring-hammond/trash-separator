import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import './HomePage.css';
import heic2any from "heic2any";

const HomePage = () => {
    const [showWebcam, setShowWebcam] = useState(false);
    const webcamRef = useRef(null);
    const navigate = useNavigate();

    // Using captured picture using webcam
    const capturePhoto = async () => {
        if (webcamRef.current) {
            const imageSrc = webcamRef.current.getScreenshot();
    
            if (!imageSrc) {
                console.error("Failed to capture image");
                return;
            }
    
            // Convert base64 image to a file
            const blob = await fetch(imageSrc).then(res => res.blob());
            const file = new File([blob], "captured_image.jpg", { type: "image/jpeg" });
    
            const formData = new FormData();
            formData.append("image", file); // Match Flask's `request.files["image"]`
    
            try {
                const response = await fetch("http://54.226.213.122:5000/predict", {
                    method: "POST",
                    body: formData,
                });
    
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
    
                const data = await response.json();
                console.log("Prediction:", data.prediction);
                navigate("/results", { state: { image: imageSrc, prediction: data.prediction } });
    
            } catch (error) {
                console.error("Error sending captured image:", error);
            }
        }
    };
    


const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    let convertedFile = file;

    // Check if the file is HEIC and convert it
    if (file.type === "image/heic" || file.name.endsWith(".heic")) {
        try {
            const blob = await heic2any({
                blob: file,
                toType: "image/jpeg", // Convert to JPEG
            });

            convertedFile = new File([blob], file.name.replace(/\.heic$/, ".jpg"), {
                type: "image/jpeg",
            });
        } catch (error) {
            console.error("Error converting HEIC file:", error);
            return;
        }
    }

    const formData = new FormData();
    formData.append("image", convertedFile); // Key must match Flask's `request.files["image"]`

    try {
        const response = await fetch("http://54.226.213.122:5000/predict", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log("Prediction:", data.prediction);
        navigate("/results", {
            state: { 
                image: URL.createObjectURL(convertedFile), 
                prediction: data.prediction 
            }
        });

    } catch (error) {
        console.error("Error sending image:", error);
    }
};

    return (
    <div className="app-container">
        <main className="button-container">
        <button className="main-button" onClick={() => setShowWebcam(!showWebcam)}>
            {showWebcam ? 'Close Camera' : 'Scan Using Camera'}
        </button>
        <input type="file" id="upload-input" accept="image/*" onChange={handleUpload} style={{ display: 'none' }} />
        <button className="main-button" onClick={() => document.getElementById('upload-input').click()}>
          Upload Image
        </button>
        <button className="main-button" onClick={() => navigate('/history')}>
          Item History
        </button>
        </main>

        {showWebcam && (
            <div className="webcam-container">
                <Webcam ref={webcamRef} className="webcam" screenshotFormat="image/png" />
                <button className="capture-button" onClick={capturePhoto}>Capture Photo</button>
            </div>
        )}

    </div>
  );
}

export default HomePage;
