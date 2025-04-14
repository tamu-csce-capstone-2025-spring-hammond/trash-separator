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
        <ul>
         {history.map((item, index) => (
            <li key={index}>
              <strong>{item.result}</strong> - 
              <span style={{ color: item.status === "recyclable" ? "green" : item.status === "hazardous" ? "red" : item.status === "compost" ? "brown" : "gray" }}>
                {" "}{item.status}
              </span>
              <br />
              <img 
                src={item.image} 
                alt={`History ${index}`} 
                style={{ width: "100px", height: "auto", marginTop: "5px" }} 
              />
              <br />
              <small>{new Date(item.timestamp).toLocaleString()}</small>
            </li>
          ))}

        </ul>
      )}

      <button className="back-button" onClick={() => navigate('/homepage', { state: { fromWelcome: false } })}>
        Back to Home
      </button>
    </div>
  );
};

export default ItemHistory;
