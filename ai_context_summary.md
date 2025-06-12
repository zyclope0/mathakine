# 🤖 AI AGENT CONTEXT - MATHAKINE PROJECT

> **CRITICAL**: This file is optimized for AI agents. All rules and constraints are MANDATORY.

## 🎯 PROJECT ESSENCE

**MATHAKINE** = Educational math platform for autistic children with Star Wars theme
- **Target**: Adaptive math learning for 6-16 years old with special needs
- **Theme**: Complete Star Wars universe (children are "Math Padawans")
- **Status**: ✅ PRODUCTION READY - Fully functional
- **Architecture**: Dual backend FastAPI (pure API) + Starlette (web interface)
- **Database**: PostgreSQL (production) + SQLite (development)

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
```

### **Directory Structure - RESPECT ORGANIZATION**
```
mathakine/
├── app/                    # FastAPI application
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas  
│   ├── services/          # Business logic
│   ├── api/endpoints/     # REST endpoints
│   └── core/              # Configuration & constants
├── server/                # Starlette server modules
│   ├── handlers/          # Business logic by domain
│   ├── views.py           # HTML page management
│   └── routes.py          # Route configuration
├── templates/             # Jinja2 templates
├── static/                # CSS/JS/assets
├── tests/                 # 4-level test structure
└── docs/                  # Complete documentation
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

---

## 🎖️ BADGE SYSTEM - COMPLETE GAMIFICATION

### **Operational Badges (6 total)**
```python
# Progression badges
"first_steps"    # 10 pts - "Éveil de la Force"
"padawan_path"   # 50 pts - "Apprenti Jedi"  
"knight_trial"   # 100 pts - "Chevalier Jedi"

# Mastery badges
"addition_master" # 100 pts - "Maître de l'Harmonie"

# Special badges  
"speed_demon"    # 75 pts - "Réflexes de Jedi"
"perfect_day"    # 150 pts - "Harmonie avec la Force"
```

### **Automatic Attribution**
```python
# Integrated in ExerciseService.record_attempt()
if attempt.is_correct:
    badge_service = BadgeService(self.db)
    new_badges = badge_service.check_and_award_badges(user_id, attempt_data)
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
```

### **Patterns That Always Work**
```python
# ✅ CORRECT PATTERNS
adapt_enum_for_db("LogicChallengeType", "sequence", db)
data["hints"] = json.dumps(["hint1", "hint2"])
user = get_current_user(request); user_id = user.id
created_at=datetime.now(timezone.utc)
hints: Optional[List[str]] = Field(None)
```

---

## 🚀 DEVELOPMENT WORKFLOW

### **Before Any Code Change**
1. **Read current context** (this file)
2. **Understand constraints** (critical rules above)
3. **Check existing patterns** (follow established code)
4. **Plan validation** (which tests to run)

### **After Any Code Change**
1. **Immediate testing**: Run functional tests
2. **Validation**: Check enum mappings if modified
3. **Documentation**: Update context if major change
4. **Commit**: Only if critical tests pass

### **Debugging Process**
1. **Isolated tests**: Test specific functionality
2. **Detailed logs**: Use print() + PostgreSQL logs
3. **Immediate validation**: Test after each micro-fix
4. **Context update**: Document solution for future

---

## 🎯 CURRENT OPERATIONAL STATUS

### **100% Functional Features**
- ✅ **9 exercise types** × 4 difficulty levels = 36 combinations
- ✅ **Badge system** with automatic attribution  
- ✅ **Real-time statistics** with immediate updates
- ✅ **Authentication** with session cookies
- ✅ **Dashboard** with authentic user data
- ✅ **Premium UI** with Star Wars holographic theme

### **Test Results (Must Maintain)**
- ✅ **Functional tests**: 6/6 pass (100% success)
- ✅ **Code coverage**: 52% (improving)
- ✅ **PostgreSQL compatibility**: Perfect enum mapping
- ✅ **JSON format**: Compatible with PostgreSQL native

### **Server Configuration**
- **URL**: http://localhost:8000
- **Test credentials**: `test_user` / `test_password`
- **Database**: PostgreSQL connected (mathakine_test_gii8)
- **Mode**: Debug with auto-reload

---

## 📜 PROJECT PHILOSOPHY

### **Core Principles**
1. **Never break existing functionality** - Always test before commit
2. **Maintain Star Wars immersion** - All text should fit theme
3. **Prioritize accessibility** - Support for autistic children needs
4. **Progressive enhancement** - Basic functionality works everywhere
5. **Documentation sync** - Always update context after changes

### **Code Quality Standards**
1. **Explicit over implicit** - Clear variable names, explicit dates
2. **Fail fast** - Validate inputs early, use proper error handling
3. **Test-driven stability** - All changes must pass functional tests
4. **Consistent patterns** - Follow established code patterns
5. **Future-proof design** - Write code that can evolve

### **User Experience Focus**
1. **Educational effectiveness** - Math learning is primary goal
2. **Motivational design** - Gamification encourages progress
3. **Inclusive accessibility** - Works for different ability levels
4. **Immediate feedback** - Real-time validation and encouragement
5. **Parent transparency** - Clear progress tracking for families

---

## 🔍 REFERENCE FILES - QUICK ACCESS

### **Critical Configuration**
- `app/core/constants.py` - Exercise types, difficulty levels, limits
- `app/core/messages.py` - AI prompts, explanations, UI text
- `app/core/config.py` - Database, security, environment settings

### **Business Logic**  
- `app/services/exercise_service.py` - Exercise CRUD and attempt recording
- `app/services/badge_service.py` - Badge logic and automatic attribution
- `server/exercise_generator.py` - Exercise generation (9 types)

### **Database Mappings**
- `app/utils/db_helpers.py` - Enum mapping functions (PostgreSQL/SQLite)
- `app/models/` - SQLAlchemy models with relationships
- `app/schemas/` - Pydantic schemas for validation

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
```

---

## 🎯 SUCCESS METRICS - MAINTAIN THESE

### **Technical Metrics**
- **Functional tests**: 6/6 must pass always
- **Code coverage**: Target 60%+ (currently 52%)
- **Server startup**: < 5 seconds  
- **API response**: < 200ms average

### **User Experience Metrics**  
- **Exercise generation**: < 1 second
- **Badge attribution**: Immediate after exercise completion
- **Dashboard update**: Real-time statistics display
- **Authentication**: Seamless login/logout flow

### **Quality Indicators**
- **Zero enum mapping errors** in PostgreSQL
- **Zero Pydantic validation errors** in tests
- **Zero authentication failures** in handlers
- **100% Star Wars theme consistency** in UI text

---

## 🛡️ FINAL CONSTRAINTS

### **NEVER MODIFY WITHOUT TESTING**
- Enum mapping functions in `db_helpers.py`
- Exercise generation core logic in `exercise_generator.py`  
- Authentication logic in user handlers
- Database models with relationships

### **ALWAYS VALIDATE IMMEDIATELY**
- Run functional tests after any change
- Check enum mappings if touching PostgreSQL
- Verify authentication if modifying user logic
- Test exercise generation if changing generators

### **DOCUMENTATION SYNC REQUIRED**
- Update this context file for major changes
- Document new patterns in relevant code comments
- Keep API documentation in sync with endpoints
- Maintain changelog for version tracking

---

**🤖 This context provides all necessary information for AI agents to work effectively on Mathakine while respecting all critical constraints and maintaining system stability.**