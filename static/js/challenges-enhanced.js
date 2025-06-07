/**
 * Mathakine - Challenges Enhanced avec feedback utilisateur amélioré
 */

class ChallengesEnhanced {
    constructor() {
        this.challengeInfo = {
            1: {
                name: "Sommes de Tatooine",
                description: "Aide Luke à compter ses crédits",
                objective: "Résoudre 5 exercices d'addition niveau Initié",
                reward: "50 ⭐ + Badge Compteur de Tatooine",
                exerciseType: "addition",
                difficulty: "initie",
                totalExercises: 5
            },
            2: {
                name: "Calculs Hyperspatiaux", 
                description: "Calcule les vitesses des vaisseaux rebelles",
                objective: "Résoudre 8 exercices de multiplication niveau Padawan",
                reward: "120 ⭐ + Badge Pilote Hyperespace",
                exerciseType: "multiplication",
                difficulty: "padawan",
                totalExercises: 8
            },
            3: {
                name: "Partage des Rations",
                description: "Distribue équitablement les provisions sur Hoth",
                objective: "Résoudre 6 exercices de fractions niveau Chevalier",
                reward: "200 ⭐ + Badge Maître des Rations",
                exerciseType: "fractions", 
                difficulty: "chevalier",
                totalExercises: 6
            },
            4: {
                name: "Architecture de l'Étoile Noire",
                description: "Analyse les plans secrets de l'Empire",
                objective: "Résoudre 10 exercices de géométrie niveau Maître",
                reward: "500 ⭐ + Badge Architecte Impérial",
                exerciseType: "geometrie",
                difficulty: "maitre", 
                totalExercises: 10
            },
            999: {
                name: "Mission Alderaan",
                description: "Aide la Princesse Leia avec les coordonnées hyperspace",
                objective: "Résoudre 20 exercices de géométrie niveau Chevalier",
                reward: "250 ⭐ + Badge Héros d'Alderaan + Accès Maître Jedi",
                exerciseType: "geometrie",
                difficulty: "chevalier",
                totalExercises: 20,
                isWeekly: true
            }
        };
    }

