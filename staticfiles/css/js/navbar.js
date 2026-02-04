// Dropdowns interactifs
document.addEventListener('DOMContentLoaded', function() {
    // Adresse dropdown
    const addressTrigger = document.querySelector('.address-trigger');
    const addressDropdown = document.querySelector('.address-dropdown');
    
    if (addressTrigger && addressDropdown) {
        addressTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            addressDropdown.style.display = 
                addressDropdown.style.display === 'block' ? 'none' : 'block';
        });
    }
    
    // User dropdown
    const userMenu = document.querySelector('.user-menu');
    const userDropdown = document.querySelector('.user-dropdown');
    
    if (userMenu && userDropdown) {
        userMenu.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.style.display = 
                userDropdown.style.display === 'block' ? 'none' : 'block';
        });
    }
    
    // Fermer les dropdowns en cliquant ailleurs
    document.addEventListener('click', function() {
        if (addressDropdown) addressDropdown.style.display = 'none';
        if (userDropdown) userDropdown.style.display = 'none';
    });
    
    // Animation du compteur panier
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        setInterval(() => {
            cartCount.style.transform = 'scale(1.1)';
            setTimeout(() => {
                cartCount.style.transform = 'scale(1)';
            }, 300);
        }, 3000);
    }
    
    // Animation des catégories
    const categoryLinks = document.querySelectorAll('.category-link');
    categoryLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});