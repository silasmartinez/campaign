# Technical Debt Tracking

This file tracks significant technical debt that should be prioritized against new feature work.

## Critical Debt (Blocks Production)
*None currently identified*

## High Priority Debt (Impacts Maintainability)

### 1. Missing Setup Wizard 🧙‍♂️
- **Issue**: No initial configuration flow for new users
- **Impact**: Poor onboarding experience, manual config required
- **Effort**: Medium (2-3 days)
- **Dependencies**: None
- **Priority**: High - affects user adoption

### 2. No Docker Support
- **Issue**: Only virtual environment installation, no containerized option
- **Impact**: Deployment complexity, environment inconsistencies
- **Effort**: Medium (1-2 days)
- **Dependencies**: Dockerfile, docker-compose, make targets
- **Priority**: High - affects deployment and scaling

### 3. Single Campaign Limitation
- **Issue**: No isolation between different campaigns
- **Impact**: Users can't manage multiple campaigns cleanly
- **Effort**: Large (1-2 weeks)
- **Dependencies**: Database schema changes, CLI updates
- **Priority**: Medium - feature limitation but not blocking

## Medium Priority Debt (Code Quality)

### 4. Limited Test Coverage
- **Issue**: Only basic smoke tests, no comprehensive unit/integration tests
- **Impact**: Risk of regressions, harder to refactor safely
- **Effort**: Large (ongoing)
- **Dependencies**: Test framework setup, mocking patterns
- **Priority**: Medium - important for long-term maintenance

### 5. Hardcoded Model Fallbacks
- **Issue**: Task-specific model routing has hardcoded fallback logic
- **Impact**: Brittle when models are unavailable, hard to configure
- **Effort**: Small (1 day)
- **Dependencies**: Configuration system updates
- **Priority**: Low - working but not elegant

## Low Priority Debt (Nice to Have)

### 6. CLI Error Handling Inconsistency
- **Issue**: Some commands have better error messages than others
- **Impact**: Inconsistent user experience
- **Effort**: Small (1-2 days)
- **Dependencies**: None
- **Priority**: Low - UX improvement

### 7. Configuration Validation
- **Issue**: YAML configs aren't validated on load
- **Impact**: Runtime errors from bad configs
- **Effort**: Small (1 day)  
- **Dependencies**: Pydantic schema definitions
- **Priority**: Low - rare issue

## Resolved Debt ✅

### ~~LLM Integration Missing~~ ✅
- **Resolved**: 2025-06-14 - Implemented Ollama service with task-specific routing

### ~~Async/Await Issues~~ ✅  
- **Resolved**: 2025-06-14 - Fixed content synthesizer async handling

### ~~Import Statement Inconsistencies~~ ✅
- **Resolved**: 2025-06-14 - Standardized to modern Python syntax

---

## Debt Assessment Guidelines

**Critical**: Blocks production deployment or causes data loss
**High**: Significantly impacts user experience or development velocity  
**Medium**: Affects code quality or maintainability
**Low**: Minor improvements or polish

**Effort Scale**: Small (< 1 day), Medium (1-3 days), Large (> 1 week)

---

*Last updated: 2025-06-14*