/**
 * Mathakine - Challenges Hybrides (Exercices + Logic Challenges)
 * Version qui gère les deux types de défis
 */

class HybridChallengeSystem {
    constructor() {
        // Challenges d'exercices classiques (existants)
        this.exerciseChallenges = {
            1: {
                name: "Sommes de Tatooine",
                type: "EXERCISE",
                story: "Aide Luke Skywalker à compter ses crédits",
                target: "5 exercices d'addition niveau Initié",
                reward: "50 ⭐ + Badge Compteur de Tatooine",
                redirect: "/exercises?exercise_type=addition&difficulty=initie",
                icon: "🌅"
            },
            2: {
                name: "Calculs Hyperspatiaux", 
                type: "EXERCISE",
                story: "Calcule les vitesses des vaisseaux rebelles",
                target: "8 exercices de multiplication niveau Padawan",
                reward: "120 ⭐ + Badge Pilote Hyperespace",
                redirect: "/exercises?exercise_type=multiplication&difficulty=padawan",
                icon: "⚡"
            },
            3: {
                name: "Partage des Rations",
                type: "EXERCISE",
                story: "Distribue les provisions aux soldats rebelles",
                target: "6 exercices de fractions niveau Chevalier", 
                reward: "200 ⭐ + Badge Maître des Rations",
                redirect: "/exercises?exercise_type=fractions&difficulty=chevalier",
                icon: "🍞"
            },
            4: {
                name: "Architecture de l'Étoile Noire",
                type: "EXERCISE",
                story: "Analyse les plans secrets pour trouver les points faibles",
                target: "10 exercices de géométrie niveau Maître",
                reward: "500 ⭐ + Badge Architecte Impérial",
                redirect: "/exercises?exercise_type=geometrie&difficulty=maitre",
                icon: "🔧"
            }
        };

        // Logic Challenges (nouveaux)
        this.logicChallenges = {
            100: {
                name: "🚀 Code de Navigation Spatiale",
                type: "LOGIC_SEQUENCE",
                story: "L'ordinateur de bord d'un vaisseau spatial affiche une séquence de navigation. Déchiffrez le code !",
                target: "Résoudre la séquence géométrique",
                reward: "150 ⭐ + Badge Navigation",
                logic_id: 2292, // ID dans logic_challenges
                icon: "🚀"
            },
            101: {
                name: "🌌 Formation de Constellation",
                type: "LOGIC_PATTERN", 
                story: "Les étoiles d'une constellation forment un pattern géométrique. Identifiez la règle !",
                target: "Reconnaître le pattern stellaire",
                reward: "175 ⭐ + Badge Constellation",
                logic_id: 2293,
                icon: "🌌"
            },
            102: {
                name: "🔧 Réparation Station Spatiale",
                type: "LOGIC_PUZZLE",
                story: "Un système de la station spatiale est défaillant. Utilisez la logique pour réparer !",
                target: "Résoudre le puzzle de dépendances",
                reward: "200 ⭐ + Badge Ingénieur",
                logic_id: 2294,
                icon: "🔧"
            },
            103: {
                name: "🔺 Géométrie des Astéroïdes",
                type: "LOGIC_PATTERN",
                story: "Un champ d'astéroïdes présente des formes géométriques. Identifiez le pattern !",
                target: "Analyser les formes géométriques",
                reward: "175 ⭐ + Badge Géomètre",
                logic_id: 2295,
                icon: "🔺"
            },
            104: {
                name: "🕵️ Mystère du Cargo Spatial",
                type: "LOGIC_DEDUCTION",
                story: "Un cargo spatial a disparu. Analysez les indices pour déterminer sa destination !",
                target: "Résoudre l'enquête par déduction",
                reward: "225 ⭐ + Badge Enquêteur",
                logic_id: 2296,
                icon: "🕵️"
            }
        };

        // Challenge hebdomadaire (mix)
        this.weeklyChallenge = {
            999: {
                name: "Mission Alderaan",
                type: "HYBRID",
                story: "Mission complète : exercices + énigmes logiques pour sauver Alderaan !",
                target: "15 exercices géométrie + 3 énigmes logiques",
                reward: "500 ⭐ + Badge Héros d'Alderaan + Accès Maître Jedi",
                parts: [
                    { type: "exercises", count: 15, exercise_type: "geometrie", difficulty: "chevalier" },
                    { type: "logic", count: 3, challenge_types: ["SEQUENCE", "PUZZLE", "PATTERN"] }
                ],
                icon: "🏆",
                isWeekly: true
            }
        };
    }

