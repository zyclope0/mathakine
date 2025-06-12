# 🤖 AI AGENT CONTEXT - MATHAKINE PROJECT (EXHAUSTIVE)

> **CRITICAL**: This file is optimized for AI agents. All rules and constraints are MANDATORY.

## 🎯 PROJECT ESSENCE

**MATHAKINE** = Educational math platform for autistic children with Star Wars theme
- **Target**: Adaptive math learning for 6-16 years old with special needs
- **Theme**: Complete Star Wars universe (children are "Math Padawans")
- **Status**: ✅ PRODUCTION READY - Fully functional
- **Architecture**: Dual backend FastAPI (pure API) + Starlette (web interface)
- **Database**: PostgreSQL (production) + SQLite (development)
- **Version**: 4.0 (January 2025) with complete gamification

---

## 🚨 CRITICAL CONSTRAINTS - NEVER VIOLATE

### **1. MANDATORY PARAMETER ORDER**
```python
# ✅ ALWAYS CORRECT
adapt_enum_for_db(enum_name, value, db)  # enum_name FIRST, value SECOND

# ❌ NEVER DO THIS - WILL BREAK SYSTEM
adapt_enum_for_db(value, enum_name, db)  # WRONG ORDER = CRITICAL FAILURE
```

### **2. POSTGRESQL JSON STORAGE - MANDATORY CONVERSION**
```python
# ✅ ALWAYS REQUIRED for PostgreSQL
if isinstance(data["hints"], list):
    data["hints"] = json.dumps(data["hints"])

# ❌ NEVER store Python lists directly in PostgreSQL JSON fields
data["hints"] = ["hint1", "hint2"]  # WILL FAIL in PostgreSQL
```

### **3. PYDANTIC SCHEMAS - MODERN FORMAT ONLY**
```python
# ✅ CURRENT SCHEMA FORMAT (use this)
class LogicChallengeBase(BaseModel):
    hints: Optional[List[str]] = Field(None, description="Liste des indices")
    user_solution: str = Field(..., description="Réponse utilisateur")

# ❌ OBSOLETE FORMAT (never use)
# hint_level1: str, hint_level2: str, hint_level3: str
# user_answer: str
```

### **4. TEST FIXTURES - EXPLICIT DATES MANDATORY**
```python
# ✅ ALWAYS REQUIRED
created_at=datetime.now(timezone.utc)  # EXPLICIT date
updated_at=datetime.now(timezone.utc)  # EXPLICIT date

# ❌ NEVER USE None - CAUSES PYDANTIC ERRORS
created_at=None, updated_at=None
```

### **5. AUTHENTICATION - CURRENT USER RETRIEVAL**
```python
# ✅ ALWAYS USE get_current_user() for handlers
user = get_current_user(request)
user_id = user.id

# ❌ NEVER hardcode user IDs
user_id = 1  # CRITICAL ERROR - breaks multi-user system
```

### **6. JAVASCRIPT AUTHENTICATION - CREDENTIALS MANDATORY**
```javascript
// ✅ ALWAYS INCLUDE credentials for authenticated requests
fetch('/api/submit-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // CRITICAL for session cookies
    body: JSON.stringify(data)
});

// ❌ NEVER omit credentials - causes 401 errors
fetch('/api/submit-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)  // Missing credentials!
});
```

---

## 🏗️ TECHNICAL ARCHITECTURE

### **Entry Points**
- **enhanced_server.py** : Main server (web interface + minimal API)
- **app/main.py** : Pure REST API (testing, debugging, external clients)
- **mathakine_cli.py** : Complete CLI interface (6 commands)

### **Core Stack**
```yaml
Backend: 
  - FastAPI 0.115.12 (pure REST API)
  - Starlette 0.31.1 (web interface)
  - SQLAlchemy 2.0.40 ORM + Alembic migrations
Database:
  - PostgreSQL 14+ (production) 
  - SQLite (development)
  - Perfect compatibility between both
Frontend:
  - Jinja2 templates (Star Wars holographic theme)
  - Modular CSS with variable system
  - Vanilla JavaScript + ES6 modules
Tests:
  - pytest with 4-level structure (unit/api/integration/functional)
  - CI/CD with intelligent test classification
Security:
  - JWT tokens with HTTP-only cookies
  - Bcrypt password hashing
  - CORS configuration
  - Rate limiting protection
```

### **Directory Structure - RESPECT ORGANIZATION**
```
mathakine/
├── app/                    # FastAPI application
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas  
│   ├── services/          # Business logic
│   ├── api/endpoints/     # REST endpoints
│   ├── core/              # Configuration & constants
│   ├── utils/             # Helper functions
│   └── db/                # Database initialization
├── server/                # Starlette server modules
│   ├── handlers/          # Business logic by domain
│   ├── views.py           # HTML page management
│   └── routes.py          # Route configuration
├── templates/             # Jinja2 templates
├── static/                # CSS/JS/assets
│   ├── styles/           # CSS files (modular)
│   ├── js/               # JavaScript modules
│   ├── img/              # Images and icons
│   └── sounds/           # Audio feedback
├── tests/                 # 4-level test structure
├── scripts/               # Utility scripts
├── migrations/            # Alembic migrations
└── docs/                  # Complete documentation
```

---

## 🎨 UI/UX SYSTEM - STAR WARS HOLOGRAPHIC THEME

### **Design Principles - NEVER VIOLATE**
1. **Star Wars Immersion** : All text, colors, animations must fit theme
2. **Accessibility First** : Support for autistic children (colors, animations, fonts)
3. **Progressive Enhancement** : Basic functionality without JavaScript
4. **Mobile Responsive** : Works on all screen sizes
5. **Performance Optimized** : Fast loading, efficient animations

