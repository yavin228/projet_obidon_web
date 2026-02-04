// ===== SYSTÈME D'ÉTOILES INTERACTIF =====
const starRating = document.getElementById('starRating');

if (starRating) {
    const stars       = starRating.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating-value');
    const ratingText  = document.getElementById('rating-text');

    let selectedRating = 0;

    const ratingTexts = {
        0: 'Sélectionnez une note',
        1: 'Très décevant',
        2: 'Décevant',
        3: 'Moyen',
        4: 'Bien',
        5: 'Excellent !'
    };

    function setStars(rating, permanent = false) {
        stars.forEach((star, idx) => {
            // idx commence à 0 → rating 1 = première étoile (idx < 1)
            if (idx < rating) {
                star.classList.add('star-filled');
                star.classList.remove('star-empty');
            } else {
                star.classList.remove('star-filled');
                star.classList.add('star-empty');
            }
        });

        if (permanent) {
            selectedRating = rating;
            ratingInput.value = rating;
            ratingText.textContent = ratingTexts[rating] || ratingTexts[0];

            ratingText.style.transform = 'scale(1.08)';
            setTimeout(() => ratingText.style.transform = 'scale(1)', 180);
        }
    }

    stars.forEach(star => {
        const value = parseInt(star.dataset.value);

        star.addEventListener('mouseenter', () => {
            setStars(value, false);
            ratingText.textContent = ratingTexts[value];
        });

        star.addEventListener('click', () => {
            setStars(value, true);

            // mini feedback
            star.style.transform = 'scale(1.35)';
            setTimeout(() => star.style.transform = '', 160);
        });
    });

    starRating.addEventListener('mouseleave', () => {
        setStars(selectedRating, false);
        ratingText.textContent = ratingTexts[selectedRating] || ratingTexts[0];
    });

    // Blocage submit si pas de note
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', e => {
            if (selectedRating === 0) {
                e.preventDefault();
                alert('Veuillez sélectionner une note avant de publier.');
                
                starRating.style.animation = 'shake 0.5s';
                setTimeout(() => starRating.style.animation = '', 600);
            }
        });
    }

    // État initial
    setStars(0, false);
}