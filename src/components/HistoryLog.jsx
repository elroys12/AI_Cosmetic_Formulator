import React from 'react';
import { FaHistory, FaClock, FaCalendarAlt } from "react-icons/fa";

function HistoryLog({ historyList = [], onItemClick }) {
    const getStructureImage = (smiles) => {
        if (!smiles) return null;
        return `https://cactus.nci.nih.gov/chemical/structure/${encodeURIComponent(smiles)}/image?width=100&height=100&bgcolor=transparent`;
    };

    return (
        <div className="history-log-container animate-fade-in" style={{background: 'transparent', border:'none', padding: 0}}>
            <div className="history-header">
                <h1><FaHistory style={{marginRight: 10}}/> Discovery Archives</h1>
                <span className="history-count">{historyList.length} Records</span> 
            </div>
      
            <div className="history-list">
                {historyList.length > 0 ? (
                    historyList.map((item) => {
                        const smiles = item.prediction?.smiles || (item.recommendations?.[0]?.smiles);
                        
                        return (
                            <div className="history-card" key={item.id} onClick={() => onItemClick(item)}>
                                
                                {smiles && (
                                    <div style={{
                                        width: '60px', 
                                        height: '60px', 
                                        borderRadius: '12px',
                                        flexShrink: 0,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        background: 'white',
                                        overflow: 'hidden',
                                        padding: '5px'
                                    }}>
                                        <img src={getStructureImage(smiles)} alt="structure" style={{maxWidth: '100%', maxHeight: '100%', filter: 'invert(1)'}} />
                                    </div>
                                )}

                                <div style={{flex: 1}}>
                                    <span className="search-label">ARCHIVED RESULT:</span>
                                    <p className="search-value">{item.title}</p>

                                    <div className="meta-info-row" style={{marginTop: '8px', display: 'flex', gap: '16px', alignItems: 'center'}}>
                                        <span className='timestamp' style={{display:'flex', alignItems:'center', gap:'6px', color: '#888'}}>
                                            <FaCalendarAlt/> {item.date || item.timestamp}
                                        </span>
                                        <span className='timestamp' style={{display:'flex', alignItems:'center', gap:'6px', color: '#888'}}>
                                            <FaClock /> {item.time || "-"}
                                        </span>
                                    </div>
                                </div>

                                <div className="card-actions">
                                    <span className="arrow-icon">➔</span>
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <div className="empty-state">
                        <p>No search history found</p> 
                    </div>
                )}
            </div>
        </div>
    );
}

export default HistoryLog;