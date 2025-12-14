import React, { useState, useEffect, useRef } from 'react';
import { FaEye, FaEyeSlash } from "react-icons/fa";
import SuccessModal from "./SuccessModal";
import ErrorModal from "./ErrorModal";
import { authAPI } from '../api';

function Login({ onLoginClick, onSwitchToRegister, isLanding, setIsLanding }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false); 
    const [errors, setErrors] = useState({
        email: '',
        password: ''
    });
    const [showSuccess, setShowSuccess] = useState(false);
    const [showError, setShowError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const passwordInputRef = useRef(null);

    useEffect(() => {
        let newErrors = { email: '', password: '' };

        if (email) {
            if (!email.includes('@')) {
                newErrors.email = "Invalid email (Missing'@')";
            } 
        }

        if (password && password.length < 1) {
            newErrors.password = "Password cannot be empty";
        }

        setErrors(newErrors);
    },  [email, password]);

    const handleLogin = async () => {
        if (errors.email || errors.password || !email || !password) {
            setErrorMessage("Please enter a valid email and password.");
            setShowError(true);
            return;
        }

        setIsLoading(true);

        try {
            const data = await authAPI.login(email, password);
            localStorage.setItem('token', data.access_token);

            const realName = data.user?.full_name || data.user?.email?.split('@')[0] || "Researcher";
            
            localStorage.setItem('username', realName);
            
            console.log("Login Successfull:", realName);
            setShowSuccess(true);

            setTimeout(() => {
              setShowSuccess(false);
              onLoginClick(); 
            },3000);
        } catch (error) {
            console.error("Login Failed", error)

            const msg = error.response?.data?.detail || "Login Failed!! Check your email or password."

            setErrorMessage(msg);
            setShowError(true);
        } finally {
            setIsLoading(false);
        }
    };

    const togglePasswordVisibility = (e) => {
        e.preventDefault(); 
        
        const input = passwordInputRef.current;
        if (!input) return; 

        const cursorPosition = input.selectionStart;

        setShowPassword(prev => !prev);

        setTimeout(() => {
            if (input) {
                input.focus();
                input.setSelectionRange(cursorPosition, cursorPosition);
            }
        }, 0);
    };

    return (
        <div className={`login-page-wrapper ${isLanding ? 'landing-mode' : 'access-mode'}`}>
            
            {showSuccess && <SuccessModal message="Login Successfull! Redirecting..." />}
            {showError && <ErrorModal message={errorMessage} onClose={() => setShowError(false)} />}

            <div className="left-sidebar">               
                <div 
                    className="accenture-trigger" 
                    onClick={() => setIsLanding(!isLanding)}
                    title={isLanding ? "Enter Research Lab" : "Back to View"}
                >
                    <span className="icon-content">&gt;</span> 
                </div>

            </div>

            <div className='right-sidebar'>
                <div className='auth-container'>
                    <h1>Access your Research</h1>
                    <p>Please enter your credentials.</p>

                    <div className='auth-form'>
                        <div className="form-group">
                            <label>Email</label>
                            <input
                                type='email'
                                placeholder='Enter your registered email'
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                style={errors.email ? {borderColor: '#ff4d4d'} : {}}
                            />
                            <span className="field-error">{errors.email}</span>
                        </div>

                        <div className="form-group">
                            <label>Password</label>
                            <div className="password-wrapper">
                                <input
                                    ref={passwordInputRef}
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder='Enter your password'
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    style={errors.password ? {borderColor: '#ff4d4d'} : {}}
                                />
                                <button 
                                    type="button" className="eye-icon"
                                    onClick={togglePasswordVisibility}
                                    onMouseDown={(e) => e.preventDefault()}
                                >
                                    {showPassword ? <FaEyeSlash /> : <FaEye />} 
                                </button>
                            </div>
                            <span className="field-error">{errors.password}</span>
                        </div>

                        <button onClick={handleLogin} disabled={isLoading} style={{marginTop: '10px'}}>
                            {isLoading ? "Signing In..." : "Sign In"}
                        </button>
                    </div>

                    <p>New researcher? 
                        <button className='link-button' onClick={onSwitchToRegister}>
                            Create an account
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Login;