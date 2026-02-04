// reviews.js - Gestion interactive des avis et notation par étoiles

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== SYSTÈME D'ÉTOILES INTERACTIF =====
    const starRating = document.getElementById('starRating');
    
    if (starRating) {
        const stars = starRating.querySelectorAll('.star');
        const ratingInput = document.getElementById('rating-value');
        const ratingText = document.getElementById('rating-text');
        
        let selectedRating = 0;
        
        // Textes associés aux notes
        const ratingTexts = {
            0: 'Sélectionnez une note',
            1: 'Très décevant',
            2: 'Décevant',
            3: 'Moyen',
            4: 'Bien',
            5: 'Excellent !'
        };
        
        // Fonction pour mettre à jour l'affichage des étoiles
        function updateStars(rating, isPermanent = false) {
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('star-filled');
                    star.classList.remove('star-empty');
                } else {
                    star.classList.remove('star-filled');
                    star.classList.add('star-empty');
                }
            });
            
            if (isPermanent) {
                selectedRating = rating;
                ratingInput.value = rating;
                ratingText.textContent = ratingTexts[rating];
                
                // Animation du texte
                ratingText.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    ratingText.style.transform = 'scale(1)';
                }, 200);
            }
        }
        
        // Survol des étoiles
        stars.forEach((star, index) => {
            // Au survol
            star.addEventListener('mouseenter', function() {
                const value = parseInt(this.getAttribute('data-value'));
                updateStars(value, false);
                ratingText.textContent = ratingTexts[value];
            });
            
            // Au clic
            star.addEventListener('click', function() {
                const value = parseInt(this.getAttribute('data-value'));
                updateStars(value, true);
                
                // Animation de confirmation
                this.style.transform = 'scale(1.3)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 200);
            });
        });
        
        // Quand la souris quitte la zone d'étoiles
        starRating.addEventListener('mouseleave', function() {
            if (selectedRating > 0) {
                updateStars(selectedRating, false);
                ratingText.textContent = ratingTexts[selectedRating];
            } else {
                updateStars(0, false);
                ratingText.textContent = ratingTexts[0];
            }
        });
        
        // Validation du formulaire
        const reviewForm = document.getElementById('reviewForm');
        if (reviewForm) {
            reviewForm.addEventListener('submit', function(e) {
                if (selectedRating === 0) {
                    e.preventDefault();
                    alert('Veuillez sélectionner une note avant de soumettre votre avis.');
                    
                    // Animation d'alerte sur les étoiles
                    starRating.style.animation = 'shake 0.5s';
                    setTimeout(() => {
                        starRating.style.animation = '';
                    }, 500);
                    
                    return false;
                }
            });
        }
    }
    
    // ===== BOUTON WISHLIST =====
    const wishlistBtn = document.getElementById('addToWishlistBtn');
    if (wishlistBtn) {
        wishlistBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            const icon = this.querySelector('i');
            
            if (this.classList.contains('active')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.style.color = '#e74c3c';
                this.style.borderColor = '#e74c3c';
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                this.style.color = '#D4AF37';
                this.style.borderColor = '#D4AF37';
            }
        });
    }
    
    // ===== GESTION QUANTITÉ PRODUIT =====
    const increaseBtn = document.getElementById('increaseQty');
    const decreaseBtn = document.getElementById('decreaseQty');
    const quantityInput = document.getElementById('quantity');
    
    if (increaseBtn && decreaseBtn && quantityInput) {
        increaseBtn.addEventListener('click', function() {
            let qty = parseInt(quantityInput.value);
            let max = parseInt(quantityInput.max);
            if (qty < max) {
                quantityInput.value = qty + 1;
            }
        });
        
        decreaseBtn.addEventListener('click', function() {
            let qty = parseInt(quantityInput.value);
            if (qty > 1) {
                quantityInput.value = qty - 1;
            }
        });
    }
    
    // ===== GALERIE D'IMAGES =====
    window.changeMainImage = function(thumb) {
        const mainImg = document.getElementById('mainProductImage');
        if (mainImg && thumb) {
            mainImg.src = thumb.dataset.full;
            
            // Effet de transition
            mainImg.style.opacity = '0';
            setTimeout(() => {
                mainImg.style.opacity = '1';
            }, 100);
            
            // Mise à jour des miniatures actives
            document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('active'));
            thumb.classList.add('active');
        }
    };
    
    // ===== AJOUT AU PANIER =====
    const addToCartBtn = document.getElementById('addToCartBtn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            if (!this.disabled) {
                const productId = this.closest('form').querySelector('[name="product_id"]')?.value;
                const quantity = document.getElementById('quantity').value;
                
                // Animation du bouton
                this.innerHTML = '<i class="fas fa-check"></i> Ajouté !';
                this.style.backgroundColor = '#27ae60';
                
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-shopping-cart"></i> Ajouter au panier';
                    this.style.backgroundColor = '';
                }, 2000);
                
                // Ici, vous pouvez ajouter votre logique AJAX pour ajouter au panier
                console.log('Produit ajouté:', productId, 'Quantité:', quantity);
            }
        });
    }
});

// ===== ANIMATION SHAKE POUR VALIDATION =====
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);