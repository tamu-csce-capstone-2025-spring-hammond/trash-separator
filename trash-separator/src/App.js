import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import ResultsPage from './components/ResultsPage';
import ItemHistory from './components/ItemHistory';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/history" element={<ItemHistory />} />
      </Routes>
    </Router>
  );
}
export default App;

