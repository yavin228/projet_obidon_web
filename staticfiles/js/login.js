(function() {
  'use strict';

  // ── DOM References ──
  const form        = document.getElementById('loginForm');
  const emailInput  = document.getElementById('email');
  const pwdInput    = document.getElementById('password');
  const toggleBtn   = document.getElementById('togglePwd');
  const toggleIcon  = document.getElementById('toggleIcon');
  const submitBtn   = document.getElementById('submitBtn');
  const rememberCb  = document.getElementById('remember');
  const alertsEl    = document.getElementById('alertsContainer');
  const fieldEmail  = document.getElementById('fieldEmail');
  const fieldPwd    = document.getElementById('fieldPassword');

  // ── Show Alert ──
  function showAlert(msg, type = 'error') {
    const icons = { error: 'fa-circle-exclamation', success: 'fa-circle-check', info: 'fa-circle-info' };
    const el = document.createElement('div');
    el.className = 'alert alert-' + type;
    el.innerHTML =
      `<i class="fas ${icons[type] || icons.info} alert-icon"></i>
       <span>${msg}</span>
       <button class="alert-close" aria-label="Fermer"><i class="fas fa-xmark"></i></button>`;

    el.querySelector('.alert-close').addEventListener('click', () => el.remove());
    alertsEl.appendChild(el);

    // Auto-dismiss after 5s
    setTimeout(() => { if (el.parentNode) el.remove(); }, 5000);
  }

  // ── Clear field error ──
  function clearError(input) {
    input.classList.remove('is-error');
  }

  // ── Set field error ──
  function setError(input) {
    input.classList.add('is-error');
    input.focus();
  }

  // ── Password Toggle ──
  toggleBtn.addEventListener('click', function() {
    if (pwdInput.type === 'password') {
      pwdInput.type = 'text';
      toggleIcon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
      pwdInput.type = 'password';
      toggleIcon.classList.replace('fa-eye-slash', 'fa-eye');
    }
  });

  // ── Real-time error clearing ──
  [emailInput, pwdInput].forEach(input => {
    input.addEventListener('input', function() {
      this.classList.remove('is-error');
    });
  });

  // ── Form Submit ──
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    let valid = true;
    const emailVal = emailInput.value.trim();
    const pwdVal   = pwdInput.value;
    const emailRe  = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Clear previous errors
    clearError(emailInput);
    clearError(pwdInput);

    if (!emailVal) {
      showAlert('Veuillez entrer votre adresse email.', 'error');
      setError(emailInput);
      valid = false;
    } else if (!emailRe.test(emailVal)) {
      showAlert('Adresse email invalide.', 'error');
      setError(emailInput);
      valid = false;
    }

    if (!pwdVal) {
      showAlert('Veuillez entrer votre mot de passe.', 'error');
      setError(pwdInput);
      valid = false;
    } else if (pwdVal.length < 6) {
      showAlert('Le mot de passe doit contenir au moins 6 caractères.', 'error');
      setError(pwdInput);
      valid = false;
    }

    if (!valid) return;

    // Loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connexion en cours…';

    // Remember Me
    if (rememberCb.checked) {
      localStorage.setItem('obidon_email', emailVal);
    } else {
      localStorage.removeItem('obidon_email');
    }

    // Simulated POST — in production this form submits via Django
    setTimeout(() => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Se connecter';
      showAlert('Connexion réussie — redirection…', 'success');
    }, 2500);
  });

  // ── Remember Me: restore on load ──
  (function() {
    const saved = localStorage.getItem('obidon_email');
    if (saved) {
      emailInput.value = saved;
      rememberCb.checked = true;
    }
  })();

  // ── Social buttons (placeholder) ──
  document.getElementById('btnGoogle').addEventListener('click', function() {
    showAlert('Connexion Google sera disponible prochainement.', 'info');
  });

  document.getElementById('btnFacebook').addEventListener('click', function() {
    showAlert('Connexion Facebook sera disponible prochainement.', 'info');
  });

  // ── Prevent resubmission on refresh ──
  if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
  }

})();