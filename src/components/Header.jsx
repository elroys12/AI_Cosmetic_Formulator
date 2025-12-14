import React, { useState, useEffect, useRef } from "react";
import { FaChevronDown, FaHistory, FaSignOutAlt, FaHome } from "react-icons/fa";

function Header({title, onLogout, onNavigate, username}) {
    const[isMenuOpen, setIsMenuOpen] = useState(false);

    const menuRef = useRef(null);

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    useEffect(() => {
        function handleClickOutside(event) {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setIsMenuOpen(false);
            }
        }

        document.addEventListener("mousedown", handleClickOutside);
        
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [menuRef]);

    return (
        <header>
            <div 
                className="header-logo"
                onClick={() => onNavigate('/')} 
                style={{ cursor: 'pointer'}}
            >
                {title}
            </div>

            <div className="user-menu-container" ref={menuRef}>
                <button
                    className="user-btn"
                    onClick={toggleMenu}
                >
                    <span style={{fontWeight: 'bold'}}>{username || "Researcher"}</span>
                    <FaChevronDown className={`arrow-icon ${isMenuOpen ? 'rotate' : ''}`} />
                </button>

                {isMenuOpen && (
                    <div className="dropdown-menu">
                        <div 
                            className="dropdown-item" 
                            onClick={() => {
                                setIsMenuOpen(false);
                                onNavigate('/'); 
                            }}
                        >
                            <FaHome /> Home
                        </div>

                        <div
                            className="dropdown-item" 
                            onClick={() => {
                                setIsMenuOpen(false); 
                                onNavigate('history');
                            }}
                        >
                            <FaHistory /> History
                        </div>

                        <div className="dropdown-divider"></div>

                        <div 
                            className="dropdown-item danger" 
                            onClick={() => {
                                setIsMenuOpen(false);
                                onLogout();
                            }}
                        >
                            <FaSignOutAlt /> Log Out
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
}

export default Header;