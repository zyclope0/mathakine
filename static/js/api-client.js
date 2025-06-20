/**
 * Client API unifié pour Mathakine
 * Résout le problème des credentials manquants dans les appels fetch
 */
window.MathakineAPI = (function() {
    'use strict';

    /**
     * Wrapper pour fetch avec credentials et headers par défaut
     * @param {string} url - URL de l'endpoint
     * @param {object} options - Options fetch supplémentaires
     * @returns {Promise} - Promise retournée par fetch
     */
    async function apiCall(url, options = {}) {
        const defaultOptions = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        // Fusionner les options
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, finalOptions);
            
            // Gérer les erreurs HTTP communes
            if (response.status === 401) {
                console.error('Non authentifié - Redirection vers login');
                // Optionnel : rediriger vers login
                // window.location.href = '/login';
            }
            
            return response;
        } catch (error) {
            console.error('Erreur API:', error);
            throw error;
        }
    }

    /**
     * Méthodes HTTP simplifiées
     */
    return {
        // GET
        get: async (url, options = {}) => {
            return apiCall(url, {
                ...options,
                method: 'GET'
            });
        },

        // POST
        post: async (url, data = {}, options = {}) => {
            return apiCall(url, {
                ...options,
                method: 'POST',
                body: JSON.stringify(data)
            });
        },

        // PUT
        put: async (url, data = {}, options = {}) => {
            return apiCall(url, {
                ...options,
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },

        // DELETE
        delete: async (url, options = {}) => {
            return apiCall(url, {
                ...options,
                method: 'DELETE'
            });
        },

        // PATCH
        patch: async (url, data = {}, options = {}) => {
            return apiCall(url, {
                ...options,
                method: 'PATCH',
                body: JSON.stringify(data)
            });
        },

        // Méthode générique
        fetch: apiCall
    };
})();

// Alias pour compatibilité
window.apiClient = window.MathakineAPI;

// Exemples d'utilisation :
// MathakineAPI.get('/api/users/stats')
// MathakineAPI.post('/api/exercises/generate', { type: 'addition', difficulty: 'padawan' })
// MathakineAPI.delete('/api/exercises/123')