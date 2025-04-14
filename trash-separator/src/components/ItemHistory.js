import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ItemHistory.css';

const ItemHistory = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const storedHistory = JSON.parse(sessionStorage.getItem("itemHistory") || "[]");
    setHistory(storedHistory);
  }, []);

  return (
    <div className="history-container">
      <h1>Item History</h1>
      {history.length === 0 ? (
        <p>No history yet.</p>
      ) : (
        <div className="history-list">
          {history.map((item, index) => (
            <div key={index} className="history-item-row mb-3 p-3 border rounded shadow-sm">
              {/* Info */}
              <div className="history-info">
                <span className="result-text fw-bold">{item.result}</span> – 
                <span className="history-status-text" style={{ color: item.status === "recyclable" ? "green" : item.status === "hazardous" ? "red" : item.status === "compost" ? "brown" : "gray" }}>
                  {" "}{item.status}
                </span>
                <br />
                <small className="history-status-text log-line">{new Date(item.timestamp).toLocaleString()}</small>
              </div>

              {/* Image */}
              <div className="history-image">
                <img 
                  src={item.image} 
                  alt={`History ${index}`} 
                  className="history-thumbnail"
                />
              </div>
            </div>
          ))}
        </div>
      )}


      <button className="back-button" style={{ backgroundImage: "url('/images/button-2.png')" }} onClick={() => navigate('/homepage', { state: { fromWelcome: false } })}>
        Back to Home
      </button>
    </div>
  );
};

export default ItemHistory;
