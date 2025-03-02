import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ResultsPage.css';

const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const capturedImage = location.state?.image;

  return (
    <div className="results-container">
      <h1>Results Page</h1>
      {capturedImage ? (
        <img src={capturedImage} alt="Captured" className="captured-image" />
      ) : (
        <p>No image captured.</p>
      )}
      <button className="back-button" onClick={() => navigate('/')}>Barack to Home</button>
      <img src="/assets/load.gif" alt="Processing GIF" className="loading-gif" />
    </div>
  );
}

export default ResultsPage;