### **Color Palette - MANDATORY USAGE**
```css
/* Primary Colors - Star Wars Theme */
:root {
  --sw-gold: #FFD700;           /* Jedi gold */
  --sw-blue: #00BFFF;           /* Lightsaber blue */
  --sw-purple: #8b5cf6;         /* Force purple (MAIN THEME) */
  --sw-green: #00FF41;          /* Jedi green */
  --sw-red: #FF073A;            /* Sith red */
  --sw-dark: #0D0D0D;           /* Space black */
  --sw-gray: #2D2D2D;           /* Imperial gray */
  
  /* Semantic Colors */
  --success: #22c55e;           /* Exercise success */
  --warning: #f59e0b;           /* Warnings */
  --error: #ef4444;             /* Errors */
  --info: #3b82f6;              /* Information */
  
  /* Background System */
  --bg-primary: rgba(13, 13, 13, 0.95);    /* Main background */
  --bg-secondary: rgba(45, 45, 45, 0.8);   /* Card backgrounds */
  --bg-glass: rgba(255, 255, 255, 0.08);   /* Glass effect */
}
```

### **Typography System - CONSISTENT USAGE**
```css
/* Font Stack - Star Wars Themed */
:root {
  --font-primary: 'Orbitron', 'Roboto', sans-serif;     /* Headers */
  --font-secondary: 'Source Sans Pro', sans-serif;       /* Body text */
  --font-monospace: 'Fira Code', 'Courier New', mono;   /* Code */
  
  /* Font Sizes - Responsive Scale */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
}
```

### **Animation System - PERFORMANCE OPTIMIZED**
```css
/* Animation Timing - Consistent Throughout */
:root {
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
  
  /* Special Effects */
  --glow-effect: 0 0 20px rgba(139, 92, 246, 0.5);
  --hover-transform: translateY(-2px);
  --press-transform: translateY(0) scale(0.98);
}

/* MANDATORY: Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### **CSS Architecture - MODULAR SYSTEM**
```css
/* Import Order - NEVER CHANGE */
@import 'normalize.css';      /* Reset styles */
@import 'variables.css';      /* CSS variables */
@import 'utils.css';          /* Utility classes */
@import 'components.css';     /* Component styles */
@import 'space-theme.css';    /* Star Wars theme */
@import 'animations.css';     /* Animation effects */
```

### **Utility Classes - USE THESE INSTEAD OF INLINE STYLES**
```css
/* Spacing System */
.mt-1 { margin-top: 0.25rem; }    /* 4px */
.mt-2 { margin-top: 0.5rem; }     /* 8px */
.mt-3 { margin-top: 0.75rem; }    /* 12px */
.mt-4 { margin-top: 1rem; }       /* 16px */
/* ... similar for all directions and padding */

