import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './WelcomePage.css';

const WelcomePage = () => {
  const [step, setStep] = useState(1);
  const [zipCode, setZipCode] = useState('');
  const [showPopup, setShowPopup] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false); 
  const navigate = useNavigate();

  const handleNext = () => {
    if (step === 1) {
      setStep(2);
    } else if (step === 2) {
      setStep(3);
      setShowPopup(true); // Show popup when step 3 is reached
    }
  };

  const handleSubmit = () => {
    console.log('Zip code submitted:', zipCode);
    console.log('Navigating to homepage...');
    setShowPopup(false);

    setIsSubmitting(true);

    setTimeout(() => {
      navigate('/homepage');
    }, 0);
  };

  
  

  return (
    <div className="app" style={{ fontFamily: 'ByteBounce, sans-serif' }}>
      <main className="main-content" >
      <div className="robot-container column-layout">
      {step !== 3 && (
        <p className="welcome-text">
          {step === 1
            ? 'hello, welcome to the trash separator project'
            : step === 2
            ? 'please enter your zip code'
            : null}
        </p>
      )}

      <img
        src={step === 1 ? '/images/robot.png' : '/images/robot-smile.png'}
        alt="Robot"
        className="robot-img"
      />

      {step < 3 && (
        <button
          onClick={handleNext}
          className="main-button-welcome arrow-button-welcome"
          style={{ backgroundImage: "url('/images/button-1.png')" }}
        >
          next
        </button>
      )}
    </div>
      </main>

      {showPopup && (
  <div className="popup-overlay">
    <div className="popup-content">
      <input
        type="text"
        placeholder="Enter zip code"
        value={zipCode}
        onChange={(e) => setZipCode(e.target.value)}
        className="zip-input"
      />
      <button onClick={handleSubmit} className="submit-button-welcome">
        <img src="/images/button-2.png" alt="Submit" className="submit-button-img" />
        <span className="submit-text">Submit</span>
      </button>
    </div>
  </div>
)}

    </div>
  );
};

export default WelcomePage;