    showChallengeModal(challengeId) {
        let challenge = null;
        let challengeType = null;

        // Chercher dans les différents types
        if (this.exerciseChallenges[challengeId]) {
            challenge = this.exerciseChallenges[challengeId];
            challengeType = "EXERCISE";
        } else if (this.logicChallenges[challengeId]) {
            challenge = this.logicChallenges[challengeId];
            challengeType = "LOGIC";
        } else if (this.weeklyChallenge[challengeId]) {
            challenge = this.weeklyChallenge[challengeId];
            challengeType = "HYBRID";
        } else {
            console.error('Challenge introuvable:', challengeId);
            return;
        }

        this.createModal(challenge, challengeType, challengeId);
    }

    createModal(challenge, challengeType, challengeId) {
        // Créer la modal avec design adapté au type
        const modal = document.createElement('div');
        modal.id = 'hybrid-challenge-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85); display: flex; 
            align-items: center; justify-content: center; z-index: 2000;
            backdrop-filter: blur(5px);
        `;

        const typeColor = this.getTypeColor(challengeType);
        const typeIcon = this.getTypeIcon(challengeType);

        modal.innerHTML = `
            <div style="
                background: linear-gradient(135deg, #1a1f3a 0%, #2a2f4a 100%);
                border: 2px solid ${typeColor}; border-radius: 16px; padding: 2rem;
                max-width: 500px; margin: 1rem; color: #e2e8f0;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
                position: relative; overflow: hidden;
            ">
                <!-- Effet d'étoiles -->
                <div style="
                    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
                    background-image: radial-gradient(2px 2px at 20px 30px, #fff, transparent),
                                     radial-gradient(2px 2px at 40px 70px, #fff, transparent);
                    opacity: 0.1; pointer-events: none;
                "></div>
                
                <div style="position: relative; z-index: 1;">
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <div style="font-size: 3rem; margin-bottom: 0.5rem;">${challenge.icon}</div>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="color: ${typeColor}; font-size: 1.2rem;">${typeIcon}</span>
                            <h2 style="color: ${typeColor}; margin: 0; font-size: 1.8rem; font-weight: bold;">
                                ${challenge.name}
                            </h2>
                        </div>
                        <p style="color: #94a3b8; margin: 0; font-style: italic; line-height: 1.4;">
                            ${challenge.story}
                        </p>
                    </div>

                    ${this.getTypeSpecificContent(challenge, challengeType)}

                    <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                        <button id="start-challenge-btn" style="
                            background: linear-gradient(135deg, ${typeColor}, #8b5cf6);
                            color: white; border: none; padding: 0.875rem 1.5rem;
                            border-radius: 8px; cursor: pointer; font-weight: bold;
                            flex: 1; transition: all 0.3s ease; font-size: 1rem;
                        ">
                            ✨ ${this.getActionText(challengeType)}
                        </button>
                        <button id="cancel-challenge-btn" style="
                            background: transparent; color: #94a3b8; 
                            border: 1px solid #475569; padding: 0.875rem 1rem;
                            border-radius: 8px; cursor: pointer; transition: all 0.3s ease;
                        ">
                            ❌ Annuler
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Événements
        document.getElementById('start-challenge-btn').onclick = () => {
            this.startChallenge(challengeId, challengeType, challenge);
        };

        document.getElementById('cancel-challenge-btn').onclick = () => {
            this.closeModal();
        };

        modal.onclick = (e) => {
            if (e.target === modal) this.closeModal();
        };
    }

    getTypeColor(type) {
        const colors = {
            'EXERCISE': '#4a6bff',
            'LOGIC': '#f59e0b', 
            'HYBRID': '#10b981'
        };
        return colors[type] || '#4a6bff';
    }

    getTypeIcon(type) {
        const icons = {
            'EXERCISE': '📚',
            'LOGIC': '🧠',
            'HYBRID': '⚔️'
        };
        return icons[type] || '📚';
    }

    getActionText(type) {
        const actions = {
            'EXERCISE': 'Commencer les Exercices',
            'LOGIC': 'Résoudre l\'Énigme',
            'HYBRID': 'Lancer la Mission'
        };
        return actions[type] || 'Commencer';
    }

    getTypeSpecificContent(challenge, type) {
        const typeColor = this.getTypeColor(type);
        
        if (type === 'EXERCISE') {
            return `
                <div style="background: rgba(74, 107, 255, 0.1); border: 1px solid rgba(74, 107, 255, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #ffd700; margin: 0 0 0.5rem 0;">📚 Mission d'Exercices</h3>
                    <p style="margin: 0;">${challenge.target}</p>
                </div>
                <div style="background: rgba(255, 215, 0, 0.1); border: 1px solid rgba(255, 215, 0, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #ffd700; margin: 0 0 0.5rem 0;">🏆 Récompenses</h3>
                    <p style="margin: 0;">${challenge.reward}</p>
                </div>
                <div style="background: rgba(138, 43, 226, 0.1); border: 1px solid rgba(138, 43, 226, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0; text-align: center;">
                    <h3 style="color: #a855f7; margin: 0 0 0.5rem 0;">🚀 Redirection</h3>
                    <p style="margin: 0; font-size: 0.9rem;">Tu seras redirigé vers la page exercices avec les bons filtres !</p>
                </div>
            `;
        } else if (type === 'LOGIC') {
            return `
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #f59e0b; margin: 0 0 0.5rem 0;">🧠 Défi Logique</h3>
                    <p style="margin: 0;">${challenge.target}</p>
                </div>
                <div style="background: rgba(255, 215, 0, 0.1); border: 1px solid rgba(255, 215, 0, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #ffd700; margin: 0 0 0.5rem 0;">🏆 Récompenses</h3>
                    <p style="margin: 0;">${challenge.reward}</p>
                </div>
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0; text-align: center;">
                    <h3 style="color: #f59e0b; margin: 0 0 0.5rem 0;">🧩 Énigme Interactive</h3>
                    <p style="margin: 0; font-size: 0.9rem;">Tu seras dirigé vers une interface d'énigme logique spécialisée !</p>
                </div>
            `;
        } else if (type === 'HYBRID') {
            return `
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #10b981; margin: 0 0 0.5rem 0;">⚔️ Mission Hybride</h3>
                    <p style="margin: 0;">${challenge.target}</p>
                </div>
                <div style="background: rgba(255, 215, 0, 0.1); border: 1px solid rgba(255, 215, 0, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #ffd700; margin: 0 0 0.5rem 0;">🏆 Récompenses Exceptionnelles</h3>
                    <p style="margin: 0;">${challenge.reward}</p>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);
                           border-radius: 8px; padding: 1rem; margin: 1rem 0; text-align: center;">
                    <h3 style="color: #10b981; margin: 0 0 0.5rem 0;">🌟 Mission Complète</h3>
                    <p style="margin: 0; font-size: 0.9rem;">Exercices + Énigmes logiques + Récompenses spéciales !</p>
                </div>
            `;
        }
    }

    async startChallenge(challengeId, challengeType, challenge) {
        this.closeModal();
        
        if (challengeType === 'EXERCISE') {
            // Redirection vers exercices (existant)
            window.location.href = challenge.redirect;
            
        } else if (challengeType === 'LOGIC') {
            // Redirection vers interface logic challenge (nouveau)
            window.location.href = `/logic-challenge/${challenge.logic_id}`;
            
        } else if (challengeType === 'HYBRID') {
            // Redirection vers interface hybride (nouveau)
            window.location.href = `/hybrid-mission/${challengeId}`;
        }
    }

    closeModal() {
        const modal = document.getElementById('hybrid-challenge-modal');
        if (modal) {
            modal.style.opacity = '0';
            setTimeout(() => modal.remove(), 300);
        }
    }

    showRewards(challengeId) {
        // Logique pour afficher les récompenses détaillées
        console.log('Affichage récompenses pour challenge:', challengeId);
    }
}

// Instance globale
const hybridChallengeSystem = new HybridChallengeSystem();

// Fonctions globales (compatibilité)
function startChallenge(challengeId, challengeType = null) {
    hybridChallengeSystem.showChallengeModal(challengeId);
}

function continueWeeklyChallenge() {
    hybridChallengeSystem.showChallengeModal(999);
}

function showRewards(challengeId) {
    hybridChallengeSystem.showRewards(challengeId);
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 Hybrid Challenge System initialisé - Exercices + Logic Challenges');
});

// Export pour debug
window.hybridChallengeSystem = hybridChallengeSystem; 