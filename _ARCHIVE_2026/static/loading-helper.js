// Helper global pour gérer les états de chargement
window.LoadingHelper = {
    // Ajouter état de chargement à un bouton
    setButtonLoading: function(button, loading = true) {
        if (!button) return;
        
        if (loading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            // Sauvegarder le texte original
            button.dataset.originalText = button.innerHTML;
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            // Restaurer le texte original si sauvegardé
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
                delete button.dataset.originalText;
            }
        }
    },
    
    // Ajouter état de chargement à une carte
    setCardLoading: function(card, loading = true) {
        if (!card) return;
        
        if (loading) {
            card.classList.add('card-loading');
        } else {
            card.classList.remove('card-loading');
        }
    },
    
    // Ajouter état de chargement à un formulaire
    setFormLoading: function(form, loading = true) {
        if (!form) return;
        
        if (loading) {
            form.classList.add('form-loading');
            // Désactiver tous les boutons du formulaire
            form.querySelectorAll('button').forEach(btn => {
                btn.disabled = true;
            });
        } else {
            form.classList.remove('form-loading');
            // Réactiver les boutons
            form.querySelectorAll('button').forEach(btn => {
                btn.disabled = false;
            });
        }
    },
    
    // Créer un skeleton loader
    createSkeletonLoader: function(count = 3, container = null) {
        const skeletons = [];
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-loader';
            if (i === 0) skeleton.classList.add('skeleton-title');
            else if (i === count - 1) skeleton.classList.add('skeleton-short');
            skeletons.push(skeleton);
        }
        
        if (container) {
            container.innerHTML = '';
            skeletons.forEach(s => container.appendChild(s));
        }
        
        return skeletons;
    },
    
    // Afficher un loader de section
    showSectionLoader: function(container, text = 'Chargement...') {
        if (!container) return;
        
        container.innerHTML = `
            <div class="section-loading">
                <div class="section-loading-spinner"></div>
                <div class="section-loading-text">${text}</div>
            </div>
        `;
    },
    
    // Ajouter un spinner inline
    addInlineLoader: function(element) {
        if (!element) return;
        
        const loader = document.createElement('span');
        loader.className = 'loading-inline';
        element.appendChild(loader);
        
        return loader;
    },
    
    // Retirer un spinner inline
    removeInlineLoader: function(loader) {
        if (loader && loader.parentNode) {
            loader.parentNode.removeChild(loader);
        }
    },
    
    // Helper pour les requêtes avec état de chargement
    fetchWithLoading: async function(url, options = {}, button = null) {
        // Activer le chargement
        if (button) this.setButtonLoading(button, true);
        
        try {
            const response = await fetch(url, {
                ...options,
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return response;
        } finally {
            // Désactiver le chargement
            if (button) {
                // Petit délai pour éviter le flash
                setTimeout(() => {
                    this.setButtonLoading(button, false);
                }, 300);
            }
        }
    },
    
    // Helper pour les soumissions de formulaire
    submitFormWithLoading: async function(form, url, options = {}) {
        if (!form) return;
        
        // Activer le chargement
        this.setFormLoading(form, true);
        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) this.setButtonLoading(submitButton, true);
        
        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                credentials: 'include',
                ...options
            });
            
            return response;
        } finally {
            // Désactiver le chargement
            setTimeout(() => {
                this.setFormLoading(form, false);
                if (submitButton) this.setButtonLoading(submitButton, false);
            }, 300);
        }
    }
};

// Exposer globalement
window.LoadingHelper = LoadingHelper; 