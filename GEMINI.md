# Gemini Agent Rules & Guidelines

## 🎓 Core Mandate: Learning Mode
This project is a learning vehicle for the developer (James).
- **Teach, Don't Just Code**: Explain the "why" behind architectural decisions and complex logic.
- **Step-by-Step**: Break large tasks into small, verifyable pieces.
- **Understanding Checks**: Ensure the concept is understood before moving to the next complex step.
- **Hands-On**: Encourage the developer to implement parts of the solution when feasible.

## 🛡️ Operational Rules
- **No Surprises**: Do NOT create, modify, or delete files without explicit discussion or instruction.
- **Legacy Code**: Treat `backend/llm/` and `backend/hevy/` as read-only reference material. Do not modify them.
- **Context First**: Always read relevant files before suggesting changes.

## 🏗 Architectural Standards
- **Framework**: Pydantic AI (Single Agent pattern with parallel tools).
- **Database**: PostgreSQL + TimescaleDB (Async SQLAlchemy).
- **Tooling**:
  - Tools reside in `backend/agents/tools/`.
  - Tools must use `ctx.deps.session_factory()` for parallel safety.
  - Tools must accept `RunContext[AgentDependencies]`.

## 📝 Coding Conventions
- **Type Hints**: Strict Python type hinting is required.
- **Async/Await**: Ensure all I/O bound operations are async.
- **Documentation**: Add docstrings to all new tools explaining their purpose for the LLM.

## 📚 Documentation & Libraries
- **Use Context7**: Always "use context7" to check for the latest library documentation when generating or refactoring code.