    showChallengeModal(challengeId) {
        const challenge = this.challengeInfo[challengeId];
        if (!challenge) return;

        const modalHtml = `
            <div id="challenge-modal" style="
                position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                background: rgba(0,0,0,0.8); display: flex; align-items: center; 
                justify-content: center; z-index: 1000;">
                <div style="
                    background: var(--sw-space); border: 2px solid var(--sw-blue);
                    border-radius: 12px; padding: 2rem; max-width: 500px; 
                    color: var(--sw-text); text-align: center;">
                    
                    <h2 style="color: var(--sw-blue); margin-bottom: 1rem;">
                        🌟 ${challenge.name}
                    </h2>
                    
                    <p style="margin-bottom: 1rem; font-size: 1.1rem;">
                        ${challenge.description}
                    </p>
                    
                    <div style="background: rgba(74, 107, 255, 0.1); padding: 1rem; 
                                border-radius: 8px; margin: 1rem 0;">
                        <strong>🎯 Objectif:</strong><br>
                        ${challenge.objective}
                    </div>
                    
                    <div style="background: rgba(255, 215, 0, 0.1); padding: 1rem; 
                                border-radius: 8px; margin: 1rem 0;">
                        <strong>🏆 Récompense:</strong><br>
                        ${challenge.reward}
                    </div>
                    
                    <div style="margin: 1.5rem 0;">
                        <strong>➡️ Tu vas être redirigé vers:</strong><br>
                        <em>Page Exercices → ${challenge.exerciseType} niveau ${challenge.difficulty}</em>
                    </div>
                    
                    <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;">
                        <button id="start-challenge-btn" style="
                            background: var(--sw-blue); color: white; border: none;
                            padding: 0.75rem 1.5rem; border-radius: 6px; 
                            cursor: pointer; font-weight: bold;">
                            🚀 Commencer le Défi
                        </button>
                        <button id="cancel-challenge-btn" style="
                            background: var(--sw-red); color: white; border: none;
                            padding: 0.75rem 1.5rem; border-radius: 6px; 
                            cursor: pointer;">
                            ❌ Annuler
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Event listeners
        document.getElementById('start-challenge-btn').addEventListener('click', () => {
            this.closeModal();
            this.startChallengeActual(challengeId);
        });

        document.getElementById('cancel-challenge-btn').addEventListener('click', () => {
            this.closeModal();
        });

        // Fermer sur clic extérieur
        document.getElementById('challenge-modal').addEventListener('click', (e) => {
            if (e.target.id === 'challenge-modal') {
                this.closeModal();
            }
        });
    }

    closeModal() {
        const modal = document.getElementById('challenge-modal');
        if (modal) {
            modal.remove();
        }
    }

    async startChallengeActual(challengeId) {
        const challenge = this.challengeInfo[challengeId];
        if (!challenge) return;

        console.log(`🌟 Démarrage du challenge: ${challenge.name}`);
        
        // Afficher notification de redirection
        this.showNotification(
            `🚀 Challenge "${challenge.name}" démarré !`,
            `Redirection vers les exercices ${challenge.exerciseType}...`,
            'info'
        );

        // Redirection avec paramètres de challenge
        const url = `/exercises?exercise_type=${challenge.exerciseType}&difficulty=${challenge.difficulty}&challenge_id=${challengeId}&challenge_name=${encodeURIComponent(challenge.name)}`;
        
        setTimeout(() => {
            window.location.href = url;
        }, 1500);
    }

    showNotification(title, message, type = 'info') {
        const colors = {
            info: { bg: 'var(--sw-blue)', icon: '🌟' },
            success: { bg: 'var(--sw-green)', icon: '✅' },
            warning: { bg: 'var(--sw-gold)', icon: '⚠️' }
        };

        const color = colors[type] || colors.info;

        const notificationHtml = `
            <div id="challenge-notification" style="
                position: fixed; top: 20px; right: 20px; z-index: 1001;
                background: ${color.bg}; color: white; padding: 1rem;
                border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                max-width: 300px; animation: slideIn 0.3s ease;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">${color.icon}</span>
                    <strong>${title}</strong>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.9rem;">
                    ${message}
                </div>
            </div>
            <style>
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            </style>
        `;

        document.body.insertAdjacentHTML('beforeend', notificationHtml);

        // Auto-remove après 3 secondes
        setTimeout(() => {
            const notification = document.getElementById('challenge-notification');
            if (notification) {
                notification.style.animation = 'slideIn 0.3s ease reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
    }

    async showRewardsModal(challengeId) {
        const challenge = this.challengeInfo[challengeId];
        if (!challenge) return;

        const rewardsHtml = `
            <div id="rewards-modal" style="
                position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                background: rgba(0,0,0,0.8); display: flex; align-items: center; 
                justify-content: center; z-index: 1000;">
                <div style="
                    background: linear-gradient(135deg, var(--sw-space), rgba(255,215,0,0.1));
                    border: 2px solid var(--sw-gold); border-radius: 12px; 
                    padding: 2rem; max-width: 400px; color: var(--sw-text); 
                    text-align: center; box-shadow: 0 8px 32px rgba(255,215,0,0.3);">
                    
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🏆</div>
                    
                    <h2 style="color: var(--sw-gold); margin-bottom: 1rem;">
                        Récompenses du Défi
                    </h2>
                    
                    <h3 style="color: var(--sw-blue); margin-bottom: 1rem;">
                        ${challenge.name}
                    </h3>
                    
                    <div style="text-align: left; margin: 1.5rem 0;">
                        <div style="margin: 0.5rem 0;">
                            ✨ <strong>Étoiles:</strong> ${challenge.reward.match(/\d+/)[0]} ⭐
                        </div>
                        <div style="margin: 0.5rem 0;">
                            🎖️ <strong>Badge:</strong> ${challenge.reward.split('+')[1]?.trim() || 'Badge spécial'}
                        </div>
                        <div style="margin: 0.5rem 0;">
                            ⚡ <strong>XP:</strong> ${Math.floor(parseInt(challenge.reward.match(/\d+/)[0]) / 2)}
                        </div>
                        ${challenge.isWeekly ? '<div style="margin: 0.5rem 0;">🌟 <strong>Bonus:</strong> Accès niveau Maître Jedi</div>' : ''}
                    </div>
                    
                    <div style="background: rgba(74, 107, 255, 0.1); padding: 1rem; 
                                border-radius: 8px; margin: 1rem 0; font-size: 0.9rem;">
                        <strong>📈 Progression nécessaire:</strong><br>
                        ${challenge.totalExercises} exercices à résoudre
                    </div>
                    
                    <button onclick="document.getElementById('rewards-modal').remove()" style="
                        background: var(--sw-blue); color: white; border: none;
                        padding: 0.75rem 2rem; border-radius: 6px; 
                        cursor: pointer; margin-top: 1rem;">
                        ✨ Compris !
                    </button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', rewardsHtml);
    }
}

// Instance globale
const challengesEnhanced = new ChallengesEnhanced();

// Fonctions globales améliorées
function startChallenge(challengeId, challengeType) {
    challengesEnhanced.showChallengeModal(challengeId);
}

function continueWeeklyChallenge() {
    challengesEnhanced.showChallengeModal(999);
}

function showRewards(challengeId) {
    challengesEnhanced.showRewardsModal(challengeId);
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 Challenges Enhanced initialisés - Interface explicative activée');
    
    // Ajouter handlers pour les boutons sans onclick
    const challengeButtons = document.querySelectorAll('.challenges-grid .btn--primary:not([onclick])');
    const challengeIds = [2, 3, 4]; // multiplication, fractions, geometry
    
    challengeButtons.forEach((btn, index) => {
        if (challengeIds[index]) {
            btn.onclick = () => startChallenge(challengeIds[index]);
        }
    });
});

// Exposer pour debugging
window.challengesEnhanced = challengesEnhanced; 