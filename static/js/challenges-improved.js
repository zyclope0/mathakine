/**
 * Mathakine - Challenges avec Interface Explicative
 * Version améliorée qui explique à l'utilisateur ce qui va se passer
 */

class ChallengeExplainer {
    constructor() {
        this.challenges = {
            1: {
                name: "Sommes de Tatooine",
                story: "Aide Luke Skywalker à compter ses crédits avant de quitter Tatooine",
                target: "5 exercices d'addition niveau Initié",
                reward: "50 ⭐ + Badge Compteur de Tatooine",
                redirect: "/exercises?exercise_type=addition&difficulty=initie",
                icon: "🌅"
            },
            2: {
                name: "Calculs Hyperspatiaux", 
                story: "Calcule les vitesses des vaisseaux rebelles pour l'hyperespace",
                target: "8 exercices de multiplication niveau Padawan",
                reward: "120 ⭐ + Badge Pilote Hyperespace",
                redirect: "/exercises?exercise_type=multiplication&difficulty=padawan",
                icon: "⚡"
            },
            3: {
                name: "Partage des Rations",
                story: "Distribue les provisions aux soldats rebelles sur Hoth",
                target: "6 exercices de fractions niveau Chevalier", 
                reward: "200 ⭐ + Badge Maître des Rations",
                redirect: "/exercises?exercise_type=fractions&difficulty=chevalier",
                icon: "🍞"
            },
            4: {
                name: "Architecture de l'Étoile Noire",
                story: "Analyse les plans secrets pour trouver les points faibles",
                target: "10 exercices de géométrie niveau Maître",
                reward: "500 ⭐ + Badge Architecte Impérial",
                redirect: "/exercises?exercise_type=geometrie&difficulty=maitre",
                icon: "🔧"
            },
            999: {
                name: "Mission Alderaan",
                story: "Aide la Princesse Leia avec les coordonnées hyperspace critiques",
                target: "20 exercices de géométrie niveau Chevalier",
                reward: "250 ⭐ + Badge Héros d'Alderaan + Accès Maître Jedi",
                redirect: "/exercises?exercise_type=geometrie&difficulty=chevalier",
                icon: "🏆",
                isWeekly: true
            }
        };
    }

