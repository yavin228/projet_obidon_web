// Cart functionality - Add to cart with AJAX

document.addEventListener('DOMContentLoaded', function() {
    // Handle "Add to Cart" button clicks
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.getAttribute('data-product-id');
            const quantity = 1;
            
            addToCart(productId, quantity, this);
        });
    });
});

function addToCart(productId, quantity, buttonElement) {
    // Get CSRF token from cookie
    const csrftoken = getCookie('csrftoken');
    
    // Show loading state
    const originalHTML = buttonElement.innerHTML;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ajout...';
    buttonElement.disabled = true;
    
    fetch('/api/add-to-cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showNotification(data.message, 'success');
            
            // Update button
            buttonElement.innerHTML = '<i class="fas fa-check"></i> Ajouté!';
            buttonElement.style.backgroundColor = '#4CAF50';
            
            // Redirect to cart after 1 second
            setTimeout(() => {
                window.location.href = '/cart/';
            }, 1500);
        } else {
            showNotification(data.message, 'error');
            buttonElement.innerHTML = originalHTML;
            buttonElement.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Erreur lors de l\'ajout au panier', 'error');
        buttonElement.innerHTML = originalHTML;
        buttonElement.disabled = false;
    });
}

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

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 4px;
        font-weight: 500;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        ${type === 'success' ? 'background-color: #4CAF50; color: white;' : 'background-color: #f44336; color: white;'}
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
// Étoiles interactives
const stars = document.querySelectorAll('.star');
const ratingInput = document.getElementById('rating-value');
const ratingText = document.getElementById('rating-text');

if (stars.length > 0) {
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const value = star.dataset.value;
            ratingInput.value = value;
            
            stars.forEach(s => {
                if (s.dataset.value <= value) {
                    s.classList.add('star-filled');
                    s.classList.remove('star');
                } else {
                    s.classList.remove('star-filled');
                    s.classList.add('star');
                }
            });

            const texts = ['Mauvais', 'Moyen', 'Bon', 'Très bon', 'Excellent'];
            ratingText.textContent = texts[value-1] || 'Sélectionnez une note';
        });

        // Aperçu au survol
        star.addEventListener('mouseover', () => {
            const value = star.dataset.value;
            stars.forEach(s => {
                if (s.dataset.value <= value) {
                    s.classList.add('star-filled');
                }
            });
        });

        star.addEventListener('mouseout', () => {
            stars.forEach(s => {
                if (!ratingInput.value || s.dataset.value > ratingInput.value) {
                    s.classList.remove('star-filled');
                }
            });
        });
    });
}