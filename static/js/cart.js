/**
 * Obidon - Gestion du Panier & Notifications
 * Ce fichier gère l'ajout au panier, la mise à jour des quantités et les notifications.
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Initialiser le compteur du panier au chargement de la page
    if (typeof window.updateCartCount === 'function') {
        window.updateCartCount();
    }

    // 2. Gérer les boutons "Ajouter au panier" sur les listes de produits (products.html, home.html)
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Empêche le clic sur la carte produit
            
            const productId = this.getAttribute('data-product-id');
            const quantity = 1;
            
            // Appel de la fonction globale
            if (typeof window.addToCart === 'function') {
                window.addToCart(productId, quantity, this);
            } else {
                alert("Erreur: Fonction panier non chargée.");
            }
        });
    });

    // 3. Si nous sommes sur la page Panier, gérer les boutons + / - et Supprimer
    const cartPage = document.querySelector('.cart-page');
    if (cartPage) {
        initCartPageListeners();
    }
});

/**
 * Fonction Globale d'ajout au panier
 * Utilisée par product_detail.html et les listes de produits
 */
window.addToCart = function(productId, quantity, buttonElement) {
    const csrftoken = getCookie('csrftoken');
    
    // Sauvegarder l'état original du bouton
    let originalContent = '';
    let isButton = buttonElement && buttonElement.tagName === 'BUTTON';
    
    if (isButton) {
        originalContent = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ...';
        buttonElement.disabled = true;
    }

    // Appel API vers ta vue Django 'api_cart_update'
    fetch('/api/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
            action: 'add'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Succès
            showNotification(data.message || 'Produit ajouté au panier !', 'success');
            
            // Mettre à jour le compteur global
            if (typeof window.updateCartCount === 'function') {
                window.updateCartCount();
            }

            if (isButton) {
                buttonElement.innerHTML = '<i class="fas fa-check"></i> Ajouté !';
                buttonElement.style.background = '#2ecc71'; // Vert succès
                
                // Retour à la normale après 2 secondes
                setTimeout(() => {
                    buttonElement.innerHTML = originalContent;
                    buttonElement.style.background = ''; 
                    buttonElement.disabled = false;
                }, 2000);
            }
            
            return true;
        } else {
            throw new Error(data.message || 'Erreur inconnue');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur lors de l\'ajout au panier.', 'error');
        
        if (isButton) {
            buttonElement.innerHTML = originalContent;
            buttonElement.disabled = false;
        }
        return false;
    });
};

/**
 * Initialise les écouteurs d'événements spécifiques à la page Panier (cart.html)
 */
function initCartPageListeners() {
    // Boutons Supprimer
    document.querySelectorAll('.btn-remove').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            if (confirm('Supprimer ce produit du panier ?')) {
                updateCartItem(productId, 'remove');
            }
        });
    });

    // Boutons + (Augmenter)
    document.querySelectorAll('.qty-increase').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            updateCartItem(productId, 'add', 1);
        });
    });

    // Boutons - (Diminuer)
    document.querySelectorAll('.qty-decrease').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            updateCartItem(productId, 'add', -1); // On ajoute -1
        });
    });
}

/**
 * Met à jour un élément du panier (Quantité ou Suppression)
 * Utilisé uniquement sur la page cart.html
 */
function updateCartItem(productId, action, changeQty = 0) {
    const csrftoken = getCookie('csrftoken');
    const row = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
    
    // Calcul de la nouvelle quantité si c'est une modification
    let newQty = 0;
    if (action === 'add') {
        if (!row) return; // Sécurité si la ligne n'existe plus
        const currentInput = row.querySelector('.qty-value');
        if (!currentInput) return;

        newQty = parseInt(currentInput.value) + changeQty;
        if (newQty < 1) {
            if(confirm("Supprimer ce produit ?")) {
                action = 'remove';
            } else {
                return;
            }
        }
    }

    fetch('/api/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            product_id: productId,
            action: action,
            quantity: newQty
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recharger la page pour voir les nouveaux totaux calculés par Django
            location.reload(); 
        } else {
            showNotification(data.error || 'Erreur de mise à jour', 'error');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion', 'error');
    });
}

/**
 * Met à jour le compteur du panier dans la navbar
 * CORRECTION ICI : Syntaxe correcte pour attacher la fonction à l'objet window
 */
window.updateCartCount = function() {
    fetch('/api/cart-count/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const countElements = document.querySelectorAll('#cartCount');
                countElements.forEach(el => {
                    el.textContent = data.count;
                    // Animation petite secousse si > 0
                    if (data.count > 0) {
                        // Vérifie que l'élément parent existe avant d'animer
                        if(el.parentElement) {
                            el.parentElement.style.transform = "scale(1.2)";
                            setTimeout(() => el.parentElement.style.transform = "scale(1)", 200);
                        }
                    }
                });
            }
        })
        .catch(err => console.log('Erreur compteur panier:', err));
};

/**
 * Affiche une notification (Toast) en haut à droite
 */
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Styles inline pour garantir l'affichage
    notification.style.cssText = `
        position: fixed;
        top: 80px; /* Juste sous la navbar */
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        z-index: 9999;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55);
        ${type === 'success' ? 'background: linear-gradient(135deg, #2ecc71, #27ae60);' : 'background: linear-gradient(135deg, #e74c3c, #c0392b);'}
    `;
    
    document.body.appendChild(notification);
    
    // Suppression automatique
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.4s ease forwards';
        setTimeout(() => notification.remove(), 400);
    }, 3000);
}

/**
 * Utilitaire : Récupère le token CSRF depuis les cookies
 */
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

// Injection des styles d'animation pour les notifications (une seule fois)
if (!document.getElementById('notif-styles')) {
    const style = document.createElement('style');
    style.id = 'notif-styles';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}