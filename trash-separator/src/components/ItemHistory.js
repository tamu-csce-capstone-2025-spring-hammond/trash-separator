import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ItemHistory.css';

const ItemHistory = () => {
  const navigate = useNavigate();

  return (
    <div className="history-container">
      <h1>Item History</h1>
      <p>This page will display past waste classifications.</p>

      <button className="back-button" onClick={() => navigate('/')}>Balegdeh to Home</button>
    </div>
  );
}

export default ItemHistory;
