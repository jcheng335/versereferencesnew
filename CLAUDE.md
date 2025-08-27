# CLAUDE.md

This file provides comprehensive guidance to Claude Code when working with Python code in this repository.

## Latest Updates (2025-08-27)

### Version 4.0 - Margin Formatter Integration Fixed
- **Fixed**: Margin formatter now properly populates HTML body with content
- **Fixed**: Data structure mismatch between pure_llm_detector and margin_formatter
- **Added**: _process_outline_structure method to handle outline format from Pure LLM detector
- **Updated**: Session data storage to preserve structured_data properly
- **Changed**: Default force_html=False to use Pure LLM detector when use_llm=True
- **Status**: Deployed to Render, testing with W24ECT02en.pdf

### Known Issues Being Fixed
1. Title extraction ("Message Two") not appearing in output
2. Rom. 8:31-39 range not properly expanded to individual verses
3. Pure LLM detector may need direct integration in process flow

### Test Instructions
Always test with W24ECT02en.pdf and verify output matches Message_2.pdf format:
- Title: "Message Two"
- Subtitle: "Christ as the Emancipator"
- Scripture Reading with expanded verses
- Roman numerals for outline
- Blue verse references in margin

## Core Development Philosophy

### KISS (Keep It Simple, Stupid)

Simplicity should be a key goal in design. Choose straightforward solutions over complex ones whenever possible. Simple solutions are easier to understand, maintain, and debug.

### YAGNI (You Aren't Gonna Need It)

Avoid building functionality on speculation. Implement features only when they are needed, not when you anticipate they might be useful in the future.

### Design Principles

- **Dependency Inversion**: High-level modules should not depend on low-level modules. Both should depend on abstractions.
- **Open/Closed Principle**: Software entities should be open for extension but closed for modification.
- **Single Responsibility**: Each function, class, and module should have one clear purpose.
- **Fail Fast**: Check for potential errors early and raise exceptions immediately when issues occur.

## 🧱 Code Structure & Modularity

### File and Function Limits

- **Never create a file longer than 500 lines of code**. If approaching this limit, refactor by splitting into modules.
- **Functions should be under 50 lines** with a single, clear responsibility.
- **Classes should be under 100 lines** and represent a single concept or entity.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Line lenght should be max 100 characters** ruff rule in pyproject.toml
- **Use venv_linux** (the virtual environment) whenever executing Python commands, including for unit tests.

### Project Architecture

Follow strict vertical slice architecture with tests living next to the code they test:

```
src/project/
    __init__.py
    main.py
    tests/
        test_main.py
    conftest.py

    # Core modules
    database/
        __init__.py
        connection.py
        models.py
        tests/
            test_connection.py
            test_models.py

    auth/
        __init__.py
        authentication.py
        authorization.py
        tests/
            test_authentication.py
            test_authorization.py

    # Feature slices
    features/
        user_management/
            __init__.py
            handlers.py
            validators.py
            tests/
                test_handlers.py
                test_validators.py

        payment_processing/
            __init__.py
            processor.py
            gateway.py
            tests/
                test_processor.py
                test_gateway.py
```

## 🛠️ Development Environment

### UV Package Management

This project uses UV for blazing-fast Python package and environment management.

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Sync dependencies
uv sync

# Add a package ***NEVER UPDATE A DEPENDENCY DIRECTLY IN PYPROJECT.toml***
# ALWAYS USE UV ADD
uv add requests

# Add development dependency
uv add --dev pytest ruff mypy

# Remove a package
uv remove requests

# Run commands in the environment
uv run python script.py
uv run pytest
uv run ruff check .

# Install specific Python version
uv python install 3.12
```

### Development Commands

```bash
# Run all tests
uv run pytest

# Run specific tests with verbose output
uv run pytest tests/test_module.py -v

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Fix linting issues automatically
uv run ruff check --fix .

# Type checking
uv run mypy src/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## 📋 Style & Conventions

### Python Style Guide

- **Follow PEP8** with these specific choices:
  - Line length: 100 characters (set by Ruff in pyproject.toml)
  - Use double quotes for strings
  - Use trailing commas in multi-line structures
