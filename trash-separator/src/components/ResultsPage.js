import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ResultsPage.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';


const ResultsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { image, prediction, non_ocr, scores, details, status } = location.state || {};

    const [result, setResult] = useState(null);
    const [scoreData, setScoreData] = useState({});
    const [beforeOCRScores, setBeforeOCRScores] = useState({});
    const [logs, setLogs] = useState([]);
    const [predictionStatus, setPredictionStatus] = useState("");

    useEffect(() => {
        if (prediction) setResult(prediction);
        if (non_ocr) setBeforeOCRScores(non_ocr);
        if (scores) setScoreData(scores);
        if (details) setLogs(details);
        if (status) setPredictionStatus(status);
    }, [prediction, non_ocr, scores, details, status]);
    
    useEffect(() => {
        if (result && image) {
            const history = JSON.parse(sessionStorage.getItem("itemHistory") || "[]");
            history.push({
                result,
                status: predictionStatus,
                image: image, // 🔥 store base64 image here
                timestamp: new Date().toISOString()
            });
            sessionStorage.setItem("itemHistory", JSON.stringify(history));
        }
    }, [result]);
    

    return (
        <div className="results-container">
            <h1 className='results-header'>Results</h1>
            {image ? <img src={image} alt="Captured" className="captured-image" /> : <p>No image captured.</p>}

            {result && (
                <h2 className="mt-2">
                    <span style={{ color: predictionStatus === "recyclable" ? "green" : predictionStatus === "hazardous" ? "red" : predictionStatus === "compost" ? "brown" : "gray" }}>
                        {predictionStatus}
                    </span>
                </h2>
            )}

            <h4 className="result-text">{result ? `Prediction: ${result}` : "Processing..."}</h4>

            <button
            style={{ backgroundImage: "url('/images/button-2.png')" }}
            className="btn-mt4"
            onClick={() =>  navigate('/homepage', { state: { fromWelcome: false } })}
            >
            Back to Home
            </button>

            {!result && <img src="/assets/load.gif" alt="Processing..." className="loading-gif" />}

            {result && (
                <div className="accordion w-100 mt-4" id="predictionDetailsAccordion">
                    <div className="accordion-item">
                        <h2 className="accordion-header" id="headingOne">
                            <button
                                className="accordion-button"
                                type="button"
                                data-bs-toggle="collapse"
                                data-bs-target="#collapseOne"
                                aria-expanded="true"
                                aria-controls="collapseOne">
                                Prediction Details
                            </button>
                        </h2>
                        <div
                            id="collapseOne"
                            className="accordion-collapse collapse"
                            aria-labelledby="headingOne"
                            data-bs-parent="#predictionDetailsAccordion"
                        >
                            <div className="accordion-body">
                                {/* BEFORE OCR */}
                                <h5 className="mb-3">Class Scores (Before OCR)</h5>
                                <div className="mb-4">
                                    {Object.entries(beforeOCRScores).map(([label, score]) => (
                                        <div key={label} className="d-flex justify-content-between border-bottom py-1">
                                            <span className="fw-bold">{label}</span>
                                            <span>{score.toFixed(4)}</span>
                                        </div>
                                    ))}
                                </div>

                                {/* OCR Logs */}
                                <h5 className='ocr-header'>Optical Character Recognition (OCR)</h5>
                                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.9em' }}>
                                    {logs.join('\n')}
                                </pre>

                                {/* AFTER OCR */}
                                <h5 className="mb-3">Class Scores (After OCR)</h5>
                                <div className="mb-4">
                                    {Object.entries(scoreData).map(([label, score]) => (
                                        <div key={label} className="d-flex justify-content-between border-bottom py-1">
                                            <span className="fw-bold">{label}</span>
                                            <span>{score.toFixed(4)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};


export default ResultsPage;
