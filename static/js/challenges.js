/**
 * Mathakine - JavaScript pour la page Défis Galactiques
 * Gestion des interactions avec l'API des challenges
 */

// Configuration des défis avec leurs types d'exercices correspondants
const CHALLENGE_CONFIG = {
    1: { type: 'addition', exercises_endpoint: '/api/exercises/generate?type=ADDITION' },
    2: { type: 'multiplication', exercises_endpoint: '/api/exercises/generate?type=MULTIPLICATION' },
    3: { type: 'fractions', exercises_endpoint: '/api/exercises/generate?type=FRACTION' },
    4: { type: 'geometry', exercises_endpoint: '/api/exercises/generate?type=GEOMETRIE' },
    999: { type: 'weekly', exercises_endpoint: '/api/exercises/generate?type=GEOMETRIE&difficulty=CHEVALIER' }
};

/**
 * Démarre un défi spécifique
 * @param {number} challengeId - ID du défi
 * @param {string} challengeType - Type du défi (addition, multiplication, etc.)
 */
async function startChallenge(challengeId, challengeType) {
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    
    try {
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Lancement...';
        button.disabled = true;
        
        // Redirection vers les exercices appropriés
        if (challengeId === 999) {
            window.location.href = '/exercises?type=GEOMETRIE&difficulty=CHEVALIER';
        } else {
            window.location.href = `/exercises?type=${challengeType.toUpperCase()}`;
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        button.innerHTML = originalContent;
        button.disabled = false;
    }
}

/**
 * Continue le défi hebdomadaire
 */
function continueWeeklyChallenge() {
    startChallenge(999, 'weekly');
}

/**
 * Affiche les récompenses d'un défi
 * @param {number} challengeId - ID du défi
 */
function showRewards(challengeId) {
    alert(`Récompenses du défi ${challengeId}: Étoiles et badges à débloquer !`);
}

/**
 * Fonction utilitaire pour afficher des notifications
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--sw-card-bg);
        border: 1px solid var(--sw-card-border);
        border-radius: var(--border-radius);
        padding: var(--space-md);
        box-shadow: var(--shadow-elevated);
        z-index: 1001;
        animation: slideInRight 0.3s ease;
        ${type === 'error' ? 'border-left: 4px solid var(--sw-red);' : 'border-left: 4px solid var(--sw-blue);'}
    `;
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-suppression après 3 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

/**
 * Ajoute les gestionnaires d'événements aux boutons de défis
 */
function addChallengeHandlers() {
    // Défi hebdomadaire
    const weeklyButton = document.querySelector('.weekly-challenge .btn--primary');
    if (weeklyButton && !weeklyButton.onclick) {
        weeklyButton.onclick = () => continueWeeklyChallenge();
    }
    
    const rewardsButton = document.querySelector('.weekly-challenge .btn--secondary');
    if (rewardsButton && !rewardsButton.onclick) {
        rewardsButton.onclick = () => showRewards(999);
    }
    
    // Défis quotidiens - ajouter les handlers en fonction de l'ordre
    const challengeButtons = document.querySelectorAll('.challenges-grid .challenge-card .btn--primary');
    const challengeTypes = ['addition', 'multiplication', 'fractions', 'geometry'];
    
    challengeButtons.forEach((button, index) => {
        if (!button.onclick) {
            const challengeId = index + 1;
            const challengeType = challengeTypes[index] || 'general';
            button.onclick = () => startChallenge(challengeId, challengeType);
        }
    });
}

/**
 * Met à jour le timer du défi hebdomadaire
 */
function updateWeeklyTimer() {
    const timerElement = document.querySelector('.challenge-timer');
    if (timerElement) {
        const now = new Date();
        const endOfWeek = new Date(now);
        endOfWeek.setDate(now.getDate() + (7 - now.getDay())); // Prochain dimanche
        endOfWeek.setHours(23, 59, 59, 999);
        
        const timeLeft = endOfWeek - now;
        
        if (timeLeft > 0) {
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            
            timerElement.textContent = `⏰ Temps restant : ${days}j ${hours}h ${minutes}m`;
        } else {
            timerElement.textContent = `⏰ Nouveau défi disponible !`;
        }
    }
}

/**
 * Initialise les animations des cartes
 */
function initCardAnimations() {
    const challengeCards = document.querySelectorAll('.challenge-card');
    challengeCards.forEach((card, index) => {
        // Ajouter un attribut data pour faciliter les interactions
        card.setAttribute('data-challenge-id', index + 1);
        
        // Animation au survol
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px) scale(1.02)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Initialisation de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 Page Défis Galactiques initialisée - Mathakine L\'API Rebelle');
    
    // Ajouter les styles nécessaires au document
    addModalStyles();
    
    // Mise à jour du timer du défi hebdomadaire
    updateWeeklyTimer();
    setInterval(updateWeeklyTimer, 60000); // Mise à jour chaque minute
    
    // Ajouter les gestionnaires d'événements aux boutons
    addChallengeHandlers();
    
    // Initialiser les animations des cartes
    initCardAnimations();
    
    // Notification de bienvenue
    setTimeout(() => {
        showNotification('Bienvenue dans les Défis Galactiques ! Choisissez votre mission, jeune Padawan.', 'info');
    }, 1000);
});

/**
 * Ajoute les styles CSS nécessaires pour les modals et notifications
 */
function addModalStyles() {
    if (document.getElementById('challenges-modal-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'challenges-modal-styles';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .modal-content {
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--space-lg);
            padding-bottom: var(--space-md);
            border-bottom: 1px solid var(--sw-card-border);
        }
        
        .btn-close {
            background: none;
            border: none;
            color: var(--sw-text-secondary);
            cursor: pointer;
            padding: var(--space-xs);
            border-radius: 50%;
            transition: var(--default-transition);
        }
        
        .btn-close:hover {
            background: var(--sw-card-hover);
            color: var(--sw-text);
        }
        
        .reward-stars {
            font-size: 1.5rem;
            color: var(--sw-gold);
        }
    `;
    
    document.head.appendChild(style);
}

// Exposer les fonctions globalement pour les onclick handlers
window.startChallenge = startChallenge;
window.continueWeeklyChallenge = continueWeeklyChallenge;
window.showRewards = showRewards; 