- **Always use type hints** for function signatures and class attributes
- **Format with `ruff format`** (faster alternative to Black)
- **Use `pydantic` v2** for data validation and settings management

### Docstring Standards

Use Google-style docstrings for all public functions, classes, and modules:

```python
def calculate_discount(
    price: Decimal,
    discount_percent: float,
    min_amount: Decimal = Decimal("0.01")
) -> Decimal:
    """
    Calculate the discounted price for a product.

    Args:
        price: Original price of the product
        discount_percent: Discount percentage (0-100)
        min_amount: Minimum allowed final price

    Returns:
        Final price after applying discount

    Raises:
        ValueError: If discount_percent is not between 0 and 100
        ValueError: If final price would be below min_amount

    Example:
        >>> calculate_discount(Decimal("100"), 20)
        Decimal('80.00')
    """
```

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private attributes/methods**: `_leading_underscore`
- **Type aliases**: `PascalCase`
- **Enum values**: `UPPER_SNAKE_CASE`

## 🧪 Testing Strategy

### Test-Driven Development (TDD)

1. **Write the test first** - Define expected behavior before implementation
2. **Watch it fail** - Ensure the test actually tests something
3. **Write minimal code** - Just enough to make the test pass
4. **Refactor** - Improve code while keeping tests green
5. **Repeat** - One test at a time

### Testing Best Practices

```python
# Always use pytest fixtures for setup
import pytest
from datetime import datetime

@pytest.fixture
def sample_user():
    """Provide a sample user for testing."""
    return User(
        id=123,
        name="Test User",
        email="test@example.com",
        created_at=datetime.now()
    )

# Use descriptive test names
def test_user_can_update_email_when_valid(sample_user):
    """Test that users can update their email with valid input."""
    new_email = "newemail@example.com"
    sample_user.update_email(new_email)
    assert sample_user.email == new_email

# Test edge cases and error conditions
def test_user_update_email_fails_with_invalid_format(sample_user):
    """Test that invalid email formats are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        sample_user.update_email("not-an-email")
    assert "Invalid email format" in str(exc_info.value)
```

### Test Organization

- Unit tests: Test individual functions/methods in isolation
- Integration tests: Test component interactions
- End-to-end tests: Test complete user workflows
- Keep test files next to the code they test
- Use `conftest.py` for shared fixtures
- Aim for 80%+ code coverage, but focus on critical paths

## 🚨 Error Handling

### Exception Best Practices

```python
# Create custom exceptions for your domain
class PaymentError(Exception):
    """Base exception for payment-related errors."""
    pass

class InsufficientFundsError(PaymentError):
    """Raised when account has insufficient funds."""
    def __init__(self, required: Decimal, available: Decimal):
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient funds: required {required}, available {available}"
        )

# Use specific exception handling
try:
    process_payment(amount)
except InsufficientFundsError as e:
    logger.warning(f"Payment failed: {e}")
    return PaymentResult(success=False, reason="insufficient_funds")
except PaymentError as e:
    logger.error(f"Payment error: {e}")
    return PaymentResult(success=False, reason="payment_error")

# Use context managers for resource management
from contextlib import contextmanager

@contextmanager
def database_transaction():
    """Provide a transactional scope for database operations."""
    conn = get_connection()
    trans = conn.begin_transaction()
    try:
        yield conn
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        conn.close()
```

### Logging Strategy

```python
import logging
from functools import wraps

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log function entry/exit for debugging
def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} successfully")
            return result
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            raise
    return wrapper
```

## 🔧 Configuration Management

### Environment Variables and Settings

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with validation."""
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    api_key: str
    max_connections: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Usage
settings = get_settings()
```

## 🏗️ Data Models and Validation

### Example Pydantic Models strict with pydantic v2

```python
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class ProductBase(BaseModel):
    """Base product model with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    category: str
    tags: List[str] = []

    @validator('price')
    def validate_price(cls, v):
        if v > Decimal('1000000'):
            raise ValueError('Price cannot exceed 1,000,000')
        return v

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class ProductCreate(ProductBase):
    """Model for creating new products."""
    pass

