import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";
import { dataAPI } from "./api";

// Component Imports
import Header from "./components/Header.jsx";
import Login from "./components/Login.jsx";
import Register from "./components/Register.jsx";
import InputPrompt from "./components/InputPrompt.jsx";
import RecommendResult from "./components/RecommendResult.jsx";
import HistoryLog from "./components/HistoryLog.jsx";
import DetailHistory from "./components/DetailHistory.jsx";

import './App.css';

function App() {
    const navigate = useNavigate();
    const location = useLocation();
    
    const [isLanding, setIsLanding] = useState(true);

    const [isLoggedIn, setIsLoggedIn] = useState(() => {
        return localStorage.getItem('token') !== null;
    });

    const [username, setUsername] = useState(() => {
        return localStorage.getItem('username') || 'Researcher'; 
    });

    const [currentResult, setCurrentResult] = useState(null);
    const [historyList, setHistoryList] = useState([]);
    const [isDeleting, setIsDeleting] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        setIsLoggedIn(false);
        setIsLanding(true); 
        navigate('/login');
    };

    const fetchHistory = async () => {
        try {
            console.log("Fetching history from Database...");
            const data = await dataAPI.getHistory(); 
            
            const historyData = Array.isArray(data) ? data : (data.history || []); 
            
            console.log("History loaded:", historyData);
            setHistoryList(historyData);
        } catch (error) {
            console.error("Failed to fetch history:", error);
            if (error.response && error.response.status === 401) {
                handleLogout(); 
            }
        }
    };

    useEffect(() => {
        if (isLoggedIn) {
            fetchHistory(); 
        }
    }, [isLoggedIn]);

    const handleLoginSuccess = () => {
        setIsLoggedIn(true);
        setUsername(localStorage.getItem('username') || 'Researcher');
        navigate('/');
    };

    const handleSearchSuccess = (resultData) => {
        setCurrentResult(resultData); 
        fetchHistory();
        navigate('/result'); 
    };

    const handleDeleteHistory = async (id) => {
        setIsDeleting(true); 

        try {
            await dataAPI.deleteHistory(id); 
            
            await fetchHistory(); 
            navigate('/history');
        } catch (error) {
            console.error("Error deleting history:", error);
        } finally {
            setIsDeleting(false); 
        }
    };

    const isAuthPage = location.pathname === '/login' || location.pathname === '/register'; 

    return (
        <div className="app-container">
        
            {isLoggedIn && !isAuthPage && (
                <Header 
                    title="Novel Chemicals Discovery Agent" 
                    username={username}
                    onLogout={handleLogout}
                    onNavigate={(path) => navigate(path)}
                />
            )}
               
            <main 
                className={isLoggedIn ? "page-transition" : ""}
                style={isAuthPage ? { maxWidth: '100%', padding: 0, margin: 0 } : {}}
            >
                <Routes>                  
                    <Route path="/login" element={
                        !isLoggedIn ? (
                            <Login 
                                onLoginClick={handleLoginSuccess} 
                                onSwitchToRegister={() => navigate('/register')}
                                isLanding={isLanding}
                                setIsLanding={setIsLanding}
                            />
                        ) : <Navigate to="/" />
                    } />

                    <Route path="/register" element={
                        !isLoggedIn ? (
                            <Register 
                                onSwitchToLogin={() => navigate('/login')}
                                isLanding={isLanding}
                                setIsLanding={setIsLanding}
                            />
                        ) : <Navigate to="/" />
                    } />
                  
                    <Route path="/" element={
                        isLoggedIn ? (
                            <InputPrompt 
                                onSearchSuccess={handleSearchSuccess} 
                             />
                        ) : <Navigate to="/login" />
                    } />

                    <Route path="/result" element={
                        isLoggedIn ? (
                            currentResult ? (
                                <RecommendResult 
                                    {...currentResult} 
                                    onBack={() => navigate('/')} 
                                />
                            ) : <Navigate to="/" />
                        ) : <Navigate to="/login" />
                    } />

                    <Route path="/history" element={
                        isLoggedIn ? (
                            <HistoryLog
                                historyList={historyList} 
                                onItemClick={(item) => navigate(`/history/${item.id}`)}
                            />
                        ) : <Navigate to="/login" />
                    } />

                    <Route path="/history/:id" element={
                        isLoggedIn ? (
                            <HistoryWrapper 
                                historyList={historyList}
                                onDelete={handleDeleteHistory}
                                isDeleting={isDeleting}
                                onBack={() => navigate('/history')}
                            />
                        ) : <Navigate to="/login" />
                    } />
                </Routes>
            </main>
        </div>
    );
}

function HistoryWrapper({ historyList, onDelete, onBack, isDeleting }) {
    const { id } = useParams(); 
    
    if (historyList === null) { 
        return <div style={{color:'white', padding: 40, textAlign:'center'}}>
            <FaAtom className="atom-spin" style={{fontSize: '3rem', color: '#a435f0'}}/> 
            <p>Fetching archives...</p>
        </div>;
    }

    const item = historyList.find(h => h.id?.toString() === id); 

    if (!item) {
        
        if (historyList.length > 0) {
            return <div style={{color:'white', padding: 40, textAlign:'center'}}>
                        Error 404: History item with ID "{id}" not found. Maybe it was deleted?
                    </div>;
            }
    }

    return (
        <div>
            <DetailHistory 
                data={item} 
                onDelete={onDelete}
                onBack={onBack}
                isDeleting={isDeleting}
            />
        </div>
    );
}

export default App;