/* Flexbox Utilities */
.d-flex { display: flex; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.align-center { align-items: center; }
.flex-column { flex-direction: column; }

/* Text Utilities */
.text-center { text-align: center; }
.text-primary { color: var(--sw-purple); }
.text-gold { color: var(--sw-gold); }
.fw-bold { font-weight: 700; }

/* Background Utilities */
.bg-glass { background: var(--bg-glass); }
.bg-primary { background: var(--bg-primary); }
```

### **Component Patterns - REUSABLE STYLES**
```css
/* Card Pattern - Use for all card components */
.card {
  background: var(--bg-glass);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 1.5rem;
  transition: var(--transition-normal);
}

.card:hover {
  transform: var(--hover-transform);
  box-shadow: var(--glow-effect);
  border-color: var(--sw-purple);
}

/* Button Pattern - Star Wars themed */
.btn-primary {
  background: linear-gradient(135deg, var(--sw-purple), var(--sw-blue));
  border: none;
  border-radius: 8px;
  color: white;
  padding: 0.75rem 1.5rem;
  font-family: var(--font-primary);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.btn-primary:hover {
  transform: var(--hover-transform);
  box-shadow: var(--glow-effect);
}

.btn-primary:active {
  transform: var(--press-transform);
}
```

### **Accessibility Features - MANDATORY IMPLEMENTATION**
```css
/* High Contrast Mode */
.high-contrast {
  --sw-purple: #ffffff;
  --sw-gold: #ffff00;
  --bg-primary: #000000;
  --bg-secondary: #333333;
}

/* Large Text Mode */
.large-text {
  font-size: 120% !important;
  line-height: 1.6 !important;
}

/* Dyslexia-Friendly Mode */
.dyslexia-friendly {
  font-family: 'OpenDyslexic', sans-serif !important;
  letter-spacing: 0.1em !important;
  word-spacing: 0.2em !important;
}

/* Reduced Motion Mode */
.reduced-motion * {
  animation: none !important;
  transition: none !important;
}
```

### **JavaScript Patterns - CONSISTENT USAGE**
```javascript
// ✅ CORRECT: Modern ES6+ patterns
class ExerciseManager {
  constructor() {
    this.currentExercise = null;
    this.bindEvents();
  }
  
  async submitAnswer(exerciseId, answer) {
    try {
      const response = await fetch('/api/submit-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',  // MANDATORY for auth
        body: JSON.stringify({ 
          exercise_id: exerciseId, 
          selected_answer: answer 
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Submit error:', error);
      this.showError('Erreur de connexion');
      throw error;
    }
  }
  
  bindEvents() {
    // Use event delegation for dynamic content
    document.addEventListener('click', (e) => {
      if (e.target.matches('.answer-choice')) {
        this.handleAnswerClick(e);
      }
    });
  }
}

// ❌ NEVER USE: jQuery or old JavaScript patterns
// $('#element').click(function() { ... });  // NO JQUERY
```

---

## 🎲 EXERCISE SYSTEM - 9 TYPES OPERATIONAL

### **Exercise Types - ALL IMPLEMENTED**
```python
# Available in ExerciseTypes.ALL_TYPES
ADDITION = "addition"
SUBTRACTION = "soustraction" 
MULTIPLICATION = "multiplication"
DIVISION = "division"
FRACTIONS = "fractions"        # NEW: Complete fractions operations
GEOMETRIE = "geometrie"        # NEW: Perimeters, areas, diagonals
TEXTE = "texte"               # NEW: Logic problems and riddles
DIVERS = "divers"             # NEW: Money, speed, percentages, probabilities
MIXTE = "mixte"               # Intelligent combinations
```

### **Difficulty Levels - STAR WARS THEME**
```python
INITIE = "initie"        # Beginner (numbers 1-10)
PADAWAN = "padawan"      # Intermediate (numbers 10-50)
CHEVALIER = "chevalier"  # Advanced (numbers 50-100)
MAITRE = "maitre"        # Expert (numbers 100-500)
```

### **Generation Functions - PLACEMENT CRITICAL**
```python
# ✅ CORRECT PLACEMENT for standard exercises
def generate_simple_exercise(exercise_type, difficulty):
    # Place new generators HERE, not in generate_ai_exercise()
    
# ✅ CORRECT PLACEMENT for AI exercises  
def generate_ai_exercise(exercise_type, difficulty):
    # Only AI-enhanced versions with Star Wars narratives
```

### **Exercise Data Structure - MANDATORY FORMAT**
```python
# ✅ CORRECT exercise structure
exercise_data = {
    "exercise_type": "addition",           # From ExerciseTypes
    "difficulty": "padawan",               # From difficulty levels
    "title": "Addition Padawan",           # User-friendly title
    "question": "Luke a 15 cristaux...",   # Star Wars themed question
    "correct_answer": "23",                # String format
    "choices": ["23", "25", "21", "27"],   # 4 choices as strings
    "explanation": "Pour calculer...",     # Step-by-step explanation
    "tags": "algorithmique,addition",      # Comma-separated tags
    "answer_type": "number",               # Type hint for validation
    "ai_generated": False,                 # Boolean flag
    "hint": "Additionne les cristaux..."   # Optional hint
}

# ❌ NEVER USE inconsistent formats
# choices: [23, 25, 21, 27]  # Numbers instead of strings
# correct_answer: 23         # Number instead of string
```

---

## 🧪 VALIDATION SYSTEM - MANDATORY COMMANDS

### **Critical Test Validation**
```bash
# ✅ MUST ALWAYS PASS 6/6 tests
python -m pytest tests/functional/test_logic_challenge_isolated.py -v

# Expected result: 6 PASSED ✅, 0 FAILED ❌
```

### **CI/CD Test Classification**
```bash
# 🔴 Critical tests (BLOCKING)
python -m pytest tests/functional/ -v

# 🟡 Important tests (NON-BLOCKING)  
python -m pytest tests/integration/ -v

# 🟢 Complementary tests (INFORMATIVE)
python -m pytest tests/unit/test_cli.py -v
```

### **Server Startup**
```bash
# Main server with web interface
python enhanced_server.py

# API-only server
python app/main.py

# CLI interface
python mathakine_cli.py run
```

---

## 📊 DATABASE SYSTEM

### **Tables Architecture**
```sql
-- Core tables
exercises         # 9 exercise types
users            # With gamification (points, jedi_rank)
attempts         # Exercise attempts
progress         # Individual user statistics  
user_stats       # Global aggregated statistics

-- Gamification
achievements     # Badge definitions
user_achievements # Badges earned by users

-- Legacy (PROTECTED)
results, statistics, schema_version  # NEVER modify these
```

### **Enum Mapping System**
```python
# PostgreSQL/SQLite compatibility
ENUM_MAPPING = {
    ("LogicChallengeType", "sequence"): "SEQUENCE",
    ("AgeGroup", "10-12"): "GROUP_10_12",
    # Never modify mapping without testing
}
```

### **Database Models - RELATIONSHIP PATTERNS**
```python
# ✅ CORRECT: Use these relationship patterns
class User(Base):
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Required fields with validation
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Relationships with CASCADE
    exercises = relationship("Exercise", back_populates="creator", 
                           cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="user", 
                          cascade="all, delete-orphan")
    
    # Gamification fields
    total_points = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    jedi_rank = Column(String(50), default="youngling")
    
    # Timestamps - ALWAYS INCLUDE
    created_at = Column(TIMESTAMP(timezone=True), 
                       server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), 
                       server_default=func.now(), 
                       onupdate=func.now())
```

---

## 🎖️ BADGE SYSTEM - COMPLETE GAMIFICATION

### **Badge Categories - ALL IMPLEMENTED**
```python
# Progression badges (Bronze/Silver/Gold)
"first_steps"    # 10 pts - "Éveil de la Force"
"padawan_path"   # 50 pts - "Apprenti Jedi"  
"knight_trial"   # 100 pts - "Chevalier Jedi"

# Mastery badges (Type-specific)
"addition_master"      # 100 pts - 20 consecutive additions
"subtraction_master"   # 100 pts - 20 consecutive subtractions
"multiplication_master" # 100 pts - 20 consecutive multiplications
"division_master"      # 100 pts - 20 consecutive divisions

# Special badges (Achievement-based)
"speed_demon"    # 75 pts - Exercise < 5 seconds
"perfect_day"    # 150 pts - All daily exercises correct
"streak_10"      # 50 pts - 10 exercise streak
"streak_50"      # 200 pts - 50 exercise streak
```

### **Badge Attribution Logic - CRITICAL PATTERNS**
```python
# ✅ CORRECT: Badge checking after exercise completion
def record_attempt(self, attempt_data):
    """Record attempt and check badges - ATOMIC TRANSACTION"""
    with TransactionManager(self.db) as tm:
        # 1. Record the attempt
        attempt = Attempt(**attempt_data)
        self.db.add(attempt)
        self.db.flush()  # Get attempt ID
        
        # 2. Update statistics
        self.update_progress(attempt.user_id, attempt.exercise_id, attempt.is_correct)
        
        # 3. Check and award badges - MANDATORY
        if attempt.is_correct:
            badge_service = BadgeService(self.db)
            new_badges = badge_service.check_and_award_badges(
                user_id=attempt.user_id,
                attempt_data={
                    'exercise_type': exercise.exercise_type,
                    'difficulty': exercise.difficulty,
                    'time_spent': attempt.time_spent,
                    'is_correct': attempt.is_correct
                }
            )
            
            if new_badges:
                logger.info(f"🎖️ {len(new_badges)} badges awarded to user {attempt.user_id}")
        
        tm.commit()  # Atomic commit
        return attempt
```

---

## 🔧 ERROR PATTERNS - NEVER REPEAT

### **Critical Errors That Break System**
```python
# ❌ PARAMETER ORDER ERROR
adapt_enum_for_db(value, enum_name)  # BREAKS enum mapping

# ❌ POSTGRESQL JSON ERROR  
data["hints"] = ["hint1"]  # BREAKS PostgreSQL storage

# ❌ AUTHENTICATION ERROR
user_id = 1  # BREAKS multi-user functionality

# ❌ DATE ERROR IN FIXTURES
created_at=None  # BREAKS Pydantic validation

# ❌ OBSOLETE SCHEMA FIELDS
hint_level1="text"  # BREAKS modern schema validation

# ❌ MISSING CREDENTIALS IN FETCH
fetch('/api/endpoint')  # BREAKS authentication

# ❌ HARDCODED VALUES IN HANDLERS
def get_stats(request):
    user_id = 1  # BREAKS multi-user system
```

### **Patterns That Always Work**
```python
# ✅ CORRECT PATTERNS
adapt_enum_for_db("LogicChallengeType", "sequence", db)
data["hints"] = json.dumps(["hint1", "hint2"])
user = get_current_user(request); user_id = user.id
created_at=datetime.now(timezone.utc)
hints: Optional[List[str]] = Field(None)

# ✅ CORRECT JavaScript fetch
fetch('/api/endpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data)
});
```

---

## 🔐 SECURITY SYSTEM - MANDATORY IMPLEMENTATION

### **Authentication Flow - NEVER CHANGE**
```python
# ✅ CORRECT: JWT with HTTP-only cookies
@router.post("/login")
async def login(
    credentials: LoginRequest, 
    response: Response,
    db: Session = Depends(get_db)
):
    # 1. Validate credentials
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # 2. Create JWT token
    access_token = create_access_token(data={"sub": user.username})
    
    # 3. Set HTTP-only cookie - SECURE
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,      # MANDATORY: Prevents XSS
        secure=True,        # HTTPS only in production
        samesite="lax",     # CSRF protection
        max_age=1800        # 30 minutes
    )
    
    return {"message": "Login successful"}

# ❌ NEVER store tokens in localStorage or sessionStorage
# localStorage.setItem('token', token);  // SECURITY RISK
```

### **Password Security - MANDATORY STANDARDS**
```python
# ✅ CORRECT: Bcrypt with salt rounds
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password with bcrypt - 12 rounds minimum"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ❌ NEVER use weak hashing
# hashlib.md5(password.encode()).hexdigest()  // INSECURE
# hashlib.sha1(password.encode()).hexdigest()  // INSECURE
```

### **Input Validation - MANDATORY PATTERNS**
```python
# ✅ CORRECT: Pydantic validation with constraints
from pydantic import BaseModel, Field, validator

class ExerciseCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    question: str = Field(..., min_length=10, max_length=2000)
    exercise_type: str = Field(..., regex="^(addition|soustraction|multiplication|division|fractions|geometrie|texte|divers|mixte)$")
    difficulty: str = Field(..., regex="^(initie|padawan|chevalier|maitre)$")
    
    @validator('title')
    def validate_title(cls, v):
        # Sanitize HTML and dangerous characters
        return html.escape(v.strip())
    
    @validator('question')
    def validate_question(cls, v):
        if '<script>' in v.lower():
            raise ValueError('Script tags not allowed')
        return html.escape(v.strip())
```

---

## ⚡ PERFORMANCE OPTIMIZATION - MANDATORY PATTERNS

### **Database Query Optimization**
```python
# ✅ CORRECT: Optimized queries with eager loading
def get_user_with_stats(db: Session, user_id: int):
    """Get user with related data in single query"""
    return db.query(User)\
        .options(
            joinedload(User.attempts),
            joinedload(User.user_achievements)
        )\
        .filter(User.id == user_id)\
        .first()

# ✅ CORRECT: Pagination for large datasets
def get_exercises_paginated(db: Session, skip: int = 0, limit: int = 20):
    """Paginated exercise retrieval"""
    return db.query(Exercise)\
        .filter(Exercise.is_active == True)\
        .order_by(Exercise.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

# ❌ NEVER use N+1 queries
# for user in users:
#     attempts = db.query(Attempt).filter(Attempt.user_id == user.id).all()
```

### **Caching Strategy - IMPLEMENTATION REQUIRED**
```python
# ✅ CORRECT: Redis caching for expensive operations
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=100)
def get_exercise_statistics(exercise_type: str, difficulty: str):
    """Cache exercise statistics for 15 minutes"""
    cache_key = f"stats:{exercise_type}:{difficulty}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Expensive database query
    stats = calculate_exercise_statistics(exercise_type, difficulty)
    
    # Cache for 15 minutes
    redis_client.setex(cache_key, 900, json.dumps(stats))
    return stats
```

### **Frontend Performance - MANDATORY OPTIMIZATIONS**
```javascript
// ✅ CORRECT: Debounced input handling
class SearchManager {
  constructor() {
    this.searchTimeout = null;
    this.bindEvents();
  }
  
  bindEvents() {
    const searchInput = document.getElementById('search');
    searchInput.addEventListener('input', (e) => {
      this.debounceSearch(e.target.value);
    });
  }
  
  debounceSearch(query) {
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
      this.performSearch(query);
    }, 300); // 300ms debounce
  }
  
  async performSearch(query) {
    if (query.length < 2) return;
    
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        credentials: 'include'
      });
      const results = await response.json();
      this.displayResults(results);
    } catch (error) {
      console.error('Search error:', error);
    }
  }
}

