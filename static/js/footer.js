// Footer Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const firstname = document.querySelector('input[name="firstname"]');
            const lastname = document.querySelector('input[name="lastname"]');
            const email = document.querySelector('input[name="email"]');
            const terms = document.querySelector('input[name="terms"]');
            
            // Validation simple
            if (!firstname.value.trim()) {
                alert('Veuillez entrer votre prénom');
                firstname.focus();
                return;
            }
            
            if (!lastname.value.trim()) {
                alert('Veuillez entrer votre nom');
                lastname.focus();
                return;
            }
            
            if (!email.value.trim()) {
                alert('Veuillez entrer votre email');
                email.focus();
                return;
            }
            
            // Validation email simple
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value)) {
                alert('Veuillez entrer un email valide');
                email.focus();
                return;
            }
            
            if (!terms.checked) {
                alert('Veuillez accepter les conditions d\'utilisation');
                terms.focus();
                return;
            }
            
            // Afficher un message de succès
            const button = this.querySelector('.btn-subscribe');
            const originalText = button.textContent;
            button.textContent = '✓ Inscription réussie !';
            button.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
            
            // Réinitialiser après 2 secondes
            setTimeout(() => {
                newsletterForm.reset();
                button.textContent = originalText;
                button.style.background = '';
            }, 2000);
        });
    }
});

// Animation de scroll pour les éléments du footer
window.addEventListener('scroll', function() {
    const footer = document.querySelector('.footer');
    if (footer) {
        const footerPosition = footer.getBoundingClientRect().top;
        const screenPosition = window.innerHeight;
        
        if (footerPosition < screenPosition) {
            footer.style.opacity = '1';
            footer.style.animation = 'fadeInUp 0.6s ease';
        }
    }
});

// Animation fadeInUp
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
`;
document.head.appendChild(style);
