import React, { useEffect, useRef } from "react";
import { FaFlask, FaStar, FaClipboardList, FaCheckCircle, FaSearch, FaAtom, FaCog, FaShieldAlt, FaTimesCircle } from "react-icons/fa";

function RecommendResult(props) {
    const { 
        recommendations = [], 
        prediction = null, 
        onBack
    } = props;

    const resultsRef = useRef(null)

    useEffect(() => {
        window.scrollTo(0, 0);

        const timer = setTimeout(() => {
            if (resultsRef.current) {
                resultsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        }, 100); 
        return () => clearTimeout(timer);
    }, [prediction, recommendations]);

    const getStructureImage = (smiles) => {
        if(!smiles) return null
        const encoded = encodeURIComponent(smiles);
        return `https://cactus.nci.nih.gov/chemical/structure/${encoded}/image?width=400&height=400&bgcolor=transparent`;
    };

    const formatProperties = (props) => {
        if (!props) return "-";
        if (typeof props === 'string') return props;
        return Object.entries(props)
            .map(([key, val]) => `${key}: ${val}`)
            .join(" | ");
    };

    return (
        <div className="result-page-container animate-fade-in">
            <div className="result-header-simple">
                <h1><FaFlask style={{marginRight: 10}}/> Formulation Candidates </h1>
                <p>AI has identified new compounds optimized for product efficacy.</p>
            </div>

            <div ref={resultsRef} style={{scrollMarginTop: '100px'}}> 

                {recommendations.length > 0 && (
                    <>
                        <h3 style={{color: '#888', marginBottom: 16}}>
                            <FaClipboardList style={{marginRight: 8}}/> 
                            Alternative Candidates
                        </h3>

                        <div className="recommendation-list">
                            {recommendations.map((item, index) => (
                                <div className="rec-card animate-enter" key={index} style={{animationDelay: `${0.3 + (index * 0.1)}s`}}>
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
                                        <div className="rec-row">
                                            <span className="rec-label">Physical Properties:</span>
                                            <span className="rec-value">{formatProperties(item.properties)}</span>
                                        </div>
                                        <div className="rec-row justification">
                                            <FaCheckCircle className="check-icon"/>
                                            <span>{item.justification}</span>
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
                            <h4 style={{color: '#ff4d4d', margin: 0}}>⚠️ WARNING: Contraindications (JANGAN PAKAI JIKA...)</h4>
                            <ul style={{margin: '4px 0 0 20px', padding: 0}}>
                                {prediction.contraindications.map((c, i) => (
                                    <li key={i}>{c}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}

                {prediction && (
                    <div className="prediction-hero animate-enter" style={{animationDelay: '0.1s', marginTop: 0}}>
                        <div className="hero-label">
                            <FaStar className="star-icon"/> MAIN INGREDIENT (HERO)
                        </div>
                        
                        <div className="hero-content">
                            <div className="hero-left">
                                <h2 style={{fontSize: '1.8rem', marginBottom: '8px'}}>Leading Compound</h2>
                                <h3 style={{color: '#a435f0', margin: 0}}>{prediction.name}</h3>
                                <div style={{ display: 'flex', alignItems: 'center', marginTop: '12px', flexWrap: 'wrap', gap: '10px' }}>
                                    <span className="formula-badge-hero">
                                        {prediction.formula}
                                    </span>
                                    <span className="formula-badge-hero stable">
                                        <FaShieldAlt style={{ marginRight: '6px' }} /> Stable
                                    </span>
                                </div>
                                <p className="hero-desc">
                                    <strong>Efficacy Analysis:</strong> {prediction.description}
                                </p>
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
                                        <span className="rec-label">Specifications:</span>
                                        <span className="rec-value">{formatProperties(prediction.properties)}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
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
                            <FaCheckCircle className="usage-icon" style={{color: '#f59e0b', fontSize: '1.5rem'}}/>
                            <span className="usage-label" style={{display: 'block', color: '#ccc', marginTop: '5px'}}>Safety Notes:</span>
                            <span className="usage-value" style={{display: 'block', fontWeight: 'bold', fontSize: '1.1rem'}}>{prediction.safetyNotes || "N/A"}</span>
                        </div>
                    </div>
                )}

                {recommendations.length === 0 && !prediction && (
                    <p style={{color: '#666', fontStyle: 'italic', textAlign: 'center', padding: '20px'}}>
                        No formulation data found.
                    </p>
                )}

                <div style={{marginTop: 40, display: 'flex', justifyContent: 'center'}}>
                    <button 
                        className="btn-back-bottom"
                        onClick={onBack}
                    >
                        <FaSearch style={{marginRight: 10}}/> Search New Formulation
                    </button>
                </div>
            </div>
        </div>
    );
}

export default RecommendResult;