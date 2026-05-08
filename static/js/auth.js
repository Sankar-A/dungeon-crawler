// Authentication state
let currentUser = null;
let userCharacters = [];
let confirmationModalOpen = false; // Track if confirmation modal is open

// Confirmation modal handler
function showConfirmation(title, message, onConfirm) {
    const modal = document.getElementById('confirm-modal');
    const titleEl = document.getElementById('confirm-title');
    const messageEl = document.getElementById('confirm-message');
    const yesBtn = document.getElementById('confirm-yes');
    const noBtn = document.getElementById('confirm-no');
    
    titleEl.textContent = title;
    messageEl.textContent = message;
    modal.classList.add('active');
    confirmationModalOpen = true; // Set flag
    
    // Remove old listeners
    const newYesBtn = yesBtn.cloneNode(true);
    const newNoBtn = noBtn.cloneNode(true);
    yesBtn.parentNode.replaceChild(newYesBtn, yesBtn);
    noBtn.parentNode.replaceChild(newNoBtn, noBtn);
    
    const closeModal = () => {
        modal.classList.remove('active');
        confirmationModalOpen = false; // Clear flag
        document.removeEventListener('keydown', keyHandler);
    };
    
    // Add new listeners
    newYesBtn.addEventListener('click', () => {
        closeModal();
        if (onConfirm) onConfirm();
    });
    
    newNoBtn.addEventListener('click', () => {
        closeModal();
    });
    
    // Keyboard shortcuts: E/Enter for Yes, X/Escape for No
    const keyHandler = (e) => {
        const key = e.key.toLowerCase();
        if (key === 'e' || key === 'enter') {
            e.preventDefault();
            closeModal();
            if (onConfirm) onConfirm();
        } else if (key === 'x' || key === 'escape') {
            e.preventDefault();
            closeModal();
        }
    };
    document.addEventListener('keydown', keyHandler);
}

// Alert modal handler (uses confirmation modal with only OK button)
function showAlert(title, message) {
    const modal = document.getElementById('confirm-modal');
    const titleEl = document.getElementById('confirm-title');
    const messageEl = document.getElementById('confirm-message');
    const yesBtn = document.getElementById('confirm-yes');
    const noBtn = document.getElementById('confirm-no');
    
    titleEl.textContent = title;
    messageEl.textContent = message;
    modal.classList.add('active');
    
    // Hide No button, show only Yes as OK
    noBtn.style.display = 'none';
    yesBtn.textContent = 'OK';
    
    // Remove old listeners
    const newYesBtn = yesBtn.cloneNode(true);
    yesBtn.parentNode.replaceChild(newYesBtn, yesBtn);
    
    // Add new listener
    newYesBtn.addEventListener('click', () => {
        modal.classList.remove('active');
        noBtn.style.display = 'block';
        yesBtn.textContent = 'Yes';
        document.removeEventListener('keydown', keyHandler);
    });
    
    // Close on escape or enter
    const keyHandler = (e) => {
        if (e.key === 'Escape' || e.key === 'Enter' || e.key.toLowerCase() === 'e') {
            e.preventDefault();
            modal.classList.remove('active');
            noBtn.style.display = 'block';
            yesBtn.textContent = 'Yes';
            document.removeEventListener('keydown', keyHandler);
        }
    };
    document.addEventListener('keydown', keyHandler);
}

// Screen management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 5000);
}

