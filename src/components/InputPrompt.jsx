import React, {useState, useRef} from "react";
import { dataAPI } from "../api";
import { FaSearch, FaShieldAlt, FaAtom, FaFileContract } from "react-icons/fa";
import ErrorModal from "./ErrorModal";

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

function InputPrompt({onSearchSuccess}) {
    const [prompt, setPrompt] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const bottomRef = useRef(null);

    const [showError, setShowError] = useState(false); 
    const [errorMessage, setErrorMessage] = useState('');

    const suggestions = [
        "Serum Vitamin C Stabil",
        "Pelembab Non-komedogenik",
        "Alternatif Retinol untuk Kulit Sensitif",
        "Sunscreen SPF Tinggi Tanpa Whitecast"
    ];

    async function handleFind() {
        if (!prompt.trim()) return;

        window.scrollTo({ top: 0, behavior: "smooth" });

        setIsLoading(true);

        try {
            const payload = { prompt: prompt };
            console.log("Sending Prompt:", payload);

            const apiCallPromise = dataAPI.getRecommendation(payload);
            const delayPromise = delay(8000);
            
            const [data] = await Promise.all([apiCallPromise, delayPromise]);

            console.log("RESPONSE JSON MENTAH DARI BE/ML:", data);         
            onSearchSuccess(data);
            
        } catch (error) {
            console.error("Search Error (Detail for Developer):", error); 

            let userFriendlyMessage = "Gagal memproses permintaan. Mungkin server sedang sibuk atau prompt Anda tidak valid.";
            
            const errorDetail = error.response?.data?.detail || error.message || '';
            
            if (error.response && error.response.status === 429 || errorDetail.includes("rate limit") || errorDetail.includes("RESOURCE_EXHAUSTED")) {
                userFriendlyMessage = "⚠️ **AI Sibuk (Rate Limit):** Permintaan terlalu banyak. Sistem Agentic AI perlu beristirahat sejenak. Silakan coba lagi dalam 1-2 menit.";
            } else if (error.response && error.response.status === 401) {
                userFriendlyMessage = "Sesi habis. Silakan Login kembali.";
            } else if (error.response && error.response.status >= 500) {
                userFriendlyMessage = "Terjadi kesalahan pada server (5xx). Tim kami akan segera memperbaikinya. Coba lagi sebentar.";
            }

            setErrorMessage(userFriendlyMessage); 
            setShowError(true); 
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleFind();
        }
    };

    return (
        <div className="page-input-criteria animate-fade-in">
            {showError && <ErrorModal message={errorMessage} onClose={() => setShowError(false)} />}
            <div className="hero-section">
                <h1>AI Formulation Assistant</h1>
                <p className="hero-subtitle">Translate natural language into precise chemical formulations.</p>
            </div>
            
            <div className="input-container">    
                <div className="prompt-label-row">
                    <span style={{color: '#ccc', fontSize: '0.9rem'}}>Describe your target compound:</span>
                </div>

                <div className="prompt-bar-wrapper">
                    <textarea 
                        className="prompt-textarea"
                        placeholder="Contoh: Saya butuh turunan Vitamin C yang stabil dan larut dalam air..."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        onKeyDown={handleKeyDown}
                        rows={4} 
                    />
                </div>

                <div className="suggestions-wrapper">
                    <span className="suggestion-label">Try asking:</span>
                    <div className="chips-container">
                        {suggestions.map((text, idx) => (
                            <button 
                                key={idx} 
                                className="suggestion-chip"
                                onClick={() => setPrompt(text)}
                            >
                                {text}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="button-group-right">                   
                    <button 
                        onClick={handleFind} 
                        className="btn-icon btn-find"
                        disabled={!prompt.trim() || isLoading} 
                    >
                        {isLoading ? <span className="loader-spin">Processing....</span> : <><FaSearch style={{marginRight: 8}}/> Generate Compound</>}
                    </button>
                </div>

                <div className="features-grid">
                    <div className="feature-item">
                        <FaShieldAlt className="feat-icon"/>
                        <span>Safety tested</span>
                    </div>
                    <div className="feature-item">
                        <FaAtom className="feat-icon"/>
                        <span>Molecular Stability</span>
                    </div>
                    <div className="feature-item">
                        <FaFileContract className="feat-icon"/>
                        <span>Patent Free</span>
                    </div>
                </div>

                <div ref={bottomRef}></div>
            </div>
        </div>
    );
}
export default InputPrompt;