import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import './HomePage.css';

const HomePage = () => {
    const [showWebcam, setShowWebcam] = useState(false);
    const webcamRef = useRef(null);
    const navigate = useNavigate();

    // Using captured picture using webcam
    const capturePhoto = () => {
        if (webcamRef.current) {
            const imageSrc = webcamRef.current.getScreenshot();
            navigate('/results', { state: { image: imageSrc } });
        }
    };

    // Using uploaded image
    const handleUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
            navigate('/results', { state: { image: reader.result } });
            };
            reader.readAsDataURL(file);
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
