/**
 * Gestion de la soumission des exercices et intégration avec le système de recommandations
 */

// Obtenir les paramètres d'URL pour récupérer l'ID de recommandation s'il existe
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        recommendationId: params.get('rec_id')
    };
}

// Soumettre une réponse à un exercice
async function submitAnswer(exerciseId, answer) {
    try {
        // Préparer les données à envoyer
        const data = {
            exercise_id: exerciseId,
            answer: answer
        };
        
        // Faire la requête API
        const response = await fetch('/api/submit-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        // Traiter la réponse
        const result = await response.json();
        
        // Si l'exercice provient d'une recommandation, la marquer comme complétée
        const { recommendationId } = getUrlParams();
        if (recommendationId) {
            await markRecommendationAsCompleted(recommendationId);
        }
        
        return result;
    } catch (error) {
        console.error('Erreur lors de la soumission de la réponse:', error);
        return { error: 'Une erreur est survenue lors de la soumission' };
    }
}

// Marquer une recommandation comme complétée
async function markRecommendationAsCompleted(recommendationId) {
    try {
        const response = await fetch('/api/recommendations/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ recommendation_id: recommendationId })
        });
        
        const result = await response.json();
        console.log('Recommandation marquée comme complétée:', result);
        return result;
    } catch (error) {
        console.error('Erreur lors du marquage de la recommandation:', error);
        return { error: 'Une erreur est survenue lors du marquage de la recommandation' };
    }
}

// Générer un nouvel exercice, éventuellement à partir d'une recommandation
async function generateNewExercise(exerciseType, difficulty, fromRecommendation = false) {
    try {
        let url = '/api/exercises/generate';
        const params = new URLSearchParams();
        
        if (exerciseType) {
            params.append('exercise_type', exerciseType);
        }
        
        if (difficulty) {
            params.append('difficulty', difficulty);
        }
        
        // Ajouter les paramètres à l'URL si nécessaire
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const result = await response.json();
        
        // Si l'exercice est généré à partir d'une recommandation, ajouter le paramètre à l'URL
        if (fromRecommendation && result.id) {
            window.location.href = `/exercise/${result.id}?rec_id=${fromRecommendation}`;
            return null;
        }
        
        return result;
    } catch (error) {
        console.error('Erreur lors de la génération d\'un exercice:', error);
        return { error: 'Une erreur est survenue lors de la génération de l\'exercice' };
    }
}

// Exposer les fonctions qui seront utilisées par d'autres scripts
window.exerciseAPI = {
    submitAnswer,
    generateNewExercise,
    markRecommendationAsCompleted
}; 