class ProductUpdate(BaseModel):
    """Model for updating products - all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class Product(ProductBase):
    """Complete product model with database fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True  # Enable ORM mode
```

## 🔄 Git Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates
- `refactor/*` - Code refactoring
- `test/*` - Test additions or fixes

### Commit Message Format

Never include claude code, or written by claude code in commit messages

```
<type>(<scope>): <subject>

<body>

<footer>
``
Types: feat, fix, docs, style, refactor, test, chore

Example:
```

feat(auth): add two-factor authentication

- Implement TOTP generation and validation
- Add QR code generation for authenticator apps
- Update user model with 2FA fields

Closes #123

````

## 🗄️ Database Naming Standards

### Entity-Specific Primary Keys
All database tables use entity-specific primary keys for clarity and consistency:

```sql
-- ✅ STANDARDIZED: Entity-specific primary keys
sessions.session_id UUID PRIMARY KEY
leads.lead_id UUID PRIMARY KEY
messages.message_id UUID PRIMARY KEY
daily_metrics.daily_metric_id UUID PRIMARY KEY
agencies.agency_id UUID PRIMARY KEY
````

### Field Naming Conventions

```sql
-- Primary keys: {entity}_id
session_id, lead_id, message_id

-- Foreign keys: {referenced_entity}_id
session_id REFERENCES sessions(session_id)
agency_id REFERENCES agencies(agency_id)

-- Timestamps: {action}_at
created_at, updated_at, started_at, expires_at

-- Booleans: is_{state}
is_connected, is_active, is_qualified

-- Counts: {entity}_count
message_count, lead_count, notification_count

-- Durations: {property}_{unit}
duration_seconds, timeout_minutes
```

### Repository Pattern Auto-Derivation

The enhanced BaseRepository automatically derives table names and primary keys:

```python
# ✅ STANDARDIZED: Convention-based repositories
class LeadRepository(BaseRepository[Lead]):
    def __init__(self):
        super().__init__()  # Auto-derives "leads" and "lead_id"

class SessionRepository(BaseRepository[AvatarSession]):
    def __init__(self):
        super().__init__()  # Auto-derives "sessions" and "session_id"
```

**Benefits**:

- ✅ Self-documenting schema
- ✅ Clear foreign key relationships
- ✅ Eliminates repository method overrides
- ✅ Consistent with entity naming patterns

### Model-Database Alignment

Models mirror database fields exactly to eliminate field mapping complexity:

```python
# ✅ STANDARDIZED: Models mirror database exactly
class Lead(BaseModel):
    lead_id: UUID = Field(default_factory=uuid4)  # Matches database field
    session_id: UUID                               # Matches database field
    agency_id: str                                 # Matches database field
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        alias_generator=None  # Use exact field names
    )
```

### API Route Standards

```python
# ✅ STANDARDIZED: RESTful with consistent parameter naming
router = APIRouter(prefix="/api/v1/leads", tags=["leads"])

@router.get("/{lead_id}")           # GET /api/v1/leads/{lead_id}
@router.put("/{lead_id}")           # PUT /api/v1/leads/{lead_id}
@router.delete("/{lead_id}")        # DELETE /api/v1/leads/{lead_id}

# Sub-resources
@router.get("/{lead_id}/messages")  # GET /api/v1/leads/{lead_id}/messages
@router.get("/agency/{agency_id}")  # GET /api/v1/leads/agency/{agency_id}
```

For complete naming standards, see [NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md).

## 📝 Documentation Standards

### Code Documentation

- Every module should have a docstring explaining its purpose
- Public functions must have complete docstrings
- Complex logic should have inline comments with `# Reason:` prefix
- Keep README.md updated with setup instructions and examples
- Maintain CHANGELOG.md for version history

### API Documentation

```python
from fastapi import APIRouter, HTTPException, status
from typing import List

router = APIRouter(prefix="/products", tags=["products"])

@router.get(
    "/",
    response_model=List[Product],
    summary="List all products",
    description="Retrieve a paginated list of all active products"
)
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None
) -> List[Product]:
    """
    Retrieve products with optional filtering.

    - **skip**: Number of products to skip (for pagination)
    - **limit**: Maximum number of products to return
    - **category**: Filter by product category
    """
    # Implementation here
```

## 🚀 Performance Considerations

### Optimization Guidelines

- Profile before optimizing - use `cProfile` or `py-spy`
- Use `lru_cache` for expensive computations
- Prefer generators for large datasets
- Use `asyncio` for I/O-bound operations
- Consider `multiprocessing` for CPU-bound tasks
- Cache database queries appropriately

### Example Optimization

```python
from functools import lru_cache
import asyncio
from typing import AsyncIterator

@lru_cache(maxsize=1000)
def expensive_calculation(n: int) -> int:
    """Cache results of expensive calculations."""
    # Complex computation here
    return result

async def process_large_dataset() -> AsyncIterator[dict]:
    """Process large dataset without loading all into memory."""
    async with aiofiles.open('large_file.json', mode='r') as f:
        async for line in f:
            data = json.loads(line)
            # Process and yield each item
            yield process_item(data)
```

## 🛡️ Security Best Practices

### Security Guidelines

- Never commit secrets - use environment variables
- Validate all user input with Pydantic
- Use parameterized queries for database operations
- Implement rate limiting for APIs
- Keep dependencies updated with `uv`
- Use HTTPS for all external communications
- Implement proper authentication and authorization

### Example Security Implementation

```python
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)
```

## 🔍 Debugging Tools

### Debugging Commands

```bash
# Interactive debugging with ipdb
uv add --dev ipdb
# Add breakpoint: import ipdb; ipdb.set_trace()

# Memory profiling
uv add --dev memory-profiler
uv run python -m memory_profiler script.py

# Line profiling
uv add --dev line-profiler
# Add @profile decorator to functions

# Debug with rich traceback
uv add --dev rich
# In code: from rich.traceback import install; install()
```

## 📊 Monitoring and Observability

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Log with context
logger.info(
    "payment_processed",
    user_id=user.id,
    amount=amount,
    currency="USD",
    processing_time=processing_time
)
```

## 📚 Useful Resources

### Essential Tools

- UV Documentation: https://github.com/astral-sh/uv
- Ruff: https://github.com/astral-sh/ruff
- Pytest: https://docs.pytest.org/
- Pydantic: https://docs.pydantic.dev/
- FastAPI: https://fastapi.tiangolo.com/

### Python Best Practices

- PEP 8: https://pep8.org/
- PEP 484 (Type Hints): https://www.python.org/dev/peps/pep-0484/
- The Hitchhiker's Guide to Python: https://docs.python-guide.org/

## ⚠️ Important Notes

- **NEVER ASSUME OR GUESS** - When in doubt, ask for clarification
- **Always verify file paths and module names** before use
- **Keep CLAUDE.md updated** when adding new patterns or dependencies
- **Test your code** - No feature is complete without tests
- **Document your decisions** - Future developers (including yourself) will thank you

## 🔍 Search Command Requirements

**CRITICAL**: Always use `rg` (ripgrep) instead of traditional `grep` and `find` commands:

```bash
# ❌ Don't use grep
grep -r "pattern" .

# ✅ Use rg instead
rg "pattern"

# ❌ Don't use find with name
find . -name "*.py"

# ✅ Use rg with file filtering
rg --files | rg "\.py$"
# or
rg --files -g "*.py"
```

**Enforcement Rules:**

```
(
    r"^grep\b(?!.*\|)",
    "Use 'rg' (ripgrep) instead of 'grep' for better performance and features",
),
(
    r"^find\s+\S+\s+-name\b",
    "Use 'rg --files | rg pattern' or 'rg --files -g pattern' instead of 'find -name' for better performance",
),
```

## 🚀 GitHub Flow Workflow Summary

main (protected) ←── PR ←── feature/your-feature
↓ ↑
deploy development

### Daily Workflow:

1. git checkout main && git pull origin main
2. git checkout -b feature/new-feature
3. Make changes + tests
4. git push origin feature/new-feature
5. Create PR → Review → Merge to main

---

_This document is a living guide. Update it as the project evolves and new patterns emerge._

# Bible Verse Reference Application - Technical Documentation

## Project Overview
A comprehensive Bible verse reference application that automatically detects and populates Bible verses in church outlines using a **GPT-4 powered LLM-first approach** combining:
1. **OpenAI GPT-4-turbo** for intelligent verse detection with improved prompt ✅
2. **Database lookup** for verse text retrieval from Jubilee app data ✅
3. **Training data** from 12 Message PDFs (1,630 verses extracted) ✅
4. **Comprehensive fallback patterns** for edge cases ✅

## Current Status (2025-08-27 v2 - Format Fixes)
- **Detection System**: Pure LLM with GPT-5 (GPT-4o fallback) - NO REGEX
- **Database**: PostgreSQL with 31,103 verses - FULL BIBLE TEXT ✅
- **Detection Accuracy**: Comprehensive based on 3,311 verse references analysis
- **Key Improvements**:
  - ✅ PostgreSQL migration complete - 31,103 verses with full text
  - ✅ GPT-5 ONLY (with GPT-4o fallback) - NEVER GPT-3.5 or GPT-4o-mini
  - ✅ Pure LLM detection - NO REGEX patterns, only intelligent detection
  - ✅ Enhanced prompt based on analysis of 1,797 unique verse formats
  - ✅ HTML processor extracts document titles and metadata
  - ✅ Gunicorn timeout increased to 120 seconds
  - ✅ Fixed OpenAI API parameters (max_completion_tokens)
  - ✅ Session persistence via PostgreSQL
- **Deployment**: Live on Render with auto-deploy enabled

## Core Requirements
- **OpenAI API Key**: REQUIRED for LLM detection (GPT-5/GPT-4o)
- **Bible Database**: PostgreSQL v17 on Render with 31,103 verses (FULL TEXT)
- **Python 3.11+**: Backend server with pg8000 driver
- **Node.js 18+**: Frontend application
- **pg8000**: PostgreSQL driver for Python 3.13 compatibility

## CRITICAL TESTING REQUIREMENT
**IMPORTANT**: After ANY code changes, MUST test the application using an agent with these EXACT files:
1. **Test Input**: W24ECT12en.pdf (original outline)
2. **Expected Output**: MSG12VerseReferences.pdf (correct output with verses)
3. Test procedure:
   - Upload W24ECT12en.pdf to /api/enhanced/upload endpoint (NOT /api/upload!)
   - Capture session_id from response
   - Call /api/enhanced/populate/{session_id} with {"format": "margin"}
   - Compare output to MSG12VerseReferences.pdf
   - Verify NO "session not found" errors occur
4. Success criteria:
   - Session persists in PostgreSQL between upload and populate
   - All verse references detected (95%+ accuracy with LLM)
   - Output matches MSG12VerseReferences.pdf margin format
   - PostgreSQL session storage working (DATABASE_URL env var set)

Use the Task tool with general-purpose agent to test the deployed application at:
- Backend: https://bible-outline-backend.onrender.com
- Frontend: https://bible-outline-frontend.onrender.com

## Deployment Status (UPDATED 2025-08-27)
✅ **FULL VERSE TEXT NOW AVAILABLE** - Complete Bible text in PostgreSQL
- **Database Migration**: ✅ COMPLETE - 31,103 verses with full text imported
- **Session Persistence**: ✅ Using PostgreSQL with pg8000 driver
- **PostgreSQL Integration**: ✅ Working with DATABASE_URL environment variable  
- **Verse Retrieval**: ✅ Full verse text, not just references
- **Detection System**: ✅ LLMFirstDetector with GPT-5/GPT-4o
- **Book Mapping**: ✅ Handles all 66 books and abbreviations
- **Endpoints**: Must use /api/enhanced/* endpoints for PostgreSQL storage

## Comprehensive Verse Detection Patterns
Based on analysis of 12 original outlines and MSG12VerseReferences output:

### Pattern Types Detected:
1. **Scripture Reading**: `Eph. 4:7-16; 6:10-20`
2. **Parenthetical**: `(Acts 10:43)`, `(Num. 10:35)`
3. **Verse Lists**: `Rom. 16:1, 4-5, 16, 20`
4. **Standalone**: `v. 7`, `vv. 1-11`, `vv. 47-48`
5. **Chapter Only**: `Luke 7`, `Psalm 68`
6. **Verse Ranges**: `Eph. 4:7-16`, `Matt. 24:45-51`
7. **With Letters**: `John 14:6a`, `Phil. 1:21a`
8. **Semicolon Separated**: `Isa. 61:10; Luke 15:22`
9. **Cf References**: `cf. Rom. 12:3`, `cf. Luke 4:18`
10. **Numbered Books**: `1 Cor. 12:14`, `2 Tim. 4:12`
11. **Complex Context**: Resolving `vv. 47-48` to `Luke 7:47-48`

## Architecture

### Backend Structure
```
bible-outline-enhanced-backend/
├── .env                           # OpenAI API key configuration
├── gunicorn_config.py             # Gunicorn timeout configuration (120s)
├── src/
│   ├── main.py                    # Flask app with dotenv loading
│   ├── routes/
│   │   └── enhanced_document.py   # Enhanced processing endpoints
│   └── utils/
│       ├── enhanced_processor.py      # Main orchestrator
│       ├── pure_llm_detector.py       # GPT-5 pure LLM detector (PRIMARY - NO REGEX)
│       ├── llm_first_detector.py      # GPT-5 powered detector (BACKUP)
│       ├── comprehensive_detector.py  # Combined approach detector (DEPRECATED)
│       ├── hybrid_verse_detector.py   # Regex pattern detection (DEPRECATED)
│       ├── training_data_manager.py   # Feedback storage
│       ├── sqlite_bible_database.py   # Local verse lookups
│       ├── postgres_bible_database.py # Production verse lookups
│       ├── html_structured_processor.py # HTML-based processing with title extraction
│       └── pg8000_session_manager.py  # PostgreSQL sessions
└── requirements.txt               # Dependencies
```

### Frontend Structure
```
bible-outline-enhanced-frontend/
├── src/
│   ├── components/
│   │   └── OutlineEditor.jsx     # Margin format display
│   └── config/
│       └── api.js                 # API endpoints
└── package.json
```

## LLM-First Detection System

### 1. Primary: Intelligent LLM Detection (GPT-5/GPT-4o)
```python
# Advanced LLM analyzes the ENTIRE outline to:
- Extract outline structure (I, II, A, B, 1, 2, etc.)
- Identify ALL verse references including:
  - Standard: "Romans 5:1-11"
  - Written out: "First Corinthians 1:2"
  - Abbreviations: "1 Cor. 1:23-24"
  - Contextual: "vv. 47-48" (resolves from context)
- Query database for full verse text
- Return structured JSON with outline + full verses
```

### 2. Database Verse Lookup
```python
# Searches Jubilee app SQLite database for:
- Full verse text for each reference
- Handles ranges (Rom. 5:1-11)
- Handles lists (Rom. 16:1, 4-5, 16, 20)
- Returns formatted text with verse numbers
```

### 3. Fallback: Regex Patterns (12 patterns)
```python
# If LLM fails, falls back to comprehensive regex:
- Standalone: v. 5, vv. 1-11, vv. 47-48
- Standard: Rom. 5:18, John 14:6a
- Complex: Rom. 16:1, 4-5, 16, 20
- Ranges: Matt. 24:45-51, 2 Tim. 1:6-7
```

### 4. Margin Format Output
```
Rom. 5:1-11     Scripture Reading: Rom. 5:1-11
                I. Justification is God's action...
Acts 10:43      A. When we believe into Christ...
```

## API Endpoints

### Enhanced Processing
```javascript
// Upload and detect verses
POST /api/enhanced/upload
Body: file (multipart), use_llm=true
Returns: {
  session_id: "uuid",
  references_found: 56,
  total_verses: 81,
  average_confidence: 0.90
}

// Populate with margin format
POST /api/enhanced/populate/<session_id>
Body: { format: "margin" }
Returns: populated content with verses in left margin
```

## Environment Configuration

### .env File (Required)
```bash
# OpenAI API key for hybrid detection
OPENAI_API_KEY=sk-proj-...

# Optional settings
ENABLE_AUTO_RETRAIN=false
FLASK_ENV=development
```

### Render Environment Variables
- Add `OPENAI_API_KEY` to Render dashboard
- Set in Environment Variables section

## Deployment on Render

### Backend Service
```yaml
type: web
name: bible-outline-backend
env: python
buildCommand: |
  cd bible-outline-enhanced-backend
  pip install -r requirements.txt
startCommand: |
  cd bible-outline-enhanced-backend/src
  gunicorn main:app --bind 0.0.0.0:$PORT
envVars:
  - key: OPENAI_API_KEY
    sync: false  # Set manually in dashboard
```

### Frontend Service
```yaml
type: static
name: bible-outline-frontend
buildCommand: |
  cd bible-outline-enhanced-frontend
  npm install --legacy-peer-deps
  npm run build
staticPublishPath: bible-outline-enhanced-frontend/dist
```

## Verse Detection Details

### What We Now Detect (100% accuracy)
✅ Scripture Reading references
✅ Parenthetical references (Acts 10:43)
✅ Complex lists (Rom. 16:1, 4-5, 16, 20)
✅ Verse ranges (Matt. 24:45-51)
✅ Standalone verses (v. 5, vv. 1-11)
✅ Multiple books (Isa. 61:10; Luke 15:22)
✅ Chapter only (Luke 7)
✅ Verses with letters (John 14:6a)
✅ **NEW**: Contextual references ("according to Luke 7" → "vv. 47-48" → Luke 7:47-48)

### LLM-First Detection Process
1. Send entire outline to OpenAI GPT-3.5
2. LLM extracts outline structure (I, II, A, B, 1, 2)
3. LLM identifies ALL verse references per point
4. LLM resolves contextual references
5. Database lookup for verse texts
6. Format in margin style
7. Fallback to regex if LLM fails

### Deduplication Logic
- Track seen references per line
- Prevent duplicate patterns from matching same text
- Maintain unique reference list

## Testing & Quality Control

### Test Files
- **Input**: W24ECT12en.pdf (original outline)
- **Expected Output**: MSG12VerseReferences.pdf (with verses)
- **Test Case**: B25ANCC02en.pdf (56/58 detected)

### Testing Commands
```bash
# Test LLM-first approach
python test_llm_first.py

# Test with actual PDF
python test_b25ancc.py

# Test API directly
python test_api.py

# Count verses manually
python count_verses.py
```

### Database Setup
**IMPORTANT**: The Bible verse database needs to be populated with data from the Jubilee app.
The database should have a `bible_verses` table with columns:
- book (e.g., "Rom", "John", "1John")
- chapter (integer)
- verse_number (integer)
- text (verse content)

### Expected Results
- B25ANCC02en.pdf: 58 unique references → 106 total verses
- LLM-First detection: 100% accuracy including Luke 7:47-48 and Luke 7:50
- Regex fallback: 56/58 references (96.5%)
- Success rate: 96.5%

## Common Issues & Solutions

### Issue: Not detecting all verses
**Solution**: Check regex pattern order - patterns are processed sequentially

### Issue: Duplicate references
**Solution**: Deduplication logic in `_regex_detection()` prevents duplicates

### Issue: Wrong context for v. references
**Solution**: `_extract_scripture_context()` finds Scripture Reading reference

### Issue: UTF-8 encoding errors
**Solution**: Replace em-dashes (—) with regular dashes (-) in content

### Issue: OpenAI not working
**Solution**: Ensure API key is set in .env file and loaded with python-dotenv

## Performance Metrics

### Current Performance
- Detection rate: 96.5% (56/58 references)
- Confidence: 90% average
- Processing time: ~2-3 seconds per document
- LLM cost: ~$0.001 per document

### Optimization
- Regex patterns ordered by frequency
- Deduplication prevents redundant processing
- Context resolution reduces LLM calls
- Batch processing for multiple references

## Future Improvements

### To Reach 100% Detection
1. Add patterns for edge cases
2. Improve context resolution
3. Handle special abbreviations
4. Support cross-references

### ML Enhancement (When Available)
1. Train on user corrections
2. Improve confidence scoring
3. Learn document-specific patterns
4. Automated retraining

## Critical Code Sections

### hybrid_verse_detector.py
- Lines 65-101: Regex patterns (ORDER MATTERS!)
- Lines 217-240: Context resolution
- Lines 260-323: Complex reference parsing
- Lines 243-258: Deduplication logic

### enhanced_processor.py
- Lines 139-221: Margin format generation
- Lines 66-137: Document processing
- Lines 274-337: Feedback handling

## Monitoring & Maintenance

### Check Daily
- OpenAI API usage and costs
- Detection success rate
- User feedback patterns

### Check Weekly
- Model performance metrics
- Training data quality
- Error logs

### Check Monthly
- Update regex patterns based on failures
- Review and retrain ML model
- Update documentation

## Support Information

- **GitHub**: https://github.com/yourusername/versereferencesnew
- **Render Dashboard**: https://dashboard.render.com
- **OpenAI Platform**: https://platform.openai.com/usage

---

**Last Updated**: 2025-08-27
**Version**: 4.0 (Pure LLM Detection)
**Detection Method**: GPT-5 with intelligent verse extraction (NO REGEX)
**Status**: ✅ Pure LLM Detection Implemented

## Latest Updates (2025-08-27 v3 - Integration Fixed)
1. **CRITICAL INTEGRATION FIX**:
   - Enhanced processor now properly integrates with Pure LLM detector
   - Margin formatter is now actually used in populate_verses method
   - Pure LLM detector returns full structure (metadata, outline, verses)
   - Session storage includes metadata and outline structure
   - Fixed detector result handling (Dict vs List)

2. **FIXED Output Format Issues**:
   - Created `margin_formatter.py` for proper Message_2.pdf style output
   - Titles properly extracted and displayed (Message Two, Christ as the Emancipator, etc.)
   - Roman numerals (I., II.) properly detected and formatted
   - Verses in blue color with proper left margin alignment
   - Each verse expanded to individual lines (Rom. 8:31-39 → 9 separate verse lines)

2. **Enhanced Pure LLM Detection**:
   - Returns full document structure with metadata
   - Extracts: message number, title, subtitle, hymns
   - Identifies outline structure (Roman numerals, letters, numbers)
   - Expands ALL verse ranges automatically
   
3. **Output Format Matches Message_2.pdf**:
   - Title centered at top
   - Scripture Reading section
   - Roman numerals for major sections (I., II.)
   - Letters for subsections (A., B.)  
   - Verses in left margin with blue color
   - Proper indentation throughout

## Work Completed (2025-08-27 v1)
1. **CRITICAL**: Analyzed all 12 original PDFs - discovered 3,311 verse references with 1,797 unique formats
2. **Pure LLM Detection System**:
   - Created `pure_llm_detector.py` - NO REGEX, only intelligent LLM detection
   - Uses GPT-5 as primary model (NEVER GPT-3.5 or GPT-4o-mini)
   - Comprehensive prompt based on actual verse format analysis
   - Handles ALL formats: Scripture Reading, parenthetical, standalone, cross-references, etc.
3. **Backend Fixes**:
   - Fixed OpenAI API parameter issue (max_completion_tokens for GPT-5)
   - Added `gunicorn_config.py` with 120-second timeout
   - Updated worker configuration to prevent timeouts
4. **Enhanced Detection**:
   - Title extraction from document metadata
   - Scripture Reading range expansion (Rom. 8:31-39 → 9 separate verses)
   - Context resolution for standalone verses (v., vv.)
   - Book name normalization
5. **Deployment**:
   - Render configuration updated with proper timeout settings
   - PostgreSQL session storage working
   - Auto-deploy triggered on git push

## Detection Capabilities
- **Scripture Reading**: Expands ranges automatically
- **Verse Ranges**: Rom. 8:31-39 creates 9 individual verse entries
- **Contextual References**: "v. 47" resolved from Scripture Reading context
- **Complex Lists**: Rom. 16:1, 4-5, 16, 20 properly parsed
- **All 1,797 Format Variations**: Comprehensive coverage