// Toggle Password Visibility
const togglePasswordBtn = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');

if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', function() {
        const icon = this.querySelector('i');
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });
}

// Form Validation
const loginForm = document.querySelector('.login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        
        // Simple email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailInput.value.trim()) {
            e.preventDefault();
            alert('Veuillez entrer votre adresse email');
            emailInput.focus();
            return;
        }
        
        if (!emailRegex.test(emailInput.value)) {
            e.preventDefault();
            alert('Veuillez entrer une adresse email valide');
            emailInput.focus();
            return;
        }
        
        if (!passwordInput.value.trim()) {
            e.preventDefault();
            alert('Veuillez entrer votre mot de passe');
            passwordInput.focus();
            return;
        }
        
        if (passwordInput.value.length < 6) {
            e.preventDefault();
            alert('Le mot de passe doit contenir au moins 6 caractères');
            return;
        }
    });
}

// Social Login Handlers
const socialButtons = document.querySelectorAll('.social-btn');
socialButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const platform = this.classList.contains('facebook') ? 'Facebook' : 'Google';
        console.log('Connexion avec ' + platform);
        // Intégration future avec OAuth
    });
});

// Forgot Password
const forgotPasswordLink = document.querySelector('.forgot-password');
if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Fonctionnalité "Mot de passe oublié" - À implémenter');
        // Redirection vers page réinitialisation mot de passe
    });
}

// Auto-fill password field focus effect
const formInputs = document.querySelectorAll('.form-input');
formInputs.forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.classList.remove('focused');
    });
});

// Animations on page load
window.addEventListener('load', function() {
    document.querySelector('.login-form-wrapper').style.animation = 'fadeInUp 0.6s ease';
    document.querySelector('.login-logo-section').style.animation = 'fadeInDown 0.6s ease';
});

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
