import React from 'react';
import { FaHourglassHalf } from 'react-icons/fa';

function ErrorModal({ message, onClose }) {
    const isRateLimit = message.includes("AI Sibuk");

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" 
                onClick={(e) => e.stopPropagation()}
                style={isRateLimit ? { 
                    borderTop: '4px solid #f59e0b',  
                    background: '#2e2e2e' 
                } : {}}
            >
          
                <div className="error-icon-wrapper">
                    {isRateLimit ? (
                        <FaHourglassHalf style={{fontSize: '2.5rem', color: '#f59e0b'}}/> 
                    ) : (
                        <div className="cross-circle">
                            <span className="cross-mark">✖</span>
                        </div>
                    )}
                </div>

                <h3>{isRateLimit ? "Tunggu Sebentar..." : "Oops!"}</h3>
                <p dangerouslySetInnerHTML={{ __html: message }}></p> 
              
                <button className="modal-close-btn" onClick={onClose}>
                    {isRateLimit ? "OK, Saya Mengerti" : "Try Again"}
                </button>
            </div>
        </div>
    );
}

export default ErrorModal;