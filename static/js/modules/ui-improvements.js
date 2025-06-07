/**
 * Module d'améliorations UI progressives pour Mathakine
 * 
 * Ce module ajoute des améliorations subtiles à l'interface
 * sans casser les fonctionnalités existantes
 */

export class UIImprovements {
    constructor() {
        this.init();
    }

    init() {
        // Initialisation seulement si le DOM est prêt
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.applyImprovements());
        } else {
            this.applyImprovements();
        }
    }

    applyImprovements() {
        this.enhanceButtons();
        this.enhanceCards();
        this.addRippleEffects();
        this.improveAccessibility();
        this.optimizeMobileExperience();
    }

    /**
     * Améliore progressivement les boutons existants
     */
    enhanceButtons() {
        // Trouve tous les boutons qui pourraient bénéficier des améliorations
        const buttons = document.querySelectorAll('.btn:not(.btn-unified)');
        
        buttons.forEach(btn => {
            // Ajoute la classe unifiée seulement si le bouton n'a pas de styles custom
            if (!btn.hasAttribute('style') && !btn.classList.contains('no-enhance')) {
                btn.classList.add('use-unified-styles');
            }
            
            // Améliore l'accessibilité
            if (!btn.hasAttribute('aria-label') && btn.textContent.trim()) {
                btn.setAttribute('aria-label', btn.textContent.trim());
            }
        });
    }

    /**
     * Améliore les cartes existantes
     */
    enhanceCards() {
        const cards = document.querySelectorAll('.card:not(.card-unified), .exercise-card:not(.card-unified)');
        
        cards.forEach(card => {
            // Animation d'entrée subtile
            if (!card.classList.contains('no-animate')) {
                card.classList.add('animate-in');
                
                // Observer pour animer quand visible
                if ('IntersectionObserver' in window) {
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                entry.target.style.animationDelay = '0.1s';
                                observer.unobserve(entry.target);
                            }
                        });
                    }, { threshold: 0.1 });
                    
                    observer.observe(card);
                }
            }
        });
    }

    /**
     * Ajoute des effets de ripple aux éléments interactifs
     */
    addRippleEffects() {
        const interactiveElements = document.querySelectorAll(
            '.btn:not(.no-ripple), .card:not(.no-ripple), button:not(.no-ripple)'
        );

        interactiveElements.forEach(element => {
            element.addEventListener('click', (e) => {
                const ripple = document.createElement('span');
                ripple.className = 'ripple-effect';
                
                const rect = element.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                
                element.style.position = 'relative';
                element.style.overflow = 'hidden';
                element.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    /**
     * Améliore l'accessibilité générale
     */
    improveAccessibility() {
        // Améliore les liens sans texte descriptif
        document.querySelectorAll('a').forEach(link => {
            if (!link.textContent.trim() && !link.getAttribute('aria-label')) {
                const icon = link.querySelector('i');
                if (icon) {
                    const iconClass = icon.className;
                    if (iconClass.includes('fa-home')) {
                        link.setAttribute('aria-label', 'Accueil');
                    } else if (iconClass.includes('fa-play')) {
                        link.setAttribute('aria-label', 'Démarrer');
                    }
                    // Ajouter d'autres cas selon les besoins
                }
            }
        });

        // Améliore le contraste des textes peu visibles
        document.querySelectorAll('.text-muted, .text-secondary').forEach(element => {
            const bgColor = window.getComputedStyle(element.parentElement).backgroundColor;
            if (bgColor && this.needsBetterContrast(element, bgColor)) {
                element.style.opacity = '0.9';
            }
        });
    }

    /**
     * Optimise l'expérience mobile
     */
    optimizeMobileExperience() {
        if (window.innerWidth <= 768) {
            // Améliore la taille des zones tactiles
            document.querySelectorAll('button, .btn, a').forEach(element => {
                const rect = element.getBoundingClientRect();
                if (rect.height < 44 || rect.width < 44) {
                    element.style.minHeight = '44px';
                    element.style.minWidth = '44px';
                    element.style.padding = 'var(--space-sm) var(--space-md)';
                }
            });

            // Améliore l'espacement vertical sur mobile
            document.querySelectorAll('.card, .exercise-card').forEach(card => {
                if (!card.style.marginBottom) {
                    card.style.marginBottom = 'var(--space-md)';
                }
            });
        }
    }

    /**
     * Vérifie si un élément a besoin d'un meilleur contraste
     */
    needsBetterContrast(element, bgColor) {
        // Logique simplifiée - peut être améliorée avec un calcul de contraste réel
        const isDarkBg = bgColor.includes('0, 0, 0') || bgColor.includes('rgb(0');
        const isLightText = window.getComputedStyle(element).color.includes('255');
        return isDarkBg && !isLightText;
    }
}

// Style CSS pour l'effet ripple
const style = document.createElement('style');
style.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    /* Amélioration du focus pour l'accessibilité */
    *:focus-visible {
        outline: 2px solid var(--focus-color, #9c6eff);
        outline-offset: 2px;
    }
    
    /* Amélioration des transitions pour enfants autistes */
    @media (prefers-reduced-motion: no-preference) {
        .animate-in {
            animation-duration: 0.5s;
            animation-fill-mode: both;
        }
    }
`;

document.head.appendChild(style);

// Auto-initialisation
const uiImprovements = new UIImprovements();
export default uiImprovements; 