    showExplanationModal(challengeId) {
        const challenge = this.challenges[challengeId];
        if (!challenge) {
            console.error('Challenge introuvable:', challengeId);
            return;
        }

        // Créer la modal explicative
        const modal = document.createElement('div');
        modal.id = 'challenge-explanation-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85); display: flex; 
            align-items: center; justify-content: center; z-index: 2000;
            backdrop-filter: blur(5px);
        `;

        modal.innerHTML = `
            <div style="
                background: linear-gradient(135deg, #1a1f3a 0%, #2a2f4a 100%);
                border: 2px solid #4a6bff; border-radius: 16px; padding: 2rem;
                max-width: 500px; margin: 1rem; color: #e2e8f0;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
                position: relative; overflow: hidden;
            ">
                <!-- Effet d'étoiles en arrière-plan -->
                <div style="
                    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
                    background-image: radial-gradient(2px 2px at 20px 30px, #fff, transparent),
                                     radial-gradient(2px 2px at 40px 70px, #fff, transparent),
                                     radial-gradient(1px 1px at 90px 40px, #fff, transparent);
                    opacity: 0.1; pointer-events: none;
                "></div>
                
                <div style="position: relative; z-index: 1;">
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <div style="font-size: 3rem; margin-bottom: 0.5rem;">${challenge.icon}</div>
                        <h2 style="color: #4a6bff; margin: 0; font-size: 1.8rem; font-weight: bold;">
                            ${challenge.name}
                        </h2>
                        <p style="color: #94a3b8; margin: 0.5rem 0; font-style: italic;">
                            ${challenge.story}
                        </p>
                    </div>

                    <div style="
                        background: rgba(74, 107, 255, 0.1); border: 1px solid rgba(74, 107, 255, 0.3);
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;
                    ">
                        <h3 style="color: #ffd700; margin: 0 0 0.5rem 0; font-size: 1.1rem;">
                            🎯 Votre Mission
                        </h3>
                        <p style="margin: 0; line-height: 1.4;">
                            ${challenge.target}
                        </p>
                    </div>

                    <div style="
                        background: rgba(255, 215, 0, 0.1); border: 1px solid rgba(255, 215, 0, 0.3);
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;
                    ">
                        <h3 style="color: #ffd700; margin: 0 0 0.5rem 0; font-size: 1.1rem;">
                            🏆 Récompenses
                        </h3>
                        <p style="margin: 0; line-height: 1.4;">
                            ${challenge.reward}
                        </p>
                    </div>

                    <div style="
                        background: rgba(138, 43, 226, 0.1); border: 1px solid rgba(138, 43, 226, 0.3);
                        border-radius: 8px; padding: 1rem; margin: 1.5rem 0;
                        text-align: center;
                    ">
                        <h3 style="color: #a855f7; margin: 0 0 0.5rem 0; font-size: 1rem;">
                            🚀 Que va-t-il se passer ?
                        </h3>
                        <p style="margin: 0; font-size: 0.9rem; line-height: 1.4;">
                            Vous allez être redirigé vers la <strong>page Exercices</strong><br>
                            avec <strong>seulement</strong> les exercices de ce défi !<br>
                            <em>Votre progression sera automatiquement suivie.</em>
                        </p>
                    </div>

                    <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                        <button id="start-mission-btn" style="
                            background: linear-gradient(135deg, #4a6bff, #8b5cf6);
                            color: white; border: none; padding: 0.875rem 1.5rem;
                            border-radius: 8px; cursor: pointer; font-weight: bold;
                            flex: 1; transition: all 0.3s ease; font-size: 1rem;
                        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 25px rgba(74,107,255,0.4)'"
                           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                            ✨ Commencer la Mission !
                        </button>
                        <button id="cancel-mission-btn" style="
                            background: transparent; color: #94a3b8; 
                            border: 1px solid #475569; padding: 0.875rem 1rem;
                            border-radius: 8px; cursor: pointer; transition: all 0.3s ease;
                        " onmouseover="this.style.borderColor='#64748b'; this.style.color='#e2e8f0'"
                           onmouseout="this.style.borderColor='#475569'; this.style.color='#94a3b8'">
                            ❌ Annuler
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Événements
        document.getElementById('start-mission-btn').onclick = () => {
            this.startMission(challengeId);
        };

        document.getElementById('cancel-mission-btn').onclick = () => {
            this.closeModal();
        };

        // Fermer en cliquant à l'extérieur
        modal.onclick = (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        };

        // Animation d'entrée
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.opacity = '1';
            modal.style.transition = 'opacity 0.3s ease';
        }, 10);
    }

    async startMission(challengeId) {
        const challenge = this.challenges[challengeId];
        const button = document.getElementById('start-mission-btn');
        const originalText = button.textContent;

        try {
            // Animation du bouton
            button.innerHTML = '<i class="fas fa-rocket" style="animation: spin 1s linear infinite;"></i> Lancement...';
            button.disabled = true;

            // Notification de transition
            this.showTransitionNotification(challenge);

            // Simuler un délai pour que l'utilisateur voie la transition
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Tentative API puis fallback
            try {
                const response = await fetch(`/api/challenges/start/${challengeId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                        return;
                    }
                }
            } catch (apiError) {
                console.log('API indisponible, redirection directe');
            }

            // Fallback : redirection directe
            window.location.href = challenge.redirect;

        } catch (error) {
            console.error('Erreur:', error);
            button.textContent = originalText;
            button.disabled = false;
            alert('❌ Erreur lors du lancement du défi. Veuillez réessayer.');
        }
    }

    showTransitionNotification(challenge) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #4a6bff, #8b5cf6);
            color: white; padding: 1.5rem 2rem; border-radius: 12px;
            z-index: 3000; text-align: center; min-width: 300px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            border: 2px solid rgba(255, 255, 255, 0.2);
        `;

        notification.innerHTML = `
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚀</div>
            <div style="font-weight: bold; margin-bottom: 0.5rem;">Mission ${challenge.name}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Redirection vers les exercices...</div>
            <div style="margin-top: 1rem;">
                <div style="width: 200px; height: 4px; background: rgba(255,255,255,0.3); border-radius: 2px; margin: 0 auto;">
                    <div style="width: 0%; height: 100%; background: #ffd700; border-radius: 2px; animation: progressBar 1.8s ease-out forwards;"></div>
                </div>
            </div>
            <style>
                @keyframes progressBar {
                    to { width: 100%; }
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
        `;

        document.body.appendChild(notification);

        // Auto-suppression
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 2500);
    }

    closeModal() {
        const modal = document.getElementById('challenge-explanation-modal');
        if (modal) {
            modal.style.opacity = '0';
            setTimeout(() => modal.remove(), 300);
        }
    }

    showRewardsDetail(challengeId) {
        const challenge = this.challenges[challengeId];
        if (!challenge) return;

        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.8); display: flex; 
            align-items: center; justify-content: center; z-index: 2000;
        `;

        modal.innerHTML = `
            <div style="
                background: linear-gradient(135deg, #1a1f3a, #2a2f4a);
                border: 2px solid #ffd700; border-radius: 16px; 
                padding: 2rem; max-width: 400px; color: white; text-align: center;
                box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🏆</div>
                <h2 style="color: #ffd700; margin-bottom: 1rem;">Récompenses</h2>
                <h3 style="color: #4a6bff; margin-bottom: 1.5rem;">${challenge.name}</h3>
                
                <div style="text-align: left; background: rgba(255,215,0,0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    ${challenge.reward.split('+').map(reward => 
                        `<div style="margin: 0.5rem 0;">✨ ${reward.trim()}</div>`
                    ).join('')}
                </div>
                
                <button onclick="this.closest('[style*=\"position: fixed\"]').remove()" style="
                    background: #ffd700; color: #1a1f3a; border: none;
                    padding: 0.75rem 2rem; border-radius: 8px; 
                    cursor: pointer; font-weight: bold; margin-top: 1rem;">
                    ✨ Compris !
                </button>
            </div>
        `;

        document.body.appendChild(modal);
    }
}

// Instance globale
const challengeExplainer = new ChallengeExplainer();

// Fonctions globales améliorées
function startChallenge(challengeId, challengeType) {
    challengeExplainer.showExplanationModal(challengeId);
}

function continueWeeklyChallenge() {
    challengeExplainer.showExplanationModal(999);
}

function showRewards(challengeId) {
    challengeExplainer.showRewardsDetail(challengeId);
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 Challenge Explainer initialisé - Interface explicative active');
    
    // Remplacer les handlers existants
    const buttons = document.querySelectorAll('.challenges-grid .btn--primary:not([onclick])');
    const challengeIds = [2, 3, 4]; // multiplication, fractions, geometry
    
    buttons.forEach((btn, index) => {
        if (challengeIds[index]) {
            btn.onclick = () => startChallenge(challengeIds[index]);
        }
    });

    // Message d'aide initial
    setTimeout(() => {
        const helpBanner = document.createElement('div');
        helpBanner.style.cssText = `
            position: fixed; bottom: 20px; right: 20px; z-index: 1000;
            background: linear-gradient(135deg, #4a6bff, #8b5cf6);
            color: white; padding: 1rem; border-radius: 8px; max-width: 280px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3); font-size: 0.9rem;
        `;
        helpBanner.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 0.5rem;">💡 Nouveauté !</div>
            <div>Cliquez sur un défi pour voir une explication détaillée avant de commencer !</div>
            <button onclick="this.parentElement.remove()" style="
                background: rgba(255,255,255,0.2); border: none; color: white;
                padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer;
                margin-top: 0.5rem; float: right; font-size: 0.8rem;">
                ✕
            </button>
        `;
        document.body.appendChild(helpBanner);

        // Auto-suppression après 8 secondes
        setTimeout(() => {
            if (helpBanner.parentElement) {
                helpBanner.remove();
            }
        }, 8000);
    }, 2000);
});

// Export pour debug
window.challengeExplainer = challengeExplainer; 