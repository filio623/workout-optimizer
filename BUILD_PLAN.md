# Workout Optimizer - Step-by-Step Build Plan

## Overview
This plan outlines the development steps for building a minimal, robust, and extensible workout optimizer backend using FastAPI, Hevy API integration, and OpenAI LLM capabilities.

## Phase 1: Core Module Setup

### 1. Configuration Management
- [x] Create `app/config.py`
  - [x] Load environment variables from `.env`
  - [x] Validate required API keys (HEVY_API_KEY, OPENAI_API_KEY)
  - [x] Add configuration classes/settings
  - [x] Add error handling for missing config

### 2. Data Models
- [x] Create `app/models.py`
  - [x] Define Pydantic models for Workout, Routine, Exercise
  - [x] Add request/response models for API endpoints
  - [x] Include validation and type hints
  - [x] Add optional fields and defaults

### 3. Hevy API Integration
- [ ] Refactor existing `app/hevy/client.py`
  - [ ] Use config.py for API key management
  - [ ] Add proper error handling and logging
  - [ ] Add type hints and docstrings
  - [ ] Test all existing endpoints work correctly

### 4. LLM Interface
- [ ] Refactor existing `app/llm/interface.py`
  - [ ] Use config.py for OpenAI API key
  - [ ] Add proper error handling
  - [ ] Create reusable prompt templates
  - [ ] Add conversation context management
  - [ ] Test basic chat functionality

### 5. Workout Analysis
- [ ] Refactor existing `app/services/workout_analyzer.py`
  - [ ] Use models.py for data structures
  - [ ] Add proper error handling
  - [ ] Improve muscle group analysis
  - [ ] Add volume and intensity calculations
  - [ ] Test analysis functions

## Phase 2: API Integration

### 6. Connect Modules to FastAPI
- [ ] Update `app/main.py`
  - [ ] Import all modules (config, hevy_client, llm_interface, workout_analyzer)
  - [ ] Load config in lifespan handler
  - [ ] Connect `/workouts` endpoint to hevy_client
  - [ ] Connect `/chat` endpoint to llm_interface
  - [ ] Connect `/analyze` endpoint to workout_analyzer
  - [ ] Add proper error handling to all endpoints

### 7. Data Flow Implementation
- [ ] Implement proper request/response models
- [ ] Add input validation for all endpoints
- [ ] Handle API errors gracefully
- [ ] Add logging for debugging

## Phase 3: Testing & Quality

### 8. Testing Setup
- [ ] Create `tests/` directory
- [ ] Create `tests/__init__.py`
- [ ] Add basic test for `workout_analyzer.py`
- [ ] Add basic test for `hevy_client.py`
- [ ] Add basic test for `llm_interface.py`
- [ ] Add integration tests for API endpoints

### 9. Code Quality
- [ ] Add type hints to all functions
- [ ] Add docstrings to all public functions
- [ ] Add error handling throughout
- [ ] Add basic logging
- [ ] Code review and cleanup

## Phase 4: Documentation & Polish

### 10. Documentation
- [ ] Update `README.md`
  - [ ] Add setup instructions
  - [ ] Add usage examples
  - [ ] Add API endpoint documentation
  - [ ] Add troubleshooting section
- [ ] Update `ARCHITECTURE_PLAN.md` with any changes
- [ ] Update `MVP_PROJECT_ANALYSIS.md` with progress

### 11. Final Testing
- [ ] Test all endpoints with curl/Postman
- [ ] Test error scenarios
- [ ] Test with real Hevy data
- [ ] Test AI chat functionality
- [ ] Performance testing (basic)

## Phase 5: Optional Enhancements

### 12. Advanced Features (Future)
- [ ] Add caching layer
- [ ] Add rate limiting
- [ ] Add more sophisticated error handling
- [ ] Add request/response logging
- [ ] Add health check endpoint

## Requirements Update

### Current Requirements
```
requests
python-dotenv
openai
agents
fastapi
uvicorn
pydantic
pytest
httpx
python-multipart
email-validator
```

### Additional Requirements to Add
- [x] `pytest` - for testing
- [x] `httpx` - for async HTTP requests (optional, for testing)
- [x] `python-multipart` - for form data handling (if needed)
- [x] `email-validator` - for email validation (if needed)

## Success Criteria

### MVP Complete When:
- [ ] All endpoints return real data (not placeholders)
- [ ] Hevy API integration works correctly
- [ ] AI chat functionality works
- [ ] Workout analysis provides meaningful insights
- [ ] All tests pass
- [ ] Documentation is complete and accurate
- [ ] App can be run and tested locally

## Notes

- **Keep it simple**: Focus on core functionality first
- **Test as you go**: Don't wait until the end to test
- **Document changes**: Update docs as you implement features
- **Error handling**: Add proper error handling from the start
- **Type hints**: Use them consistently for better code quality

## Next Steps After MVP

1. **Database Integration**: Add SQLite/PostgreSQL for data persistence
2. **Frontend Development**: Add web/mobile interface
3. **Advanced AI Features**: More sophisticated analysis and recommendations
4. **User Management**: Authentication and user profiles
5. **Deployment**: Production deployment and monitoring

---

**Remember**: This is a learning project. Take your time, understand each step, and don't hesitate to ask for help when needed! 

## ✅ **Current Structure is Correct!**

The `config.py` and `models.py` files are properly located in the `app/` directory, which is the ideal structure for a FastAPI application:

### **Why This Structure is Good:**

1. **`app/config.py`** ✅
   - Central configuration accessible to all modules
   - Follows FastAPI best practices
   - Easy to import: `from app.config import config`

2. **`app/models.py`** ✅
   - Data models accessible to all modules
   - Clean separation of concerns
   - Easy to import: `from app.models import Workout, Exercise, etc.`

3. **Modular Organization** ✅
   - `app/hevy/` - Hevy API integration
   - `app/llm/` - LLM interface
   - `app/services/` - Business logic
   - `app/main.py` - FastAPI application entry point

### **Alternative Structures (Not Recommended for This Project):**

❌ **Root level config/models** - Would make imports messy
❌ **Separate config/ and models/ directories** - Overkill for this size project
❌ **Inside each module** - Would create circular dependencies

## **Current Structure is Perfect for:**
- ✅ Minimal, robust MVP
- ✅ Easy imports and maintenance
- ✅ Clear separation of concerns
- ✅ Scalable as the project grows

The structure you have is exactly what we want for a learning project that's minimal but well-organized. We can proceed with confidence to the next step! 

Ready to move on to **Step 3: Hevy API Integration**? 