// ❌ NEVER perform search on every keystroke
// input.addEventListener('input', (e) => {
//   performSearch(e.target.value);  // Too frequent API calls
// });
```

---

## 📝 LOGGING SYSTEM - MANDATORY USAGE

### **Logging Configuration - STANDARDIZED**
```python
# ✅ CORRECT: Use centralized logging
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Log levels and usage
logger.debug("Detailed information for debugging")
logger.info("General information about program execution")
logger.warning("Something unexpected happened")
logger.error("A serious problem occurred")
logger.critical("A very serious error occurred")

# ✅ CORRECT: Structured logging with context
logger.bind(
    user_id=user.id,
    exercise_type="addition",
    difficulty="padawan"
).info("Exercise attempt recorded")

# ✅ CORRECT: Exception logging
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed", extra={
        "user_id": user_id,
        "operation": "exercise_generation"
    })

# ❌ NEVER use print() statements in production
# print(f"User {user_id} logged in")  // Use logger instead
```

### **Log File Structure - AUTOMATED ROTATION**
```
logs/
├── debug.log          # Detailed debugging information
├── info.log           # General application flow
├── warning.log        # Warning messages
├── error.log          # Error messages
├── critical.log       # Critical system errors
└── archived/          # Rotated log files
    ├── debug.2025-01-15.zip
    └── error.2025-01-14.zip
