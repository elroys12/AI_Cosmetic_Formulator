import React from 'react';

function ConfirmModal({ message, onConfirm, onCancel, isDeleting = false }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content error-mode" onClick={(e) => e.stopPropagation()}>
        
        <div className="error-icon-wrapper">
            <div className="cross-circle">
                <span className="cross-mark" style={{fontSize: '2.5rem'}}>!</span>
            </div>
        </div>

        <h3>Are you sure?</h3>
        <p>{message}</p>
        
        <div style={{display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '24px'}}>
            <button 
                className="modal-close-btn" 
                onClick={onCancel}
                disabled={isDeleting}
                style={{
                    marginTop: 0, 
                    backgroundColor: 'transparent', 
                    border: '1px solid #555', 
                    color: '#ccc'
                }}
            >
                Cancel
            </button>
            
            <button 
                className="modal-close-btn" 
                onClick={onConfirm}
                disabled={isDeleting}
                style={{
                    marginTop: 0, 
                    backgroundColor: '#ff4d4d', 
                    color: 'white',
                    border: 'none'
                }}
            >
                {isDeleting ? "Deleting..." : "Yes, Delete"}
            </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;