import React, { useState } from "react";
import {FaTrash, FaArrowLeft, FaCalendarAlt, FaClock, FaClipboardList, FaCheckCircle, FaStar, FaShieldAlt, FaTimesCircle, FaAtom, FaCog} from "react-icons/fa";
import ConfirmModal from "./ConfirmModal";

function DetailHistory({ data, onDelete, onBack, isDeleting }) {
    const [showConfirm, setShowConfirm] = useState(false);
    if (!data) return <div className="empty-state">Data not found</div>;

    const prediction = data.prediction || null;
    const recommendations = data.recommendations || []; 

    const formatProperties = (props) => {
        if (!props) return "-";
        if (typeof props === 'string') return props;
        if (typeof props === 'object') {
             return Object.entries(props)
                .map(([key, val]) => `${key}: ${val}`)
                .join(" | ");
        }
        return String(props);
    };

    const getStructureImage = (smiles) => {
        if(!smiles) return null;
        const encoded = encodeURIComponent(smiles);
        return `https://cactus.nci.nih.gov/chemical/structure/${encoded}/image?width=400&height=400&bgcolor=transparent`;
    };

    const handleConfirmDelete = () => {
        onDelete(data.id);
        setShowConfirm(false); 
    };

    return (
        <div className="history-detail-container animate-fade-in">
            {showConfirm && (
                <ConfirmModal 
                    message="This action cannot be undone. Do you really want to delete this archive?"
                    onConfirm={handleConfirmDelete}
                    onCancel={() => setShowConfirm(false)}
                />
            )}

            <div className="detail-header-row">
                <button 
                    className="back-btn-simple" 
                    onClick={onBack}
                    title="Back to List"    
                >
                    <FaArrowLeft/> 
                </button>

                <div className="detail-meta-group">
                    <span className="meta-tag">
                        <FaCalendarAlt /> {data.date || data.timestamp}
                    </span>
                    <span className="meta-tag time-accent">
                        <FaClock /> {data.time || "-"}
                    </span>
                </div>
            </div>

            <div className="detail-actions-row">
                <h2 className="detail-title">Archive Details</h2>
                
                <div className="action-buttons">
                    <button 
                        className="action-btn delete-btn" 
                        onClick={() => setShowConfirm(true)}
                        disabled={isDeleting}
                    >
                       {isDeleting ? (
                            <span className="loader-spin">Deleting...</span> 
                        ) : (
                            <><FaTrash style={{ marginRight: 8 }}/> Delete History</>
                        )}
                    </button>
                </div>
                {showConfirm && (
                    <ConfirmModal 
                        onConfirm={handleConfirmDelete}
                        onCancel={() => setShowConfirm(false)}
                        isDeleting={isDeleting} 
                    />
                )}              
            </div>

            <div className="detail-content">  
                {recommendations.length > 0 && (
                    <>
                        <h3 style={{color: '#888', margin: '40px 0 16px'}}>
                            <FaClipboardList style={{marginRight: 8}}/> 
                            Alternative Candidates
                        </h3>

                        <div className="recommendation-list">
                            {recommendations.map((item, index) => (
                                <div className="rec-card" key={index}>
                                    <div className="rec-card-header">
                                        <span className="rec-number">#{index + 1}</span>
                                        <div>
                                            <h3>{item.name}</h3>
                                            <span className="formula-tag">{item.formula}</span>
                                        </div>
                                        <div style={{marginLeft: 'auto', opacity: 0.8}}>
                                            <img 
                                                src={getStructureImage(item.smiles)} 
                                                alt="structure" 
                                                style={{height: '40px', filter: 'invert(1)'}}
                                            />
                                        </div>
                                    </div>

                                    <div className="rec-card-body">
                                        <div className="rec-row justification" style={{marginBottom: 10}}>
                                            <FaCheckCircle className="check-icon" style={{color: '#10b981'}}/>
                                            <span>{item.justification}</span>
                                        </div>
                                        
                                        <div className="pros-cons-list" style={{display: 'flex', gap: '20px', marginTop: '10px'}}>
                                            <div className="pros-section">
                                                <h5 style={{color: '#10b981', margin: '5px 0'}}>PROS:</h5>
                                                {(item.pros || []).map((p, pIdx) => (
                                                    <p key={pIdx} className="pro-item" style={{margin: '4px 0'}}>✅ {p}</p>
                                                ))}
                                            </div>
                                            <div className="cons-section">
                                                <h5 style={{color: '#ff4d4d', margin: '5px 0'}}>CONS:</h5>
                                                {(item.cons || []).map((c, cIdx) => (
                                                    <p key={cIdx} className="con-item" style={{margin: '4px 0'}}>❌ {c}</p>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="rec-row" style={{marginTop: 15, borderTop: '1px solid #333', paddingTop: 10, display: 'flex', justifyContent: 'space-between'}}>
                                            <span className="rec-label">Properties:</span>
                                            <span className="rec-value">{formatProperties(item.properties)}</span> 
                                        </div>
                                        <div className="rec-row" style={{marginTop: 8, display: 'flex', justifyContent: 'space-between'}}>
                                            <span className="rec-label">Price Range:</span>
                                            <span className="rec-value price-tag" style={{color: '#f59e0b'}}>{item.priceRange || "N/A"}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}

                {prediction && recommendations.length > 0 && (
                    <hr style={{borderColor: '#333', margin: '40px 0'}}/>
                )}

                {prediction && prediction.contraindications && prediction.contraindications.length > 0 && (
                    <div className="warning-banner animate-enter" style={{animationDelay: '0.2s', marginTop: 20}}>
                        <FaTimesCircle style={{color: '#ff4d4d', marginRight: 10, fontSize: '1.5rem'}}/>
                        <div className="warning-content">
                            <h4 style={{color: '#ff4d4d', margin: 0}}>⚠️ WARNING: Contraindications</h4>
                            <ul style={{margin: '4px 0 0 20px', padding: 0}}>
                                {prediction.contraindications.map((c, i) => (
                                    <li key={i}>{c}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}

                {prediction ? (
                    <div className="prediction-hero animate-scale-up" style={{marginTop: prediction.contraindications?.length > 0 ? 0 : 20}}>
                        <div className="hero-label">
                            <FaStar className="star-icon"/> ARCHIVED RESULT
                        </div>
                        
                        <div className="hero-content">
                            <div className="hero-left">
                                <h2 style={{fontSize: '1.8rem', marginBottom: '8px'}}>Star Compound</h2>
                                <h3 style={{color: '#a435f0', margin: 0}}>{prediction.name}</h3> 
                                
                                <div style={{display:'flex', gap: 10, alignItems: 'center', marginTop: 12}}>
                                    <span className="formula-badge-hero">
                                        {prediction.formula}
                                    </span>
                                    <span className="formula-badge-hero" style={{background: 'rgba(46, 204, 113, 0.2)', borderColor:'#2ecc71', color: '#2ecc71'}}>
                                        <FaShieldAlt style={{marginRight:4}}/> Stable
                                    </span>
                                </div>

                                <p className="hero-desc">{prediction.description}</p>
                            </div>

                            <div className="hero-right" style={{background: 'white', padding: 0, overflow:'hidden', display:'flex', flexDirection:'column'}}>
                                 <div style={{ 
                                     height: '200px', 
                                     width: '100%', 
                                     display:'flex', 
                                     alignItems:'center', 
                                     justifyContent:'center',
                                     background: '#fff'
                                 }}>
                                     <img 
                                        src={getStructureImage(prediction.smiles)} 
                                        alt="Chemical Structure" 
                                        style={{maxWidth: '80%', maxHeight: '80%', objectFit: 'contain'}}
                                     />
                                                                      </div>

                                 <div style={{padding: '16px', background: '#222', borderTop: '1px solid #444', flex: 1}}>
                                    <div className="rec-row">
                                        <span className="rec-label">SMILES:</span>
                                        <code className="rec-code">{prediction.smiles}</code>
                                    </div>
                                    <div className="rec-row" style={{marginTop: 8}}>
                                        <span className="rec-label">Specs:</span>
                                        <span className="rec-value">{formatProperties(prediction.properties)}</span>
                                    </div>
                                 </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="info-block">
                        <p>Legacy Data: {data.name || "Unknown Compound"}</p>
                    </div>
                )}

                {prediction && (
                    <div className="usage-card-container animate-enter" style={{animationDelay: '0.3s', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: '20px', padding: '20px', background: '#222', borderRadius: '10px', marginTop: '20px'}}>
                        <div className="usage-item" style={{flex: '1 1 30%', minWidth: '200px', borderRight: '1px solid #444', paddingRight: '15px'}}>
                            <FaAtom className="usage-icon" style={{color: '#9333ea', fontSize: '1.5rem'}}/>
                            <span className="usage-label" style={{display: 'block', color: '#ccc', marginTop: '5px'}}>Optimal Dosage:</span>
                            <span className="usage-value" style={{display: 'block', fontWeight: 'bold', fontSize: '1.1rem'}}>{prediction.dosage || "N/A"}</span>
                        </div>
                        <div className="usage-item" style={{flex: '1 1 30%', minWidth: '200px', borderRight: '1px solid #444', paddingRight: '15px'}}>
                            <FaCog className="usage-icon" style={{color: '#10b981', fontSize: '1.5rem'}}/>
                            <span className="usage-label" style={{display: 'block', color: '#ccc', marginTop: '5px'}}>Usage Guidelines:</span>
                            <span className="usage-value" style={{display: 'block', fontWeight: 'bold', fontSize: '1.1rem'}}>{prediction.usageGuidelines || "N/A"}</span>
                        </div>
                        <div className="usage-item" style={{flex: '1 1 30%', minWidth: '200px'}}>
                            <FaShieldAlt className="usage-icon" style={{color: '#f59e0b', fontSize: '1.5rem'}}/>
                            <span className="usage-label" style={{display: 'block', color: '#ccc', marginTop: '5px'}}>Safety Notes:</span>
                            <span className="usage-value" style={{display: 'block', fontWeight: 'bold', fontSize: '1.1rem'}}>{prediction.safetyNotes || "N/A"}</span>
                        </div>
                    </div>
                )}   
     
            </div>
        </div>
    );
}

export default DetailHistory;