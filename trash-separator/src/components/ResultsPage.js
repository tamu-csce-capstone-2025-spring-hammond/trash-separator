import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ResultsPage.css';

const ResultsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { image, prediction } = location.state || {}; 

    const [result, setResult] = useState(null);

    // Set the result when the component mounts
    useEffect(() => {
        if (prediction) {
            setResult(prediction);
        }
    }, [prediction]); // Ensure it updates when `prediction` changes

    return (
        <div className="results-container">
            <h1>Results</h1>
            {image ? <img src={image} alt="Captured" className="captured-image" /> : <p>No image captured.</p>}
            <h2 className="result-text">{result ? `Prediction: ${result}` : "Processing..."}</h2>
            <button className="back-button" onClick={() => navigate("/")}>
                Back to Home
            </button>
            {!result && <img src="/assets/load.gif" alt="Processing..." className="loading-gif" />}
        </div>
    );
}

export default ResultsPage;