```

---

## 🚀 DEVELOPMENT WORKFLOW

### **Before Any Code Change**
1. **Read current context** (this file)
2. **Understand constraints** (critical rules above)
3. **Check existing patterns** (follow established code)
4. **Plan validation** (which tests to run)
5. **Review UI/UX guidelines** (if touching interface)

### **After Any Code Change**
1. **Immediate testing**: Run functional tests
2. **Validation**: Check enum mappings if modified
3. **UI verification**: Test visual changes on different screens
4. **Performance check**: Ensure no regression in load times
5. **Documentation**: Update context if major change
6. **Commit**: Only if critical tests pass

### **Debugging Process**
1. **Isolated tests**: Test specific functionality
2. **Detailed logs**: Use structured logging with context
3. **Browser devtools**: Check console, network, performance
4. **Database queries**: Verify data integrity
5. **Immediate validation**: Test after each micro-fix
6. **Context update**: Document solution for future

---

## 🎯 CURRENT OPERATIONAL STATUS

### **100% Functional Features**
- ✅ **9 exercise types** × 4 difficulty levels = 36 combinations
- ✅ **Badge system** with automatic attribution (6 badges)
- ✅ **Real-time statistics** with immediate updates
- ✅ **Authentication** with JWT + HTTP-only cookies
- ✅ **Dashboard** with authentic user data and charts
- ✅ **Premium UI** with Star Wars holographic theme
- ✅ **Accessibility** with 4 support modes (contrast, large text, reduced motion, dyslexia)
- ✅ **Mobile responsive** design for all screen sizes
- ✅ **Performance optimized** with caching and lazy loading

### **Test Results (Must Maintain)**
- ✅ **Functional tests**: 6/6 pass (100% success)
- ✅ **Code coverage**: 52% (improving)
- ✅ **PostgreSQL compatibility**: Perfect enum mapping
- ✅ **JSON format**: Compatible with PostgreSQL native
- ✅ **UI tests**: All components render correctly
- ✅ **Performance**: Page load < 2 seconds

### **Server Configuration**
- **URL**: http://localhost:8000
- **Test credentials**: `test_user` / `test_password`
- **Database**: PostgreSQL connected (mathakine_test_gii8)
- **Mode**: Debug with auto-reload
- **Logs**: Structured logging to files with rotation

---

## 📜 PROJECT PHILOSOPHY

### **Core Principles**
1. **Never break existing functionality** - Always test before commit
2. **Maintain Star Wars immersion** - All text should fit theme
3. **Prioritize accessibility** - Support for autistic children needs
4. **Progressive enhancement** - Basic functionality works everywhere
5. **Documentation sync** - Always update context after changes
6. **Performance first** - Optimize for speed and efficiency
7. **Security by design** - Never compromise on security

### **Code Quality Standards**
1. **Explicit over implicit** - Clear variable names, explicit dates
2. **Fail fast** - Validate inputs early, use proper error handling
3. **Test-driven stability** - All changes must pass functional tests
4. **Consistent patterns** - Follow established code patterns
5. **Future-proof design** - Write code that can evolve
6. **DRY principle** - Don't repeat yourself, use utilities
7. **SOLID principles** - Single responsibility, open/closed, etc.

### **User Experience Focus**
1. **Educational effectiveness** - Math learning is primary goal
2. **Motivational design** - Gamification encourages progress
3. **Inclusive accessibility** - Works for different ability levels
4. **Immediate feedback** - Real-time validation and encouragement
5. **Parent transparency** - Clear progress tracking for families
6. **Cross-device consistency** - Same experience everywhere
7. **Offline resilience** - Basic functionality without network

---

## 🔍 REFERENCE FILES - QUICK ACCESS

### **Critical Configuration**
- `app/core/constants.py` - Exercise types, difficulty levels, limits
- `app/core/messages.py` - AI prompts, explanations, UI text
- `app/core/config.py` - Database, security, environment settings
- `app/core/logging_config.py` - Centralized logging configuration

### **Business Logic**  
- `app/services/exercise_service.py` - Exercise CRUD and attempt recording
- `app/services/badge_service.py` - Badge logic and automatic attribution
- `app/services/auth_service.py` - Authentication and user management
- `server/exercise_generator.py` - Exercise generation (9 types)

### **Database Mappings**
- `app/utils/db_helpers.py` - Enum mapping functions (PostgreSQL/SQLite)
- `app/models/` - SQLAlchemy models with relationships
- `app/schemas/` - Pydantic schemas for validation
- `migrations/` - Alembic database migrations

### **Frontend Components**
- `templates/base.html` - Base template with navigation
- `static/styles/variables.css` - CSS variables and theme
- `static/styles/utils.css` - Utility classes
- `static/js/` - JavaScript modules and components

### **Testing**
- `tests/functional/test_logic_challenge_isolated.py` - Must pass 6/6
- `tests/conftest.py` - Test configuration and fixtures
- `scripts/pre_commit_check.py` - CI/CD validation

---

## ⚡ EMERGENCY COMMANDS

### **If System Broken**
```bash
# 1. Check functional tests immediately
python -m pytest tests/functional/test_logic_challenge_isolated.py -v

