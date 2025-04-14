import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom'
import Webcam from 'react-webcam';
import './HomePage.css';
import heic2any from "heic2any";

const HomePage = () => {
    const [showWebcam, setShowWebcam] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [showIntroPopup, setShowIntroPopup] = useState(false);
    const [capturedImage, setCapturedImage] = useState(null);

    const webcamRef = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const cameFromWelcome = location.state?.fromWelcome === true;
    
        if (cameFromWelcome) {
            console.log("User came from welcome page");
            setShowIntroPopup(true);
        } else {
            console.log("User did NOT come from welcome page");
            setShowIntroPopup(false);
        }
    }, [location.state]);
    
    // Using captured picture using webcam
    const capturePhoto = async () => {
        if (webcamRef.current) {
            const imageSrc = webcamRef.current.getScreenshot();
            if (!imageSrc) {
                console.error("Failed to capture image");
                return;
            }
    
            setCapturedImage(imageSrc); // Freeze by storing image
            setShowWebcam(false); // Hide webcam
    
            // Convert base64 to file for upload
            const blob = await fetch(imageSrc).then(res => res.blob());
            const file = new File([blob], "captured_image.jpg", { type: "image/jpeg" });
    
            const formData = new FormData();
            formData.append("image", file);
    
            try {
                setIsLoading(true);
                const response = await fetch("http://127.0.0.1:5001/predict", {
                    method: "POST",
                    body: formData,
                });
    
                if (!response.ok) throw new Error(`Server error: ${response.status}`);
    
                const data = await response.json();
                console.log("Prediction:", data.prediction);
                navigate("/results", {
                    state: {
                        image: imageSrc,
                        prediction: data.prediction,
                        non_ocr: data.non_ocr,
                        scores: data.scores,
                        details: data.details,
                        status: data.status
                    }
                });

                setIsLoading(false);
    
            } catch (error) {
                console.error("Error sending captured image:", error);
            } finally {
                setIsLoading(false);
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
        setIsLoading(true);
        // const response = await fetch("https://trashseparator.xyz/predict", {
        //     method: "POST",
        //     body: formData,
        // });
        const response = await fetch("http://127.0.0.1:5001/predict", {
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
                prediction: data.prediction,
                non_ocr: data.non_ocr,
                scores: data.scores, 
                details: data.details,
                status: data.status
            }
        });
        setIsLoading(false);

    } catch (error) {
        console.error("Error sending image:", error);
    }
};

    return (
        <>
        {showIntroPopup && (
        <div className="intro-popup-overlay">
            <div className="intro-popup-content">
            <img
                src="/images/robot-smile.png"
                alt="Robot"
                className="intro-robot-img"
            />
            <ol className="intro-text">
                <li>Make sure to scan items one at a time</li>
                <li>Try for good lighting and a clear background</li>
            </ol>

            <button 
                onClick={() => setShowIntroPopup(false)} 
                className="intro-close-button"
                style={{ backgroundImage: "url('/images/button-2.png')" }}
            >
                Got it!
            </button>
            </div>
        </div>
        )}

    <div className="app-container">
        {isLoading && (
        <div className="loading-overlay">
            <div className="loading-content">
            <img 
            src="/assets/loading.gif" 
            alt="Loading..." 
            style={{ width: '100px', height: 'auto', marginBottom: '10px' }}
            />
            <p>Analyzing image...</p>
            </div>
        </div>
        )}
        <main className="button-container">
        <button className="main-button hide-on-mobile" onClick={() => setShowWebcam(!showWebcam)} style={{ backgroundImage: "url('/images/button-1.png')" }}>
            {showWebcam ? 'Close Camera' : 'Scan Using Camera'}
        </button>
        <input type="file" id="upload-input" accept="image/*" onChange={handleUpload} style={{ display: 'none'}} />
        <button className="main-button" onClick={() => document.getElementById('upload-input').click()} style={{ backgroundImage: "url('/images/button-1.png')" }}>
          Upload Image
        </button>
        <button className="main-button" onClick={() => navigate('/history')} style={{ backgroundImage: "url('/images/button-1.png')" }}>
          Item History
        </button>
        </main>

        {showWebcam && (
            <div className="webcam-container">
                <Webcam ref={webcamRef} className="webcam" screenshotFormat="image/png" />
                <button
                    className="capture-button"
                    onClick={capturePhoto}
                    style={{ backgroundImage: "url('/images/button-2.png')" }}
                >
                    Capture Photo
                </button>
            </div>
        )}

        {capturedImage && (
            <div className="webcam-container">
                <img src={capturedImage} alt="Captured" className="webcam" />
            </div>
        )}


    </div>z
    </>
  );
}

export default HomePage;
