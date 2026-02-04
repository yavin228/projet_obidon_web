// ACCOUNT PAGE JAVASCRIPT - OBIDON

document.addEventListener('DOMContentLoaded', function() {
    
    // Menu Navigation
    const menuItems = document.querySelectorAll('.menu-item:not(.logout)');
    const contentSections = document.querySelectorAll('.content-section');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all menu items and sections
            menuItems.forEach(mi => mi.classList.remove('active'));
            contentSections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Show corresponding section
            const sectionId = this.getAttribute('data-section');
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
                
                // Scroll to top of content
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Logout confirmation
    const logoutForm = document.querySelector('.menu-item.logout').closest('form');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            const confirmed = confirm('Êtes-vous sûr de vouloir vous déconnecter ?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }
    
    // Stats animation on load
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(stat => {
        const finalValue = parseInt(stat.textContent) || 0;
        animateValue(stat, 0, finalValue, 1000);
    });
    
    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }
    
    // Form validation for settings
    const settingsForm = document.querySelector('.settings-group form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const firstName = document.getElementById('first_name').value.trim();
            const lastName = document.getElementById('last_name').value.trim();
            
            if (!firstName || !lastName) {
                showNotification('Veuillez remplir tous les champs obligatoires', 'error');
                return false;
            }
            
            // Simulate form submission
            const submitBtn = this.querySelector('.btn-primary');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                submitBtn.innerHTML = '<i class="fas fa-check"></i> Enregistré !';
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
                showNotification('Vos informations ont été mises à jour avec succès', 'success');
            }, 1500);
        });
    }
    
    // Notification checkboxes
    const notificationCheckboxes = document.querySelectorAll('.notification-option input[type="checkbox"]');
    notificationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const label = this.nextElementSibling.textContent;
            const status = this.checked ? 'activées' : 'désactivées';
            showNotification(`Notifications ${label.toLowerCase()} ${status}`, 'info');
        });
    });
    
    // Show notification function
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
        document.body.appendChild(notification);
        
        // Add styles if not already present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    min-width: 300px;
                    max-width: 500px;
                    z-index: 10000;
                    animation: slideInRight 0.3s ease;
                }
                
                .notification-success {
                    border-left: 4px solid #43A047;
                    color: #43A047;
                }
                
                .notification-error {
                    border-left: 4px solid #E53935;
                    color: #E53935;
                }
                
                .notification-info {
                    border-left: 4px solid #2196F3;
                    color: #2196F3;
                }
                
                .notification i:first-child {
                    font-size: 1.3rem;
                }
                
                .notification span {
                    flex: 1;
                    color: #333;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: #999;
                    cursor: pointer;
                    font-size: 1.1rem;
                    padding: 0;
                    transition: color 0.3s;
                }
                
                .notification-close:hover {
                    color: #333;
                }
                
                @keyframes slideInRight {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes slideOutRight {
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
        }
        
        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
    
    // Add address card click handler
    const addAddressCard = document.querySelector('.address-card.add-address');
    if (addAddressCard) {
        addAddressCard.addEventListener('click', function() {
            showNotification('Fonctionnalité d\'ajout d\'adresse bientôt disponible', 'info');
        });
    }
    
    // Empty state buttons
    const emptyStateBtns = document.querySelectorAll('.empty-state .btn-primary');
    emptyStateBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Add a subtle animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
    
    // Stat cards hover effect enhancement
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Info boxes animation
    const infoBoxes = document.querySelectorAll('.info-box');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    infoBoxes.forEach((box, index) => {
        box.style.opacity = '0';
        box.style.animationDelay = `${index * 0.1}s`;
        observer.observe(box);
    });
    
    // Add fadeInUp animation
    if (!document.getElementById('account-animations')) {
        const style = document.createElement('style');
        style.id = 'account-animations';
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
            
            .stat-card {
                transition: all 0.3s ease;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Preserve active section on page reload
    const currentHash = window.location.hash;
    if (currentHash) {
        const sectionName = currentHash.replace('#', '');
        const targetMenuItem = document.querySelector(`[data-section="${sectionName}"]`);
        if (targetMenuItem) {
            targetMenuItem.click();
        }
    }
    
    // Update URL hash when section changes
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            window.location.hash = sectionId;
        });
    });
    
    console.log('🍞☕ Page de compte Obidon chargée avec succès!');
});

// Global function for delete account confirmation
function confirmDeleteAccount() {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 15px;
            padding: 2.5rem;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: scaleIn 0.3s ease;
        ">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <i class="fas fa-exclamation-triangle" style="font-size: 4rem; color: #E53935;"></i>
            </div>
            <h3 style="color: #E53935; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">
                Supprimer votre compte ?
            </h3>
            <p style="color: #666; text-align: center; margin-bottom: 1.5rem; line-height: 1.6;">
                Cette action est <strong>IRRÉVERSIBLE</strong> et supprimera définitivement :
            </p>
            <ul style="color: #666; margin-bottom: 2rem; padding-left: 2rem;">
                <li>Toutes vos commandes</li>
                <li>Vos adresses de livraison</li>
                <li>Vos produits favoris</li>
                <li>Toutes vos données personnelles</li>
            </ul>
            <div style="display: flex; gap: 1rem;">
                <button onclick="this.closest('div[style*=fixed]').remove()" style="
                    flex: 1;
                    padding: 12px 24px;
                    border: 2px solid #ddd;
                    background: white;
                    color: #666;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s;
                ">
                    Annuler
                </button>
                <button onclick="deleteAccountConfirmed()" style="
                    flex: 1;
                    padding: 12px 24px;
                    border: none;
                    background: #E53935;
                    color: white;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s;
                ">
                    Supprimer définitivement
                </button>
            </div>
        </div>
    `;
    
    // Add animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes scaleIn {
            from { transform: scale(0.9); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(modal);
}

function deleteAccountConfirmed() {
    alert('Suppression du compte... (À implémenter côté serveur)');
    document.querySelector('div[style*="fixed"]').remove();
    // Ici vous ajouterez l'appel AJAX pour supprimer le compte
}