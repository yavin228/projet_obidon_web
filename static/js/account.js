// Account Page Navigation
document.addEventListener('DOMContentLoaded', function() {
    const menuItems = document.querySelectorAll('.menu-item');
    const contentSections = document.querySelectorAll('.content-section');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (this.classList.contains('logout')) {
                return; // Allow logout link to work normally
            }
            e.preventDefault();
            
            const sectionId = this.getAttribute('data-section');
            
            // Remove active class from all menu items and sections
            menuItems.forEach(m => m.classList.remove('active'));
            contentSections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked menu item and corresponding section
            this.classList.add('active');
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.add('active');
            }
        });
    });
    
    // Edit Profile Button
    const editProfileBtn = document.querySelector('.btn-edit-profile');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Scroll to settings section
            document.querySelector('[data-section="settings"]').click();
        });
    }
    
    // Add Address Button
    const addAddressCard = document.querySelector('.address-card.add-address');
    if (addAddressCard) {
        addAddressCard.addEventListener('click', function() {
            alert('Formulaire Ajouter une adresse - À implémenter');
        });
    }
    
    // Form Submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Modifications enregistrées (fonctionnalité à implémenter)');
        });
    });
    
    // Modify/Delete Address Links
    const addressLinks = document.querySelectorAll('.address-actions .btn-link');
    addressLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            if (this.classList.contains('danger')) {
                if (confirm('Êtes-vous sûr de vouloir supprimer cette adresse?')) {
                    alert('Adresse supprimée (fonctionnalité à implémenter)');
                }
            } else {
                alert('Formulaire Modifier l\'adresse - À implémenter');
            }
        });
    });
    
    // Delete Account Button
    const deleteAccountBtn = document.querySelector('.settings-group.danger-zone .btn-danger');
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Êtes-vous absolument sûr? Cette action est irréversible!')) {
                if (confirm('Confirmer la suppression du compte? Tous vos données seront perdues.')) {
                    alert('Compte en cours de suppression (fonctionnalité à implémenter)');
                }
            }
        });
    }
    
    // Checkbox Handlers
    const checkboxes = document.querySelectorAll('.checkbox-custom input');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            console.log(`${this.id}: ${this.checked}`);
        });
    });
});

// Smooth Transitions
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .content-section.active {
        animation: slideIn 0.3s ease;
    }
`;
document.head.appendChild(style);