# 2. Verify server startup
python enhanced_server.py

# 3. Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}'

# 4. Check database connection
python -c "from app.db.init_db import get_db; print('DB OK' if next(get_db()) else 'DB FAIL')"
```

### **If UI Issues**
```bash
# 1. Check CSS compilation
ls -la static/styles/

# 2. Verify JavaScript modules
python -m http.server 8080 --directory static/

# 3. Test responsive design
# Use browser dev tools with different viewports

# 4. Check accessibility
# Use browser accessibility audits (Lighthouse)
```

### **If Enum Errors**
```python
# Verify enum values
from app.models.logic_challenge import LogicChallengeType
print(f"SEQUENCE: {LogicChallengeType.SEQUENCE.value}")  # Must be "sequence"

# Test mapping function
from app.utils.db_helpers import adapt_enum_for_db
result = adapt_enum_for_db("LogicChallengeType", "sequence", None)
print(f"Result: {result}")  # Must be "SEQUENCE"
```

### **If Database Issues**
```bash
# Check PostgreSQL connection
python -c "from app.db.init_db import create_tables_with_test_data; create_tables_with_test_data()"

# Verify test user exists
python -c "from app.services.auth_service import get_user_by_username; from app.db.init_db import get_db; print(get_user_by_username(next(get_db()), 'test_user'))"

# Run Alembic migrations
alembic upgrade head
```

---

## 🎯 SUCCESS METRICS - MAINTAIN THESE

### **Technical Metrics**
- **Functional tests**: 6/6 must pass always
- **Code coverage**: Target 60%+ (currently 52%)
- **Server startup**: < 5 seconds  
- **API response**: < 200ms average
- **Page load time**: < 2 seconds on 3G
- **Lighthouse score**: > 90 for performance, accessibility

### **User Experience Metrics**  
- **Exercise generation**: < 1 second
- **Badge attribution**: Immediate after exercise completion
- **Dashboard update**: Real-time statistics display
- **Authentication**: Seamless login/logout flow
- **Mobile responsiveness**: Works on 320px+ screens
- **Accessibility**: WCAG 2.1 AA compliance

### **Quality Indicators**
- **Zero enum mapping errors** in PostgreSQL
- **Zero Pydantic validation errors** in tests
- **Zero authentication failures** in handlers
- **100% Star Wars theme consistency** in UI text
- **Zero console errors** in browser
- **Zero CSS validation errors**

---

## � DEVELOPMENT BEST PRACTICES - MANDATORY STANDARDS

### **Python Code Standards - NEVER VIOLATE**
```python
# ✅ CORRECT: Type hints are MANDATORY
def calculate_points(user_id: int, correct_answers: int) -> int:
    """Calculate user points based on correct answers."""
    return correct_answers * 10

# ✅ CORRECT: Docstrings for all functions
def process_exercise_attempt(attempt_data: dict) -> dict:
    """
    Process an exercise attempt and update user statistics.
    
    Args:
        attempt_data: Dictionary containing attempt information
        
    Returns:
        Dictionary with processing results
        
    Raises:
        ValidationError: If attempt_data is invalid
        DatabaseError: If database operation fails
    """
    pass

# ✅ CORRECT: Error handling with specific exceptions
try:
    result = risky_database_operation()
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise DatabaseError("Failed to process attempt")
except ValidationError as e:
    logger.warning(f"Validation error: {e}")
    raise HTTPException(400, "Invalid data format")

# ❌ NEVER USE: Bare except clauses
# try:
#     risky_operation()
# except:  # NEVER do this
#     pass
```

### **FastAPI Standards - CONSISTENT PATTERNS**
```python
# ✅ CORRECT: Endpoint structure with proper dependencies
@router.post("/exercises/attempt", response_model=AttemptResponse)
async def submit_exercise_attempt(
    attempt: AttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AttemptResponse:
    """Submit an exercise attempt - STAR WARS THEMED RESPONSE"""
    try:
        # Validate attempt data
        if not attempt.exercise_id:
            raise HTTPException(400, "L'exercice est requis, jeune Padawan")
        
        # Process attempt
        service = ExerciseService(db)
        result = service.record_attempt(
            user_id=current_user.id,
            attempt_data=attempt.dict()
        )
        
        return AttemptResponse(
            success=True,
            message="Tentative enregistrée avec succès !",
            data=result
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error for user {current_user.id}: {e}")
        raise HTTPException(400, f"Données invalides: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(500, "Une erreur inattendue s'est produite")

# ✅ CORRECT: Response models with Star Wars theme
class AttemptResponse(BaseModel):
    success: bool
    message: str = Field(..., description="Message en français avec thème Star Wars")
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Excellente réponse, jeune Padawan !",
                "data": {"points_earned": 10, "badges_unlocked": []}
            }
        }
```

### **Database Best Practices - MANDATORY PATTERNS**
```python
# ✅ CORRECT: Transaction management
from contextlib import contextmanager

@contextmanager
def transaction_scope(db_session):
    """Database transaction context manager."""
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()

# ✅ CORRECT: Query optimization with indexes
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)  # INDEXED
    email = Column(String(255), unique=True, index=True)     # INDEXED
    created_at = Column(TIMESTAMP(timezone=True), index=True) # INDEXED for queries
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_user_activity', 'username', 'created_at'),
    )

