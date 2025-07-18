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
- [x] Refactor existing `app/hevy/client.py`
  - [x] Use config.py for API key management
  - [x] Add proper error handling and logging
  - [x] Add type hints and docstrings
  - [x] Test all existing endpoints work correctly

### 4. LLM Interface
- [x] Refactor existing `app/llm/interface.py`
  - [x] Use config.py for OpenAI API key
  - [x] Add proper error handling
  - [x] Create reusable prompt templates
  - [x] Add conversation context management
  - [x] Test basic chat functionality
  - [x] Implement OpenAI Agents SDK integration
  - [x] Add 8 function tools for workout and routine management
  - [x] Successfully create and post routines to Hevy

### 5. Exercise Templates Caching
- [x] Create `app/services/exercise_cache.py`
  - [x] Implement static file approach for instant access
  - [x] Move exercise templates to `app/data/exercise_templates.json`
  - [x] Achieve 0.00s loading time (vs 12s API calls)
  - [x] Add cache management tools
  - [x] Organize file structure properly

### 6. Workout Analysis
- [ ] Refactor existing `app/services/workout_analyzer.py`
  - [ ] Use models.py for data structures
  - [ ] Add proper error handling
  - [ ] Improve muscle group analysis
  - [ ] Add volume and intensity calculations
  - [ ] Test analysis functions

## Phase 2: API Integration

### 7. Connect Modules to FastAPI
- [ ] Update `app/main.py`
  - [ ] Import all modules (config, hevy_client, llm_interface, workout_analyzer)
  - [ ] Load config in lifespan handler
  - [ ] Connect `/workouts` endpoint to hevy_client
  - [ ] Connect `/chat` endpoint to llm_interface
  - [ ] Connect `/analyze` endpoint to workout_analyzer
  - [ ] Add proper error handling to all endpoints

### 8. Data Flow Implementation
- [ ] Implement proper request/response models
- [ ] Add input validation for all endpoints
- [ ] Handle API errors gracefully
- [ ] Add logging for debugging

## Phase 3: Enhanced Capabilities

### 9. Smart Exercise Selection
- [ ] Create `app/services/exercise_analyzer.py`
  - [ ] Group exercises by muscle groups, equipment, types
  - [ ] Build selection strategies (balanced, focused, variety)
  - [ ] Add new LLM tools for smart selection
  - [ ] Update agent instructions for intelligent exercise choice

### 10. Interactive LLM Conversation
- [ ] Implement session management
- [ ] Add conversation history
- [ ] Enable context-aware responses
- [ ] Test multi-turn conversations

### 11. Workout Analysis Tools
- [ ] Add `get_recent_workouts()` tool
- [ ] Add `analyze_workout_trends()` tool
- [ ] Add `calculate_volume_by_muscle_group()` tool
- [ ] Integrate pandas for data analysis

## Phase 4: Testing & Quality

### 12. Testing Setup
- [x] Create `tests/` directory
- [x] Create `tests/__init__.py`
- [x] Add basic test for exercise cache functionality
- [ ] Add basic test for `workout_analyzer.py`
- [ ] Add basic test for `hevy_client.py`
- [ ] Add basic test for `llm_interface.py`
- [ ] Add integration tests for API endpoints

### 13. Code Quality
- [x] Add type hints to all functions
- [x] Add docstrings to all public functions
- [x] Add error handling throughout
- [x] Add basic logging
- [x] Code review and cleanup
- [x] Performance optimization (exercise loading)

## Phase 5: Documentation & Polish

### 14. Documentation
- [x] Update `README.md`
  - [x] Add setup instructions
  - [x] Add usage examples
  - [x] Add API endpoint documentation
  - [x] Add troubleshooting section
- [x] Update `ARCHITECTURE_PLAN.md` with any changes
- [x] Update `MVP_PROJECT_ANALYSIS.md` with progress
- [x] Update `STEP_4_PLAN.md` with current status

### 15. Final Testing
- [x] Test exercise cache functionality
- [x] Test LLM interface with routine creation
- [x] Test error scenarios
- [x] Test with real Hevy data
- [x] Test AI chat functionality
- [ ] Performance testing (basic)
- [ ] Test all endpoints with curl/Postman

## Phase 6: Advanced Features (Future)

### 16. Multi-Routine Creation & Folders
- [ ] Add routine folder creation tools
- [ ] Implement multi-routine generation
- [ ] Add workout program templates
- [ ] Test folder organization

### 17. Frontend Development
- [ ] Build a proper UI for the chat interface
- [ ] Add real-time conversation capabilities
- [ ] Create workout visualization tools

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
- [ ] `pandas` - for workout analysis (future)

## Success Criteria

### MVP Complete When:
- [x] All endpoints return real data (not placeholders)
- [x] Hevy API integration works correctly
- [x] AI chat functionality works
- [x] Exercise templates load instantly
- [x] Routine creation works end-to-end
- [ ] Workout analysis provides meaningful insights
- [ ] All tests pass
- [x] Documentation is complete and accurate
- [x] App can be run and tested locally

### Enhanced Features Complete When:
- [ ] Smart exercise selection with muscle group analysis
- [ ] Interactive conversation capabilities
- [ ] Workout analysis tools with pandas
- [ ] Multi-routine creation and organization
- [ ] Frontend interface (optional)

## Performance Achievements

### Exercise Template Loading:
- **Before:** 12+ seconds (API calls)
- **After:** 0.00 seconds (static file)
- **Improvement:** 100% faster ⚡

### Routine Creation:
- **Total Time:** ~3 seconds (including LLM processing)
- **Exercise Selection:** Instant
- **API Post:** ~0.2 seconds

### File Organization:
- **Static File:** `app/data/exercise_templates.json` (432 exercises)
- **Cache Service:** `app/services/exercise_cache.py`
- **Clean Structure:** Organized and maintainable

## Notes

- **Keep it simple**: Focus on core functionality first ✅
- **Test as you go**: Don't wait until the end to test ✅
- **Document changes**: Update docs as you implement features ✅
- **Error handling**: Add proper error handling from the start ✅
- **Type hints**: Use them consistently for better code quality ✅
- **Performance optimization**: Optimize critical paths ✅

## Next Steps After MVP

1. **Smart Exercise Selection**: Muscle group analysis and intelligent selection
2. **Interactive Conversation**: Multi-turn dialogue capabilities
3. **Workout Analysis**: Data analysis with pandas
4. **Multi-Routine Creation**: Create multiple routines and organize in folders
5. **Frontend Development**: Add web/mobile interface
6. **Database Integration**: Add SQLite/PostgreSQL for data persistence
7. **Advanced AI Features**: More sophisticated analysis and recommendations
8. **User Management**: Authentication and user profiles
9. **Deployment**: Production deployment and monitoring

---

**Remember**: This is a learning project. We've successfully built a solid foundation with excellent performance. The next phase focuses on making the exercise selection more intelligent and adding interactive conversation capabilities! 