const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const sessionSelect = document.getElementById('session');
const loginBtn = document.getElementById('login-btn');
const shutdownBtn = document.getElementById('shutdown-btn');
const timeElement = document.getElementById('time');
const dateElement = document.getElementById('date');

let isAuthenticating = false;
let currentUser = null;

const lightdm = window.lightdm;

function initializeGreeter() {
    console.log('Initializing greeter...');
    console.log('LightDM available:', !!lightdm);
    
    if (lightdm) {
        if (lightdm.users && lightdm.users.length > 0) {
            console.log('Users found:', lightdm.users.map(u => u.username));
            // Optional: Create user list if you want clickable users
        } else {
            // Set default username if available
            usernameInput.value = '';
        }
        
        setupLightDMEventHandlers();
    } else {
        console.warn('LightDM API not available - running in demo mode');
        showError('LightDM API not available - Demo Mode');
    }
    
    populateSessions();
    
    updateDateTime();
    setInterval(updateDateTime, 1000);
    
    setTimeout(() => {
        usernameInput.focus();
        usernameInput.select();
    }, 500);
}

function setupLightDMEventHandlers() {
    if (!lightdm) return;
    
    // Authentication complete callback
    window.authentication_complete = function() {
        console.log('Authentication complete callback');
        console.log('is_authenticated:', lightdm.is_authenticated);
        
        if (lightdm.is_authenticated) {
            handleSuccessfulAuth();
        } else {
            handleFailedAuth('Authentication failed');
        }
    };
    
    // Authentication prompt callback
    window.show_prompt = function(text, type) {
        console.log('Prompt:', text, type);
        // Could show this in UI if needed
    };
    
    // Authentication message callback
    window.show_message = function(text, type) {
        console.log('Message:', text, type);
        if (type === 1) { // Error type
            showError(text);
        }
    };
}

function populateSessions() {
    console.log('Populating sessions...');
    
    // Clear existing options
    sessionSelect.innerHTML = '';
    
    let sessions = [];
    
    if (lightdm && lightdm.sessions && lightdm.sessions.length > 0) {
        sessions = lightdm.sessions;
        console.log('Available sessions:', sessions);
    } else {
        // Fallback sessions for demo
        sessions = [
            { key: 'awesome', name: 'AwesomeWM' },
            { key: 'xfce', name: 'XFCE' }
        ];
    }
    
    sessions.forEach(session => {
        const option = document.createElement('option');
        option.value = session.key;
        option.textContent = session.name;
        sessionSelect.appendChild(option);
    });
    
    // Set default session
    if (lightdm && lightdm.default_session) {
        sessionSelect.value = lightdm.default_session;
    } else {
        // Try to find awesome or set first
        const awesomeOption = Array.from(sessionSelect.options).find(
            opt => opt.value.toLowerCase().includes('awesome')
        );
        sessionSelect.value = awesomeOption ? awesomeOption.value : sessions[0].key;
    }
}