// Initialize auth handlers
function initAuth() {
    // Show/hide forms
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'block';
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('register-form').style.display = 'none';
        document.getElementById('login-form').style.display = 'block';
    });

    // Login
    document.getElementById('login-btn').addEventListener('click', () => {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;

        if (!username || !password) {
            showError('auth-error', 'Please enter username and password');
            return;
        }

        socket.emit('login', { username, password });
    });

    // Register
    document.getElementById('register-btn').addEventListener('click', () => {
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-password-confirm').value;

        if (!username || username.length < 3 || username.length > 50) {
            showError('auth-error', 'Username must be 3-50 characters');
            return;
        }

        if (!password || password.length < 6) {
            showError('auth-error', 'Password must be at least 6 characters');
            return;
        }

        if (password !== confirmPassword) {
            showError('auth-error', 'Passwords do not match');
            return;
        }

        socket.emit('register', { username, password });
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        currentUser = null;
        userCharacters = [];
        showScreen('login-screen');
    });

    // Character selection
    document.getElementById('create-character-btn').addEventListener('click', () => {
        if (userCharacters.length >= 10) {
            showAlert('Character Limit', 'Maximum 10 characters per account');
            return;
        }
        showScreen('character-creation-screen');
    });

    document.getElementById('back-to-select-btn').addEventListener('click', () => {
        showScreen('character-select-screen');
    });

    // Character creation
    document.getElementById('create-btn').addEventListener('click', () => {
        const name = document.getElementById('character-name').value.trim();

        if (!name || name.length < 1 || name.length > 10) {
            showError('creation-error', 'Character name must be 1-10 characters');
            return;
        }

        socket.emit('create_character', { name });
    });

    // Enter key handlers
    document.getElementById('login-password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') document.getElementById('login-btn').click();
    });

    document.getElementById('register-password-confirm').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') document.getElementById('register-btn').click();
    });

    document.getElementById('character-name').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') document.getElementById('create-btn').click();
    });
}

// Socket event handlers
function setupAuthSocketHandlers() {
    socket.on('register_success', (data) => {
        currentUser = data.user;
        userCharacters = [];
        
        // Show guest mode indicator if applicable
        if (data.guest_mode) {
            showAlert('Guest Mode', 'Database is disabled. Playing in guest mode - progress will not be saved.');
        }
        
        showScreen('character-select-screen');
        renderCharacterList();
    });

    socket.on('register_failed', (data) => {
        showError('auth-error', data.reason);
    });

    socket.on('login_success', (data) => {
        currentUser = data.user;
        userCharacters = data.characters;
        
        // Show guest mode indicator if applicable
        if (data.guest_mode) {
            showAlert('Guest Mode', 'Database is disabled. Playing in guest mode - progress will not be saved.');
        }
        
        showScreen('character-select-screen');
        renderCharacterList();
    });

    socket.on('login_failed', (data) => {
        showError('auth-error', data.reason);
    });

    socket.on('auth_required', (data) => {
        showError('auth-error', 'Please login first');
        showScreen('login-screen');
    });

    socket.on('character_creation_failed', (data) => {
        showError('creation-error', data.reason);
    });

    socket.on('characters_list', (data) => {
        userCharacters = data.characters;
        renderCharacterList();
    });

    socket.on('character_deleted', (data) => {
        userCharacters = userCharacters.filter(c => c.name !== data.name);
        renderCharacterList();
    });
}

// Render character list
function renderCharacterList() {
    const listEl = document.getElementById('character-list');
    listEl.innerHTML = '';

    if (userCharacters.length === 0) {
        listEl.innerHTML = '<p style="color: #bbb;">No characters yet. Create your first hero!</p>';
        return;
    }

    userCharacters.forEach(char => {
        const card = document.createElement('div');
        card.className = 'character-card';
        card.innerHTML = `
            <h3>${char.name}</h3>
            <div class="char-stat">Level: ${char.level}</div>
            <div class="char-stat">Floor: ${char.floor}</div>
            <div class="char-stat">Gold: ${char.gold}</div>
            <div class="char-actions">
                <button class="play-char" data-name="${char.name}">Play</button>
                <button class="delete-char" data-name="${char.name}">Delete</button>
            </div>
        `;

        // Play character
        card.querySelector('.play-char').addEventListener('click', (e) => {
            e.stopPropagation();
            console.log('Loading character:', char.name);
            socket.emit('create_character', { name: char.name });
        });

        // Delete character
        card.querySelector('.delete-char').addEventListener('click', (e) => {
            e.stopPropagation();
            showConfirmation(
                'Delete Character',
                `Are you sure you want to delete "${char.name}"? This action cannot be undone.`,
                () => {
                    socket.emit('delete_character', { name: char.name });
                }
            );
        });

        listEl.appendChild(card);
    });
}
