// ============================================
// NAVBAR INTERACTIONS & CART DYNAMIC UPDATE
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // 1. DROPDOWNS INTERACTIFS
    // ============================================
    
    // Adresse dropdown
    const addressTrigger = document.querySelector('.address-trigger');
    const addressDropdown = document.querySelector('.address-dropdown');
    
    if (addressTrigger && addressDropdown) {
        addressTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDropdown(addressDropdown);
        });
    }
    
    // User dropdown
    const userProfileLink = document.querySelector('.user-profile-link');
    const userDropdownMenu = document.querySelector('.user-dropdown-menu');
    
    if (userProfileLink && userDropdownMenu) {
        userProfileLink.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDropdown(userDropdownMenu);
        });
    }
    
    // Fermer tous les dropdowns en cliquant ailleurs
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.address-trigger') && addressDropdown) {
            addressDropdown.style.display = 'none';
        }
        
        if (!e.target.closest('.user-profile-link') && userDropdownMenu) {
            userDropdownMenu.style.display = 'none';
        }
    });
    
    // ============================================
    // 2. FONCTION DE TOGGLE POUR DROPDOWNS
    // ============================================
    
    function toggleDropdown(element) {
        const isVisible = element.style.display === 'block';
        // Fermer tous les dropdowns
        document.querySelectorAll('.address-dropdown, .user-dropdown-menu').forEach(dropdown => {
            dropdown.style.display = 'none';
        });
        // Ouvrir celui demandé
        if (!isVisible) {
            element.style.display = 'block';
        }
    }
    
    // ============================================
    // 3. MISE À JOUR DYNAMIQUE DU PANIER
    // ============================================
    
    // Fonction pour récupérer le nombre d'articles dans le panier
    async function updateCartCount() {
        try {
            const response = await fetch('/api/cart-count/');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const cartCount = document.getElementById('cartCount');
                    if (cartCount) {
                        const oldCount = parseInt(cartCount.textContent);
                        const newCount = data.count;
                        
                        // Mettre à jour le compteur
                        cartCount.textContent = newCount;
                        
                        // Animation si le nombre a changé
                        if (oldCount !== newCount) {
                            triggerCartAnimation(cartCount, oldCount, newCount);
                        }
                        
                        return newCount;
                    }
                }
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour du panier:', error);
        }
        return null;
    }
    
    // Animation du compteur de panier
    function triggerCartAnimation(element, oldCount, newCount) {
        // Ajouter des classes pour l'animation
        element.classList.add('cart-count-updating');
        
        // Afficher une notification si un produit a été ajouté
        if (newCount > oldCount) {
            const added = newCount - oldCount;
            showNotification(`+${added} article${added > 1 ? 's' : ''} ajouté${added > 1 ? 's' : ''} au panier !`, 'success');
        }
        
        // Retirer la classe après l'animation
        setTimeout(() => {
            element.classList.remove('cart-count-updating');
        }, 500);
    }
    
    // Mettre à jour le compteur au chargement de la page
    updateCartCount();
    
    // Mettre à jour le compteur périodiquement (toutes les 30 secondes)
    setInterval(updateCartCount, 30000);
    
    // Exposer la fonction globalement
    window.updateCartCount = updateCartCount;
    
    // ============================================
    // 4. FONCTION POUR AJOUTER AU PANIER
    // ============================================
    
    // Fonction utilitaire pour récupérer le CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Fonction pour ajouter un produit au panier
    window.addToCart = async function(productId, quantity = 1) {
        try {
            const response = await fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Mettre à jour le compteur du panier
                if (typeof window.updateCartCount === 'function') {
                    window.updateCartCount();
                }
                
                // Afficher une notification de succès
                showNotification(data.message || 'Produit ajouté au panier !', 'success');
                
                return true;
            } else {
                showNotification(data.message || 'Erreur lors de l\'ajout au panier', 'error');
                return false;
            }
        } catch (error) {
            console.error('Erreur:', error);
            showNotification('Une erreur est survenue', 'error');
            return false;
        }
    };
    
    // ============================================
    // 5. SYSTÈME DE NOTIFICATIONS
    // ============================================
    
    function showNotification(message, type = 'info') {
        // Créer une notification toast
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Ajouter au body
        document.body.appendChild(notification);
        
        // Ajouter la classe pour l'animation d'entrée
        setTimeout(() => {
            notification.classList.add('notification-show');
        }, 10);
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            notification.classList.add('notification-hide');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    // ============================================
    // 6. ANIMATION DES CATÉGORIES
    // ============================================
    
    const categoryLinks = document.querySelectorAll('.category-link');
    categoryLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = 'none';
        });
    });
    
    // ============================================
    // 7. BOUTONS "AJOUTER AU PANIER"
    // ============================================
    
    // Gérer les clics sur les boutons "Ajouter au panier"
    document.querySelectorAll('.add-to-cart, .btn-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.getAttribute('data-product-id') || 
                             this.closest('[data-product-id]').getAttribute('data-product-id');
            
            if (productId) {
                // Appeler la fonction d'ajout au panier
                window.addToCart(productId, 1);
            }
        });
    });
    
    // ============================================
    // 8. STYLES POUR LES ANIMATIONS ET NOTIFICATIONS
    // ============================================
    
    // Ajouter les styles nécessaires
    const style = document.createElement('style');
    style.textContent = `
        /* Animation du compteur de panier */
        .cart-count {
            background-color: #D32F2F;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 700;
            min-width: 20px;
            text-align: center;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .cart-count-updating {
            animation: cartCountBounce 0.5s ease;
            background-color: #D4AF37 !important;
            color: #5D4037 !important;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
        }
        
        @keyframes cartCountBounce {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.3);
            }
        }
        
        /* Notifications toast */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            z-index: 9999;
            transform: translateX(400px);
            opacity: 0;
            transition: all 0.3s ease;
        }
        
        .notification-show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .notification-hide {
            transform: translateX(400px);
            opacity: 0;
        }
        
        .notification-success {
            border-left: 4px solid #4CAF50;
            color: #4CAF50;
        }
        
        .notification-error {
            border-left: 4px solid #D32F2F;
            color: #D32F2F;
        }
        
        .notification-info {
            border-left: 4px solid #2196F3;
            color: #2196F3;
        }
        
        /* Hover effect amélioré pour les catégories */
        .category-link {
            transition: all 0.3s ease !important;
        }
    `;
    document.head.appendChild(style);
    
    // ============================================
    // 9. ACCESSIBILITÉ ET CLAVIER
    // ============================================
    
    // Fermer les dropdowns avec la touche ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (addressDropdown) addressDropdown.style.display = 'none';
            if (userDropdownMenu) userDropdownMenu.style.display = 'none';
        }
    });
    
    console.log('Navbar JavaScript chargé avec succès ✅');
});