function updateDateTime() {
    const now = new Date();
    
    const time = now.toLocaleTimeString('en-GB', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const date = now.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
    
    if (timeElement) timeElement.textContent = time;
    if (dateElement) dateElement.textContent = date;
}

function handleLogin() {
    if (isAuthenticating) return;
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    const session = sessionSelect.value;
    
    if (!username) {
        showError('Please enter username');
        usernameInput.focus();
        return;
    }
    
    if (!password) {
        showError('Please enter password');
        passwordInput.focus();
        return;
    }
    
    console.log('Attempting login:', { username, session });
    
    // Update UI
    isAuthenticating = true;
    loginBtn.innerHTML = '<i class="fas fa-cog fa-spin"></i> AUTHENTICATING...';
    loginBtn.disabled = true;
    
    // If LightDM is not available, simulate login
    if (!lightdm) {
        console.log('LightDM not available - simulating login');
        setTimeout(() => {
            if (username && password) {
                handleSuccessfulAuth();
            } else {
                handleFailedAuth();
            }
        }, 1500);
        return;
    }
    
    // Real LightDM authentication flow
    try {
        // Cancel any ongoing authentication
        if (lightdm.cancel_authentication) {
            lightdm.cancel_authentication();
        }
        
        // Start authentication
        if (lightdm.authenticate) {
            lightdm.authenticate(username);
        }
        
        // Give a moment for authentication to start, then respond with password
        setTimeout(() => {
            if (lightdm.respond) {
                lightdm.respond(password);
            }
            
            // The authentication_complete callback will handle the result
            // But add a timeout fallback in case callback doesn't fire
            setTimeout(() => {
                if (isAuthenticating) {
                    console.log('Authentication timeout');
                    if (lightdm.is_authenticated) {
                        handleSuccessfulAuth();
                    } else {
                        handleFailedAuth('Authentication timeout');
                    }
                }
            }, 5000);
        }, 100);
        
    } catch (error) {
        console.error('Authentication error:', error);
        handleFailedAuth('Authentication error: ' + error.message);
    }
}

// Handle successful authentication
function handleSuccessfulAuth() {
    if (!isAuthenticating) return;
    
    console.log('Authentication successful!');
    
    // Update UI
    loginBtn.innerHTML = '<i class="fas fa-check"></i> SUCCESS!';
    loginBtn.style.background = '#0a0';
    loginBtn.style.borderColor = '#0a0';
    
    // Start session
    setTimeout(() => {
        const session = sessionSelect.value;
        console.log('Starting session:', session);
        
        if (lightdm && lightdm.start_session_sync) {
            try {
                lightdm.start_session_sync(session);
                // If we get here without error, session started
                console.log('Session start command sent');
                
                // Update UI to show session is starting
                loginBtn.innerHTML = '<i class="fas fa-play"></i> STARTING SESSION...';
                
            } catch (error) {
                console.error('Session start error:', error);
                handleFailedAuth('Session start failed: ' + error.message);
            }
        } else {
            console.error('No session start function available');
            showError('Cannot start session - LightDM API missing');
            resetLoginForm();
        }
    }, 500);
}

function handleFailedAuth(message = 'Authentication failed') {
    console.log('Authentication failed:', message);
    
    loginBtn.innerHTML = '<i class="fas fa-times"></i> FAILED';
    loginBtn.style.background = '#a00';
    loginBtn.style.borderColor = '#a00';
    
    showError(message);
    
    setTimeout(() => {
        resetLoginForm();
        passwordInput.value = '';
        passwordInput.focus();
    }, 2000);
}

function resetLoginForm() {
    isAuthenticating = false;
    loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> LOGIN';
    loginBtn.style.background = '';
    loginBtn.style.borderColor = '';
    loginBtn.disabled = false;
}

function showError(message) {
    let errorEl = document.getElementById('error-message');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.id = 'error-message';
        errorEl.className = 'error-message';
        document.querySelector('.login-form').appendChild(errorEl);
    }
    
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 3000);
}

function handlePowerAction(action) {
    console.log('Power action:', action);
    
    if (!lightdm) {
        showError('Power management not available in demo');
        return;
    }
    
    switch(action) {
        case 'shutdown':
            if (lightdm.shutdown) lightdm.shutdown();
            break;
        case 'restart':
            if (lightdm.restart) lightdm.restart();
            break;
        case 'suspend':
            if (lightdm.suspend) lightdm.suspend();
            break;
        case 'hibernate':
            if (lightdm.hibernate) lightdm.hibernate();
            break;
        default:
            showError('Unknown power action');
    }
}

document.addEventListener('DOMContentLoaded', initializeGreeter);

if (loginBtn) {
    loginBtn.addEventListener('click', handleLogin);
}

if (usernameInput) {
    usernameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            passwordInput.focus();
        }
    });
}

if (passwordInput) {
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin();
        }
    });
}

// Add some CSS for error messages
const errorStyle = document.createElement('style');
errorStyle.textContent = `
.error-message {
    background: rgba(255, 0, 0, 0.1);
    border: 1px solid #f00;
    color: #f00;
    padding: 10px;
    margin: 10px 0;
    font-family: monospace;
    display: none;
    animation: glitch 0.5s;
}
`;
document.head.appendChild(errorStyle);
