// static/js/currency-converter.js
// Script réutilisable pour la conversion de devises

class CurrencyManager {
    constructor() {
        this.config = {
            'XOF': { symbol: 'FCFA', flag: '🇹🇬', name: 'Franc CFA' },
            'USD': { symbol: '$', flag: '🇺🇸', name: 'Dollar américain' },
            'EUR': { symbol: '€', flag: '🇪🇺', name: 'Euro' }
        };
        
        this.currentCurrency = this.getUserCurrency();
        this.exchangeRates = {};
        this.isLoading = false;
        
        this.init();
    }
    
    // Initialize
    init() {
        this.fetchExchangeRates();
        this.setupEventListeners();
        this.setupAutoRefresh();
    }
    
    // Get user's preferred currency from localStorage or default
    getUserCurrency() {
        return localStorage.getItem('preferredCurrency') || 'XOF';
    }
    
    // Set user's preferred currency
    setUserCurrency(currency) {
        localStorage.setItem('preferredCurrency', currency);
        this.currentCurrency = currency;
    }
    
    // Fetch exchange rates from API
    async fetchExchangeRates() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        
        try {
            const response = await fetch(`/api/exchange-rates/?base=${this.currentCurrency}`);
            const data = await response.json();
            
            if (data.success) {
                this.exchangeRates = data.data.rates;
                console.log('✓ Exchange rates updated', this.exchangeRates);
            } else {
                console.error('Failed to fetch exchange rates:', data.error);
                this.useFallbackRates();
            }
        } catch (error) {
            console.error('Error fetching exchange rates:', error);
            this.useFallbackRates();
        } finally {
            this.isLoading = false;
        }
    }
    
    // Use fallback rates in case of API failure
    useFallbackRates() {
        const fallbackRates = {
            'XOF': { 'XOF': 1, 'USD': 0.0016, 'EUR': 0.0015 },
            'USD': { 'XOF': 620, 'USD': 1, 'EUR': 0.92 },
            'EUR': { 'XOF': 655.96, 'USD': 1.09, 'EUR': 1 }
        };
        
        this.exchangeRates = fallbackRates[this.currentCurrency] || {};
        console.warn('Using fallback exchange rates');
    }
    
    // Convert amount from one currency to another
    convert(amount, fromCurrency, toCurrency) {
        if (fromCurrency === toCurrency) {
            return amount;
        }
        
        // If converting from base currency
        if (fromCurrency === this.currentCurrency) {
            const rate = this.exchangeRates[toCurrency] || 1;
            return amount * rate;
        }
        
        // If converting to base currency
        if (toCurrency === this.currentCurrency) {
            const rate = this.exchangeRates[fromCurrency] || 1;
            return amount / rate;
        }
        
        // Converting between two non-base currencies
        const rateFrom = this.exchangeRates[fromCurrency] || 1;
        const rateTo = this.exchangeRates[toCurrency] || 1;
        return amount * rateTo / rateFrom;
    }
    
    // Format price with currency symbol
    formatPrice(amount, currencyCode) {
        const config = this.config[currencyCode];
        if (!config) return `${amount.toFixed(2)} ${currencyCode}`;
        
        const formatted = amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        return `${config.symbol} ${formatted}`;
    }
    
    // Convert all prices on the page
    async convertAllPrices() {
        await this.fetchExchangeRates();
        
        const priceElements = document.querySelectorAll('.currency-price');
        
        priceElements.forEach(element => {
            const baseAmount = parseFloat(element.dataset.baseAmount);
            const baseCurrency = element.dataset.baseCurrency || 'EUR';
            
            if (!isNaN(baseAmount)) {
                element.classList.add('loading');
                
                const convertedAmount = this.convert(
                    baseAmount, 
                    baseCurrency, 
                    this.currentCurrency
                );
                
                element.textContent = this.formatPrice(convertedAmount, this.currentCurrency);
                element.classList.remove('loading');
            }
        });
    }
    
    // Setup event listeners
    setupEventListeners() {
        // Listen for currency change events
        document.addEventListener('currencyChanged', (e) => {
            this.currentCurrency = e.detail.currency;
            this.convertAllPrices();
        });
        
        // Setup dropdown if exists
        const dropdownBtn = document.getElementById('currencyDropdownBtn');
        const dropdownMenu = document.getElementById('currencyMenu');
        
        if (dropdownBtn && dropdownMenu) {
            dropdownBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdownMenu.classList.toggle('show');
            });
            
            document.addEventListener('click', (e) => {
                if (!dropdownMenu.contains(e.target) && !dropdownBtn.contains(e.target)) {
                    dropdownMenu.classList.remove('show');
                }
            });
        }
    }
    
    // Setup auto-refresh (every hour)
    setupAutoRefresh() {
        setInterval(() => {
            this.fetchExchangeRates();
        }, 3600000); // 1 hour
    }
    
    // Change currency
    changeCurrency(newCurrency) {
        if (!this.config[newCurrency]) {
            console.error('Invalid currency:', newCurrency);
            return;
        }
        
        this.setUserCurrency(newCurrency);
        
        // Update UI
        const currentCurrencySpan = document.querySelector('.current-currency');
        if (currentCurrencySpan) {
            const config = this.config[newCurrency];
            currentCurrencySpan.innerHTML = `${config.flag} ${newCurrency}`;
        }
        
        // Update active state
        document.querySelectorAll('.currency-option').forEach(opt => {
            opt.classList.remove('active');
            const checkIcon = opt.querySelector('.fa-check');
            if (checkIcon) checkIcon.remove();
        });
        
        const selectedOption = document.querySelector(`[data-currency="${newCurrency}"]`);
        if (selectedOption) {
            selectedOption.classList.add('active');
            selectedOption.innerHTML += '<i class="fas fa-check"></i>';
        }
        
        // Close dropdown
        const dropdownMenu = document.getElementById('currencyMenu');
        if (dropdownMenu) {
            dropdownMenu.classList.remove('show');
        }
        
        // Dispatch event
        document.dispatchEvent(new CustomEvent('currencyChanged', {
            detail: { currency: newCurrency }
        }));
        
        // Convert all prices
        this.convertAllPrices();
    }
}

// Global function for easy access
function selectCurrency(code, flag, name) {
    if (window.currencyManager) {
        window.currencyManager.changeCurrency(code);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.currencyManager = new CurrencyManager();
    window.currencyManager.convertAllPrices();
});