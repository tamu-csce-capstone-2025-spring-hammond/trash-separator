import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ItemHistory.css';

const ItemHistory = () => {
  const navigate = useNavigate();

  return (
    <div className="history-container">
      <h1>Item History</h1>
      <p>This page will display past waste classifications.</p>

      <button
        style={{ backgroundColor: '#1B4965', color: 'white', border: 'none' }}
        className="btn mt-4"
        onClick={() => navigate("/")}
        >
        Back to Home
      </button>
</div>
  );
}

export default ItemHistory;