# ✅ CORRECT: Bulk operations for performance
def update_user_statistics_bulk(db: Session, user_stats: List[dict]):
    """Update multiple user statistics efficiently."""
    try:
        db.bulk_update_mappings(UserStats, user_stats)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk update failed: {e}")
        raise

# ❌ NEVER USE: Individual updates in loops
# for stat in user_stats:
#     db.query(UserStats).filter(UserStats.id == stat['id']).update(stat)
#     db.commit()  # INEFFICIENT - One commit per update
```

### **Security Best Practices - CRITICAL IMPLEMENTATION**
```python
# ✅ CORRECT: Input sanitization for all user inputs
import bleach
from html import escape

def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    # Remove potentially dangerous HTML tags
    allowed_tags = []  # No HTML allowed in math exercises
    cleaned = bleach.clean(text, tags=allowed_tags, strip=True)
    
    # Escape any remaining HTML entities
    return escape(cleaned.strip())

# ✅ CORRECT: Rate limiting implementation
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/exercises/attempt")
@limiter.limit("10/minute")  # Max 10 attempts per minute
async def submit_attempt(request: Request, ...):
    pass

# ✅ CORRECT: SQL injection prevention with parameterized queries
def get_user_exercises(db: Session, user_id: int, exercise_type: str):
    """Get user exercises - SQL injection safe."""
    return db.query(Exercise)\
        .filter(Exercise.user_id == user_id)\
        .filter(Exercise.exercise_type == exercise_type)\
        .all()

# ❌ NEVER USE: String formatting in SQL queries
# query = f"SELECT * FROM exercises WHERE user_id = {user_id}"  # SQL INJECTION RISK
```

### **Git Workflow Standards - MANDATORY PROCESS**
```bash
# ✅ CORRECT: Branch naming convention
feature/add-geometry-exercises    # New features
bugfix/fix-badge-attribution      # Bug fixes
hotfix/security-patch            # Critical fixes
refactor/optimize-db-queries     # Code improvements

# ✅ CORRECT: Commit message format
git commit -m "feat(exercises): add geometry exercise generation

- Add perimeter and area calculations
- Implement Star Wars themed geometry problems
- Add tests for new exercise types
- Update constants.py with new exercise types

Closes #123"

# ✅ CORRECT: Pre-commit checks
#!/bin/bash
# Run before every commit
python -m pytest tests/functional/test_logic_challenge_isolated.py -v
python -m flake8 app/ server/ --max-line-length=100
python -m mypy app/ server/ --ignore-missing-imports
```

### **Code Review Standards - MANDATORY CHECKLIST**
```markdown
## Code Review Checklist - EVERY PR MUST PASS

### Functionality ✅
- [ ] All functional tests pass (6/6)
- [ ] New code follows established patterns
- [ ] Star Wars theme maintained in all UI text
- [ ] Error handling implemented properly

### Security ✅
- [ ] Input validation implemented
- [ ] Authentication properly handled
- [ ] No hardcoded credentials or secrets
- [ ] SQL injection prevention verified

### Performance ✅
- [ ] Database queries optimized
- [ ] No N+1 query problems
- [ ] Proper caching implemented where needed
- [ ] Frontend performance maintained

### Code Quality ✅
- [ ] Type hints on all functions
- [ ] Docstrings for public functions
- [ ] Error messages in French with Star Wars theme
- [ ] Logging implemented with proper context

### Testing ✅
- [ ] Unit tests for new functions
- [ ] Integration tests for API endpoints
- [ ] Edge cases covered
- [ ] Test fixtures use explicit dates
```

### **Documentation Standards - MANDATORY FORMAT**
```python
# ✅ CORRECT: Module documentation
"""
Exercise Generation Module

This module handles the generation of math exercises with Star Wars theme.
All exercises are generated in French with pedagogical explanations.

Constants:
    EXERCISE_TYPES: Available exercise types
    DIFFICULTY_LEVELS: Available difficulty levels
    
Example:
    generator = ExerciseGenerator()
    exercise = generator.generate("addition", "padawan")
"""

# ✅ CORRECT: Class documentation
class ExerciseGenerator:
    """
    Generate themed math exercises for children.
    
    This class creates math exercises with Star Wars theme, appropriate
    for children aged 6-16 with special needs. All content is in French.
    
    Attributes:
        theme_templates: Star Wars themed question templates
        difficulty_ranges: Number ranges for each difficulty level
        
    Example:
        >>> generator = ExerciseGenerator()
        >>> exercise = generator.generate("addition", "padawan")
        >>> print(exercise["question"])
        "Luke a trouvé 15 cristaux de kyber..."
    """
    
    def generate(self, exercise_type: str, difficulty: str) -> dict:
        """
        Generate a single exercise.
        
        Args:
            exercise_type: Type of exercise (addition, soustraction, etc.)
            difficulty: Difficulty level (initie, padawan, chevalier, maitre)
            
        Returns:
            Dictionary containing exercise data with Star Wars theme
            
        Raises:
            ValueError: If exercise_type or difficulty is invalid
            
        Example:
            >>> exercise = generator.generate("addition", "padawan")
            >>> exercise["correct_answer"]
            "27"
        """
        pass
