// Auth utilities
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/me', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
    return null;
}

async function logoutUser() {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        localStorage.removeItem('user');
        window.location.href = '/';
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

function updateNavBar() {
    checkAuthStatus().then(user => {
        if (user) {
            document.getElementById('loginBtn').style.display = 'none';
            document.getElementById('registerBtn').style.display = 'none';
            document.getElementById('dashboardBtn').style.display = 'block';
            document.getElementById('logoutBtn').style.display = 'block';
        } else {
            document.getElementById('loginBtn').style.display = 'block';
            document.getElementById('registerBtn').style.display = 'block';
            document.getElementById('dashboardBtn').style.display = 'none';
            document.getElementById('logoutBtn').style.display = 'none';
        }
    });
}

// Update navbar on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateNavBar);
} else {
    updateNavBar();
}

// Logout button event listeners
document.querySelectorAll('#logoutBtn').forEach(btn => {
    btn.addEventListener('click', logoutUser);
});
