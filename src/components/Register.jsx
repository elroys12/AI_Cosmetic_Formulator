import React, { useState, useEffect, useRef } from "react";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import SuccessModal from "./SuccessModal";
import ErrorModal from "./ErrorModal";
import { authAPI } from "../api";

function Register({ onSwitchToLogin, isLanding, setIsLanding }) {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');   
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [errors, setErrors] = useState({
        username: '', email: '', password: '', confirmPassword: ''
    });
    const [showSuccess, setShowSuccess] = useState(false);
    const [showError, setShowError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const passwordInputRef = useRef(null);
    const confirmPasswordInputRef = useRef(null);

    useEffect(() => {
        let newErrors = { username: '', email: '', password: '', confirmPassword: '' };
        if (username && (username.length < 3 || username.length > 10)) newErrors.username = "Must be 3 - 10 characters";
        if (email && (!email.includes('@') || !email.includes('.'))) newErrors.email = "Invalid email";
        if (password) {
            if (password.length < 8 || password.length > 72) newErrors.password = "Must be 8 - 72 characters"; 
        }
        if (confirmPassword && password !== confirmPassword) newErrors.confirmPassword = "Passwords do not match";
        setErrors(newErrors);
    }, [username, email, password, confirmPassword]);

    const handleRegister = async () => {  
        if (errors.username || errors.email || errors.password || errors.confirmPassword || !username || !email || !password) {
            setErrorMessage("Please fill in the form correctly.");
            setShowError(true); return;
        }

        setIsLoading(true);

        try {
            await authAPI.register({username, email, password});
            localStorage.setItem('username', username);
            setShowSuccess(true);
            setTimeout(() => { 
                setShowSuccess(false); 
                onSwitchToLogin(); 
            }, 1500);
            
        } catch (error) {
            setErrorMessage(error.response?.data?.detail || "Registration Failed! Please try again.");
            setShowError(true);
        } finally { setIsLoading(false); }
    }

    const toggleVisibility = (e, ref, stateSetter) => {
        e.preventDefault();
        const input = ref.current;
        if (!input) return;
        const cursorPosition = input.selectionStart;
        stateSetter(prev => !prev);
        setTimeout(() => {
            if (input) {
                input.focus();
                input.setSelectionRange(cursorPosition, cursorPosition);
            }
        }, 0);
    };

    return (
        <div className={`login-page-wrapper ${isLanding ? 'landing-mode' : 'access-mode'}`}>
            
            {showSuccess && <SuccessModal message="Account Created Successfully!" />}
            {showError && <ErrorModal message={errorMessage} onClose={() => setShowError(false)} />}

            <div className="left-sidebar">
                <div 
                    className="accenture-trigger" 
                    onClick={() => setIsLanding(!isLanding)}
                    title={isLanding ? "Start Registration" : "Back"}
                >
                    <span className="icon-content">&gt;</span>
                </div>
            </div>

            <div className="right-sidebar">
                <div className="auth-container">
                    <h1>Join the Discovery</h1>
                    <div className="auth-form">
                        <div className="form-row">
                            <div className="form-group">
                                <label>Username</label>
                                <input type="text" placeholder=" Create your username" value={username} onChange={(e)=> setUsername(e.target.value)} style={errors.username ? {borderColor: '#ff4d4d'} : {}} />
                                <span className="field-error">{errors.username}</span>
                            </div>
                            <div className="form-group">
                                <label>Email</label>
                                <input type="email" placeholder="Enter your email" value={email} onChange={(e)=> setEmail(e.target.value)} style={errors.email ? {borderColor: '#ff4d4d'} : {}} />
                                <span className="field-error">{errors.email}</span>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Password</label>
                            <div className="password-wrapper">
                                <input ref={passwordInputRef} type={showPassword ? 'text' : 'password'} placeholder="Create your new password" value={password} onChange={(e)=> setPassword(e.target.value)} style={errors.password ? {borderColor: '#ff4d4d'} : {}} />
                                <button type="button" className="eye-icon" onClick={(e) => toggleVisibility(e, passwordInputRef, setShowPassword)} onMouseDown={(e) => e.preventDefault()}>
                                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                            <span className="field-error">{errors.password}</span>
                        </div>

                        <div className="form-group">
                            <label>Confirm Password</label>
                            <div className="password-wrapper">
                                <input ref={confirmPasswordInputRef} type={showConfirmPassword ? 'text' : 'password'} placeholder="Confirm your password" value={confirmPassword} onChange={(e)=> setConfirmPassword(e.target.value)} style={errors.confirmPassword ? {borderColor: '#ff4d4d'} : {}} />
                                <button type="button" className="eye-icon" onClick={(e) => toggleVisibility(e, confirmPasswordInputRef, setShowConfirmPassword)} onMouseDown={(e) => e.preventDefault()}>
                                    {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                            <span className="field-error">{errors.confirmPassword}</span>
                        </div>

                        <button onClick={handleRegister} disabled={isLoading} style={{marginTop: '10px'}}>
                            {isLoading ? "Creating Account..." : "Register Account"}
                        </button>
                    </div>
        
                    <p>Already have an account?
                        <button className="link-button" onClick={onSwitchToLogin}>Sign in</button>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default Register;