```

### **Testing Standards - COMPREHENSIVE COVERAGE**
```python
# ✅ CORRECT: Test structure and naming
class TestExerciseGeneration:
    """Test exercise generation functionality."""
    
    def test_addition_padawan_generates_valid_exercise(self):
        """Test that addition exercises for padawan level are valid."""
        # Arrange
        generator = ExerciseGenerator()
        
        # Act
        exercise = generator.generate("addition", "padawan")
        
        # Assert
        assert exercise["exercise_type"] == "addition"
        assert exercise["difficulty"] == "padawan"
        assert "cristaux" in exercise["question"]  # Star Wars theme
        assert len(exercise["choices"]) == 4
        assert exercise["correct_answer"] in exercise["choices"]
    
    def test_invalid_exercise_type_raises_error(self):
        """Test that invalid exercise type raises ValueError."""
        generator = ExerciseGenerator()
        
        with pytest.raises(ValueError, match="Type d'exercice invalide"):
            generator.generate("invalid_type", "padawan")
    
    @pytest.mark.parametrize("exercise_type,difficulty", [
        ("addition", "initie"),
        ("soustraction", "padawan"),
        ("multiplication", "chevalier"),
        ("division", "maitre")
    ])
    def test_all_combinations_generate_valid_exercises(self, exercise_type, difficulty):
        """Test all exercise type and difficulty combinations."""
        generator = ExerciseGenerator()
        exercise = generator.generate(exercise_type, difficulty)
        
        assert exercise is not None
        assert exercise["exercise_type"] == exercise_type
        assert exercise["difficulty"] == difficulty

# ✅ CORRECT: Test fixtures with explicit dates
@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=1,
        username="test_padawan",
        email="test@mathakine.com",
        hashed_password="$2b$12$hash...",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        total_points=0,
        jedi_rank="youngling"
    )
```

### **Performance Standards - MANDATORY BENCHMARKS**
```python
# ✅ CORRECT: Performance monitoring
import time
from functools import wraps

def performance_monitor(func):
    """Monitor function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 1.0:  # Log slow operations
            logger.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
        
        return result
    return wrapper

@performance_monitor
def generate_exercise(exercise_type: str, difficulty: str) -> dict:
    """Generate exercise with performance monitoring."""
    # Implementation here
    pass

# ✅ CORRECT: Database query performance
def get_user_dashboard_data(db: Session, user_id: int) -> dict:
    """Get dashboard data with single optimized query."""
    # Single query with joins instead of multiple queries
    result = db.query(User)\
        .options(
            joinedload(User.attempts),
            joinedload(User.user_achievements),
            selectinload(User.progress)
        )\
        .filter(User.id == user_id)\
        .first()
    
    return {
        "user": result,
        "recent_attempts": result.attempts[-10:],
        "badges": result.user_achievements,
        "statistics": result.progress
    }
```

### **Deployment Standards - PRODUCTION READY**
```python
# ✅ CORRECT: Environment configuration
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment validation."""
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/mathakine"
    
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Performance
    REDIS_URL: str = "redis://localhost:6379"
    MAX_WORKERS: int = 4
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# ✅ CORRECT: Health check endpoint
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check for load balancer."""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Check Redis connection (if used)
        redis_client.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "4.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(503, "Service temporarily unavailable")
```

### **Error Handling Standards - COMPREHENSIVE COVERAGE**
```python
# ✅ CORRECT: Custom exception hierarchy
class MathakineException(Exception):
    """Base exception for Mathakine application."""
    pass

class ValidationError(MathakineException):
    """Raised when data validation fails."""
    pass

class AuthenticationError(MathakineException):
    """Raised when authentication fails."""
    pass

class ExerciseGenerationError(MathakineException):
    """Raised when exercise generation fails."""
    pass

# ✅ CORRECT: Global exception handler
@app.exception_handler(MathakineException)
async def mathakine_exception_handler(request: Request, exc: MathakineException):
    """Handle custom Mathakine exceptions."""
    logger.error(f"Mathakine error: {exc}")
    
    # Star Wars themed error messages
    error_messages = {
        ValidationError: "Les données ne sont pas conformes, jeune Padawan",
        AuthenticationError: "Votre identité n'a pas pu être vérifiée",
        ExerciseGenerationError: "Impossible de générer l'exercice pour le moment"
    }
    
    message = error_messages.get(type(exc), "Une erreur inattendue s'est produite")
    
    return JSONResponse(
        status_code=400,
        content={"error": message, "type": type(exc).__name__}
    )
```

---

## �🛡️ FINAL CONSTRAINTS

### **NEVER MODIFY WITHOUT TESTING**
- Enum mapping functions in `db_helpers.py`
- Exercise generation core logic in `exercise_generator.py`  
- Authentication logic in user handlers
- Database models with relationships
- CSS variable system in `variables.css`
- JavaScript authentication patterns

### **ALWAYS VALIDATE IMMEDIATELY**
- Run functional tests after any change
- Check enum mappings if touching PostgreSQL
- Verify authentication if modifying user logic
- Test exercise generation if changing generators
- Test UI on mobile and desktop
- Validate accessibility features

### **DOCUMENTATION SYNC REQUIRED**
- Update this context file for major changes
- Document new patterns in relevant code comments
- Keep API documentation in sync with endpoints
- Maintain changelog for version tracking
- Update UI components documentation
- Document performance optimizations

### **PERFORMANCE MONITORING REQUIRED**
- Monitor API response times
- Check database query performance
- Validate frontend bundle sizes
- Test on different device capabilities
- Monitor memory usage patterns
- Track user experience metrics

---

**🤖 This exhaustive context provides all necessary information for AI agents to work effectively on every aspect of Mathakine while respecting all critical constraints and maintaining system stability, performance, and user experience.**