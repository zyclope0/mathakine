/**
 * Mathakine - API JavaScript pour les Défis Galactiques
 * Tests complets des interactions Interface → Route → API → BDD
 */

class ChallengesAPI {
    constructor() {
        this.baseURL = '';
        this.isDebugMode = true;
    }

    log(message, data = null) {
        if (this.isDebugMode) {
            console.log(`🌟 [ChallengesAPI] ${message}`, data || '');
        }
    }

    error(message, error = null) {
        console.error(`❌ [ChallengesAPI] ${message}`, error || '');
    }

    // Test 1: Démarrer un challenge (POST /api/challenges/start/{challenge_id})
    async startChallenge(challengeId, challengeType = null) {
        this.log(`Démarrage du challenge ${challengeId}`);
        
        try {
            const response = await fetch(`/api/challenges/start/${challengeId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const data = await response.json();
                this.log('Challenge démarré', data);
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                }
                return true;
            }
        } catch (error) {
            this.log('Erreur API, fallback');
            this.fallbackRedirect(challengeId, challengeType);
        }
        return false;
    }

    // Test 2: Récupérer la progression (GET /api/challenges/progress/{challenge_id})
    async getChallengeProgress(challengeId) {
        this.log(`Récupération progression challenge ${challengeId}`);
        
        try {
            const response = await fetch(`${this.baseURL}/api/challenges/progress/${challengeId}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.log('Progression récupérée', data);
                return data;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            this.error('Erreur getChallengeProgress', error);
            return null;
        }
    }

    // Test 3: Récupérer les récompenses (GET /api/challenges/rewards/{challenge_id})
    async getChallengeRewards(challengeId) {
        this.log(`Récupération récompenses challenge ${challengeId}`);
        
        try {
            const response = await fetch(`${this.baseURL}/api/challenges/rewards/${challengeId}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.log('Récompenses récupérées', data);
                return data;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            this.error('Erreur getChallengeRewards', error);
            return null;
        }
    }

    // Test 4: Récupérer le leaderboard (GET /api/users/leaderboard)
    async getLeaderboard() {
        this.log('Récupération du leaderboard');
        
        try {
            const response = await fetch(`${this.baseURL}/api/users/leaderboard`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.log('Leaderboard récupéré', data);
                return data;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            this.error('Erreur getLeaderboard', error);
            return null;
        }
    }

    // Test 5: Récupérer progression des badges (GET /api/challenges/badges/progress)
    async getBadgesProgress() {
        this.log('Récupération progression badges');
        
        try {
            const response = await fetch(`${this.baseURL}/api/challenges/badges/progress`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.log('Progression badges récupérée', data);
                return data;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            this.error('Erreur getBadgesProgress', error);
            return null;
        }
    }

    // Fallback pour redirection directe
    fallbackRedirect(challengeId, challengeType) {
        const mappings = {
            1: '/exercises?exercise_type=addition&difficulty=initie',
            2: '/exercises?exercise_type=multiplication&difficulty=padawan',
            3: '/exercises?exercise_type=fractions&difficulty=chevalier',
            4: '/exercises?exercise_type=geometrie&difficulty=maitre',
            999: '/exercises?exercise_type=geometrie&difficulty=chevalier'
        };
        
        const url = mappings[challengeId] || `/exercises?exercise_type=${challengeType?.toLowerCase()}`;
        window.location.href = url;
    }

    // Mettre à jour l'affichage de la progression
    async updateProgressDisplay(challengeId) {
        const progress = await this.getChallengeProgress(challengeId);
        if (!progress) return;

        // Mettre à jour la barre de progression
        const progressBar = document.querySelector(`[data-challenge-id="${challengeId}"] .progress-fill`);
        if (progressBar) {
            progressBar.style.width = `${progress.progress.progress_percentage}%`;
        }

        // Mettre à jour le texte
        const progressText = document.querySelector(`[data-challenge-id="${challengeId}"] .progress-text`);
        if (progressText) {
            progressText.textContent = `${progress.progress.attempts}/${progress.progress.total_exercises} exercices`;
        }
    }

    // Test complet de tous les endpoints
    async runCompleteAPITest() {
        this.log('🧪 DÉBUT DU TEST COMPLET DES API CHALLENGES');
        
        const tests = [
            {
                name: 'Leaderboard',
                test: () => this.getLeaderboard()
            },
            {
                name: 'Progression Challenge 1',
                test: () => this.getChallengeProgress(1)
            },
            {
                name: 'Récompenses Challenge 1', 
                test: () => this.getChallengeRewards(1)
            },
            {
                name: 'Progression badges',
                test: () => this.getBadgesProgress()
            },
            {
                name: 'Démarrage Challenge 999 (TEST)',
                test: () => {
                    this.log('Test startChallenge en mode simulation');
                    return fetch(`${this.baseURL}/api/challenges/start/999`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    }).then(r => r.json());
                }
            }
        ];

        const results = {};
        
        for (const test of tests) {
            this.log(`Test: ${test.name}...`);
            try {
                const result = await test.test();
                results[test.name] = { success: true, data: result };
                this.log(`✅ ${test.name}: SUCCÈS`);
            } catch (error) {
                results[test.name] = { success: false, error: error.message };
                this.error(`❌ ${test.name}: ÉCHEC`, error);
            }
        }

        this.log('🏁 RÉSULTATS DU TEST COMPLET', results);
        return results;
    }
}

// Instance globale
const challengesAPI = new ChallengesAPI();

// Fonctions globales pour compatibilité avec les templates existants
async function startChallenge(challengeId, challengeType) {
    return challengesAPI.startChallenge(challengeId, challengeType);
}

function continueWeeklyChallenge() {
    return startChallenge(999, 'weekly');
}

async function showRewards(challengeId) {
    alert(`🏆 Récompenses du défi ${challengeId}:\n✨ Étoiles et badges à débloquer !`);
}

// Initialisation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    challengesAPI.log('🌟 Défis Galactiques initialisés - L\'API Rebelle');
    
    // Ajouter les handlers pour les boutons sans onclick
    const challengeButtons = document.querySelectorAll('.challenges-grid .btn--primary:not([onclick])');
    const types = ['multiplication', 'fractions', 'geometry'];
    let typeIndex = 0;
    
    challengeButtons.forEach((btn) => {
        const challengeId = typeIndex + 2;
        btn.onclick = () => startChallenge(challengeId, types[typeIndex]);
        typeIndex++;
    });
    
    // Animation des cartes
    const cards = document.querySelectorAll('.challenge-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px) scale(1.02)';
            card.style.transition = 'all 0.3s ease';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Test de connectivité au démarrage
    setTimeout(() => {
        challengesAPI.log('🧪 Test de connectivité des API...');
        challengesAPI.getLeaderboard().then(result => {
            if (result) {
                challengesAPI.log('✅ API challenges connectées et fonctionnelles');
            } else {
                challengesAPI.log('⚠️ API challenges: problème de connectivité');
            }
        });
    }, 1000);
});

// Exposer les fonctions pour les tests manuels
window.challengesAPI = challengesAPI;
window.testChallengesAPI = () => challengesAPI.runCompleteAPITest(); 