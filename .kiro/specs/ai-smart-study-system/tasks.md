# Implementation Plan: AI-Powered Smart Study System

## Overview

This implementation plan breaks down the AI-Powered Smart Study System into ordered, dependency-aware tasks. The system is a full-stack application with React + TypeScript frontend, Python FastAPI backend, PostgreSQL + Redis storage, and OpenAI GPT-4o integration.

**Tech Stack:**
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS + Zustand
- Backend: Python FastAPI + SQLAlchemy + Pydantic
- Database: PostgreSQL + Redis
- AI: OpenAI GPT-4o
- PDF Parsing: PyMuPDF (fitz)
- Testing: Hypothesis (PBT), Pytest, React Testing Library, Playwright

---

## Task List

### Phase 1: Project Setup & Infrastructure

- [ ] 1. Initialize Project Structure
  - [ ] 1.1 Create monorepo structure with `frontend/` and `backend/` directories
  - [ ] 1.2 Initialize frontend with Vite + React + TypeScript template
  - [ ] 1.3 Initialize backend with FastAPI project structure
  - [ ] 1.4 Set up `.gitignore` for both frontend and backend
  - [ ] 1.5 Create `README.md` with setup instructions

- [ ] 2. Configure Development Environment
  - [ ] 2.1 Create `backend/requirements.txt` with all Python dependencies
  - [ ] 2.2 Create `backend/requirements-dev.txt` for development dependencies
  - [ ] 2.3 Set up `frontend/package.json` with all npm dependencies
  - [ ] 2.4 Create `.env.example` files for both frontend and backend
  - [ ] 2.5 Set up Docker Compose for PostgreSQL and Redis

- [ ] 3. Database Setup
  - [ ] 3.1 Create PostgreSQL schema migration files (Alembic)
  - [ ] 3.2 Implement `users` table migration
  - [ ] 3.3 Implement `study_sessions` table migration
  - [ ] 3.4 Implement `topics` table migration
  - [ ] 3.5 Implement `explanations` table migration
  - [ ] 3.6 Implement `quiz_questions` table migration
  - [ ] 3.7 Implement `documents` table migration
  - [ ] 3.8 Create database initialization script
  - [ ] 3.9 Configure Redis connection with TTL settings

- [ ] 4. Backend Core Infrastructure
  - [ ] 4.1 Set up FastAPI application with CORS middleware
  - [ ] 4.2 Configure SQLAlchemy engine and session management
  - [ ] 4.3 Configure Redis client with connection pooling
  - [ ] 4.4 Implement JWT authentication middleware
  - [ ] 4.5 Create base Pydantic models for API responses
  - [ ] 4.6 Set up structured logging (JSON format)
  - [ ] 4.7 Create error handling middleware with standardized error responses
  - [ ] 4.8 Configure OpenAI API client with retry logic

---

### Phase 2: Backend Data Models & Repositories

- [ ] 5. SQLAlchemy ORM Models
  - [ ] 5.1 Create `User` model
  - [ ] 5.2 Create `StudySession` model with self-referential `previous_id`
  - [ ] 5.3 Create `Topic` model with self-referential `parent_id`
  - [ ] 5.4 Create `Explanation` model
  - [ ] 5.5 Create `QuizQuestion` model with JSONB options field
  - [ ] 5.6 Create `Document` model

- [ ] 6. Pydantic API Models
  - [ ] 6.1 Create `ValidationResult` model
  - [ ] 6.2 Create `TopicAnalysis` model
  - [ ] 6.3 Create `ExplanationSet` and `ExplanationContent` models
  - [ ] 6.4 Create `QuizQuestion` and `AnswerOption` models
  - [ ] 6.5 Create `StudySession` model
  - [ ] 6.6 Create `Interaction` model
  - [ ] 6.7 Create `SessionSummary` model
  - [ ] 6.8 Create `QualityAssessment` model
  - [ ] 6.9 Create error response models

- [ ] 7. Repository Layer
  - [ ] 7.1 Create `UserRepository` with CRUD operations
  - [ ] 7.2 Create `SessionRepository` with Redis + PostgreSQL write-through
  - [ ] 7.3 Create `TopicRepository` with hierarchical queries
  - [ ] 7.4 Create `ExplanationRepository`
  - [ ] 7.5 Create `QuizRepository` with filtering by difficulty/type
  - [ ] 7.6 Create `DocumentRepository` with expiry tracking

---

### Phase 3: Backend Service Layer

- [ ] 8. InputHandler Service
  - [ ] 8.1 Implement `validate_text()` with length checks (3-500 for questions, 3-10,000 for notes)
  - [ ] 8.2 Implement `validate_file()` with size and extension checks
  - [ ] 8.3 Implement `extract_url_content()` with httpx + readability
  - [ ] 8.4 Implement shortcut phrase detection (simplify/go deeper/hard questions)
  - [ ] 8.5 Create input normalization utilities (trim, whitespace handling)

- [ ] 9. ContentExtractor Service
  - [ ] 9.1 Implement `extract_pdf()` using PyMuPDF with structure preservation
  - [ ] 9.2 Implement `extract_text_file()` with UTF-8 decoding
  - [ ] 9.3 Implement `assess_quality()` with 50-character threshold
  - [ ] 9.4 Add error handling for corrupted/password-protected PDFs
  - [ ] 9.5 Implement file storage utilities (save/delete with user/session namespacing)

- [ ] 10. TopicAnalyzer Service
  - [ ] 10.1 Create topic extraction system prompt (versioned in `prompts/topic_analysis.txt`)
  - [ ] 10.2 Implement `analyze()` with GPT-4o JSON mode call
  - [ ] 10.3 Implement confidence score calculation and 0.70 threshold check
  - [ ] 10.4 Implement session context injection for follow-up questions
  - [ ] 10.5 Add retry logic for API failures (exponential backoff)

- [ ] 11. ExplanationGenerator Service
  - [ ] 11.1 Create explanation generation system prompt (versioned in `prompts/explanation_generation.txt`)
  - [ ] 11.2 Implement `generate()` with single GPT-4o call for all 3 levels
  - [ ] 11.3 Implement word count validation (basic: 150-300, intermediate: 300-500, advanced: 400-700)
  - [ ] 11.4 Implement source reference extraction from uploaded documents
  - [ ] 11.5 Add temperature=0.3 and max_tokens=2000 configuration

- [ ] 12. QuizGenerator Service
  - [ ] 12.1 Create quiz generation system prompt (versioned in `prompts/quiz_generation.txt`)
  - [ ] 12.2 Implement `generate()` with GPT-4o JSON mode call
  - [ ] 12.3 Implement difficulty distribution validation (≥1 easy, ≥1 medium, ≥1 hard)
  - [ ] 12.4 Implement MCQ structure validation (exactly 4 options, 1 correct)
  - [ ] 12.5 Add temperature=0.7 and max_tokens=3000 configuration

- [ ] 13. AccuracyController Service
  - [ ] 13.1 Implement `validate_explanation()` with embedding cosine similarity
  - [ ] 13.2 Implement relevance score calculation (threshold: 0.80)
  - [ ] 13.3 Implement grounding check (flag claims not in source)
  - [ ] 13.4 Implement `validate_quiz()` with session context alignment check
  - [ ] 13.5 Add retry logic for relevance failures (regenerate once with stricter prompt)

- [ ] 14. SessionManager Service
  - [ ] 14.1 Implement `create_session()` with UUID generation
  - [ ] 14.2 Implement `get_session()` with Redis lookup + PostgreSQL fallback
  - [ ] 14.3 Implement `append_interaction()` with Redis write + TTL reset (2 hours)
  - [ ] 14.4 Implement `reset_session()` with previous_id preservation
  - [ ] 14.5 Implement `get_summary()` with chronological ordering
  - [ ] 14.6 Implement sliding window context strategy (first + last 5 + source excerpt)
  - [ ] 14.7 Implement session isolation (UUID namespacing, user_id filtering)

---

### Phase 4: Backend API Routes

- [ ] 15. Session Routes (`/api/v1/sessions`)
  - [ ] 15.1 Implement `POST /sessions` (create new session)
  - [ ] 15.2 Implement `GET /sessions/{session_id}` (get session details)
  - [ ] 15.3 Implement `GET /sessions/{session_id}/summary` (get session summary)
  - [ ] 15.4 Implement `POST /sessions/{session_id}/reset` (reset session)
  - [ ] 15.5 Implement `DELETE /sessions/{session_id}` (delete session)

- [ ] 16. Analysis Routes (`/api/v1/sessions/{session_id}/analyze`)
  - [ ] 16.1 Implement `POST /sessions/{session_id}/analyze` (text input)
  - [ ] 16.2 Add multipart file upload support (PDF/text files)
  - [ ] 16.3 Add URL input support
  - [ ] 16.4 Implement AI pipeline orchestration (6 stages)
  - [ ] 16.5 Add input validation and error responses

- [ ] 17. Chat Routes (`/api/v1/sessions/{session_id}/chat`)
  - [ ] 17.1 Implement `POST /sessions/{session_id}/chat` (follow-up questions)
  - [ ] 17.2 Add shortcut phrase handling
  - [ ] 17.3 Add response type classification (explanation/quiz/clarification/summary)

- [ ] 18. Quiz Routes (`/api/v1/quiz`)
  - [ ] 18.1 Implement `GET /sessions/{session_id}/quiz` (get quiz questions with filters)
  - [ ] 18.2 Implement `PATCH /quiz-questions/{question_id}/save-for-review` (bookmark question)
  - [ ] 18.3 Implement `GET /sessions/{session_id}/quiz/{question_id}/answer` (get answer key)

- [ ] 19. Document Routes (`/api/v1/documents`)
  - [ ] 19.1 Implement `POST /sessions/{session_id}/documents` (upload document)
  - [ ] 19.2 Implement `DELETE /documents/{document_id}` (delete document)
  - [ ] 19.3 Add document expiry cleanup job (session end or +24h)

- [ ] 20. Dashboard Routes (`/api/v1/users/{user_id}`)
  - [ ] 20.1 Implement `GET /users/{user_id}/sessions` (recent sessions with pagination)
  - [ ] 20.2 Implement `GET /users/{user_id}/synthesis-suggestions` (AI-recommended topics)

- [ ] 21. SSE Streaming Route
  - [ ] 21.1 Implement `GET /sessions/{session_id}/analyze/stream` (progress events)
  - [ ] 21.2 Add stage progress tracking (extracting, analyzing, generating, etc.)

---

### Phase 5: Frontend Core Setup

- [ ] 22. Frontend Project Configuration
  - [ ] 22.1 Configure Tailwind CSS with custom design tokens (purple/cyan gradient theme)
  - [ ] 22.2 Set up Zustand store structure
  - [ ] 22.3 Configure React Router with routes (/, /workspace, /quiz, /library)
  - [ ] 22.4 Create API client with axios + interceptors
  - [ ] 22.5 Set up environment variables for API base URL

- [ ] 23. Zustand State Management
  - [ ] 23.1 Create `sessionStore` (current session, topics, explanations, quiz questions)
  - [ ] 23.2 Create `uiStore` (loading states, error messages, active tab)
  - [ ] 23.3 Create `authStore` (user info, JWT token)
  - [ ] 23.4 Implement store persistence with localStorage

- [ ] 24. Shared Components & Utilities
  - [ ] 24.1 Create `Button` component with variants (primary, secondary, ghost)
  - [ ] 24.2 Create `Input` component with validation states
  - [ ] 24.3 Create `Card` component
  - [ ] 24.4 Create `Badge` component (for difficulty levels, tags)
  - [ ] 24.5 Create `LoadingSpinner` component
  - [ ] 24.6 Create `ErrorMessage` component
  - [ ] 24.7 Create API utility functions (error handling, response parsing)

---

### Phase 6: Frontend Layout & Navigation

- [ ] 25. Layout Components
  - [ ] 25.1 Create `Layout` component (sidebar + main content)
  - [ ] 25.2 Create `Sidebar` component with logo and navigation
  - [ ] 25.3 Create `Logo` component (SmartStudy branding)
  - [ ] 25.4 Create `StartNewSessionButton` component
  - [ ] 25.5 Create `NavMenu` component (Dashboard, Workspace, Quizzes, Library, Settings)
  - [ ] 25.6 Add active route highlighting

---

### Phase 7: Dashboard Screen

- [ ] 26. Dashboard Components
  - [ ] 26.1 Create `DashboardScreen` container component
  - [ ] 26.2 Create `WelcomeBanner` component with user name
  - [ ] 26.3 Create `QuickActionCards` component
  - [ ] 26.4 Create `DeepDiveCard` component (resume last session)
  - [ ] 26.5 Create `QuickQuizCard` component (jump to quiz)
  - [ ] 26.6 Create `CognitiveLoadChart` component (weekly bar chart with Chart.js)
  - [ ] 26.7 Create `RecentNodesPanel` component
  - [ ] 26.8 Create `RecentNodeItem` component (subject icon, name, time ago, duration)
  - [ ] 26.9 Create `SynthesisSuggestionsPanel` component
  - [ ] 26.10 Create `SuggestionTag` component (High Relevance, Review Needed badges)

---

### Phase 8: Workspace Screen

- [ ] 27. Workspace Layout
  - [ ] 27.1 Create `WorkspaceScreen` container with split layout (65% left, 35% right)
  - [ ] 27.2 Create `InputPanel` component (left panel)
  - [ ] 27.3 Create `ChatPanel` component (right panel)

- [ ] 28. Input Panel Components
  - [ ] 28.1 Create `InputSourceHeader` component
  - [ ] 28.2 Create `UploadPDFButton` component with file picker
  - [ ] 28.3 Create `URLInputButton` component with modal
  - [ ] 28.4 Create `TextInputArea` component (large textarea with placeholder)
  - [ ] 28.5 Create `MicrophoneButton` component (voice input - optional)
  - [ ] 28.6 Create `AnalyzeButton` component with loading state
  - [ ] 28.7 Create `KnowledgeBreakdown` component
  - [ ] 28.8 Create `LevelTabSwitcher` component (Basic/Intermediate/Advanced tabs)
  - [ ] 28.9 Create `ExplanationCards` component
  - [ ] 28.10 Create `SubtopicCard` component (expandable with SYNTHESIZED badge)

- [ ] 29. Chat Panel Components
  - [ ] 29.1 Create `TutorHeader` component (avatar, "Online & Listening" status)
  - [ ] 29.2 Create `MessageList` component with auto-scroll
  - [ ] 29.3 Create `AIMessage` component (left-aligned, gray background)
  - [ ] 29.4 Create `UserMessage` component (right-aligned, purple background)
  - [ ] 29.5 Create `LoadingIndicator` component ("Synthesizing formulas..." animation)
  - [ ] 29.6 Create `ChatInput` component (text box + send button)

---

### Phase 9: Quiz Screen

- [ ] 30. Quiz Components
  - [ ] 30.1 Create `QuizScreen` container component
  - [ ] 30.2 Create `QuizHeader` component (topic title, question counter "Q 2 of 5")
  - [ ] 30.3 Create `QuestionDisplay` component
  - [ ] 30.4 Create `AnswerOptionList` component
  - [ ] 30.5 Create `AnswerOption` component (A/B/C/D card with teal highlight on correct)
  - [ ] 30.6 Create `AnswerExplanationCallout` component (blue left-border, shown after selection)
  - [ ] 30.7 Create `SaveForReviewButton` component (bookmark icon)
  - [ ] 30.8 Create `NextQuestionButton` component
  - [ ] 30.9 Implement quiz navigation logic (next/previous)
  - [ ] 30.10 Implement answer selection and validation

---

### Phase 10: Library Screen

- [ ] 31. Library Components
  - [ ] 31.1 Create `LibraryScreen` container component
  - [ ] 31.2 Create `SessionHistoryList` component with pagination
  - [ ] 31.3 Create `SessionHistoryItem` component (session card with metadata)
  - [ ] 31.4 Create `SavedQuizList` component
  - [ ] 31.5 Create `SavedQuizItem` component (bookmarked questions)

---

### Phase 11: Frontend-Backend Integration

- [ ] 32. API Integration
  - [ ] 32.1 Implement session creation API call
  - [ ] 32.2 Implement analyze API call (text/PDF/file/URL)
  - [ ] 32.3 Implement chat API call (follow-up questions)
  - [ ] 32.4 Implement quiz fetching API call
  - [ ] 32.5 Implement answer key reveal API call
  - [ ] 32.6 Implement session summary API call
  - [ ] 32.7 Implement session reset API call
  - [ ] 32.8 Implement SSE connection for progress streaming

- [ ] 33. State Synchronization
  - [ ] 33.1 Connect Zustand store to API responses
  - [ ] 33.2 Implement optimistic UI updates
  - [ ] 33.3 Implement error handling and retry logic
  - [ ] 33.4 Implement loading states for all async operations

---

### Phase 12: Property-Based Testing (Backend)

- [ ] 34. Property Test Setup
  - [ ] 34.1 Install Hypothesis and configure test settings
  - [ ] 34.2 Create custom Hypothesis strategies for domain models
  - [ ] 34.3 Set up test fixtures (sample PDFs, text files)

- [ ] 35. Input Validation Properties (Properties 1, 2, 12, 13)
  - [ ] 35.1 Implement Property 1: Input Length Validation test
  - [ ] 35.2 Implement Property 2: Input Preservation Round-Trip test
  - [ ] 35.3 Implement Property 12: Shortcut Phrase Recognition test
  - [ ] 35.4 Implement Property 13: Document Quality Flag Threshold test

- [ ] 36. Topic Analysis Properties (Properties 3, 4)
  - [ ] 36.1 Implement Property 3: Topic Structure Constraints test
  - [ ] 36.2 Implement Property 4: Confidence Score Validity test

- [ ] 37. Explanation Properties (Properties 5, 6)
  - [ ] 37.1 Implement Property 5: Explanation Word Count Bounds test
  - [ ] 37.2 Implement Property 6: Explanation Set Completeness test

- [ ] 38. Quiz Properties (Properties 7, 8)
  - [ ] 38.1 Implement Property 7: Quiz Difficulty Distribution test
  - [ ] 38.2 Implement Property 8: MCQ Structure and Answer Key Completeness test

- [ ] 39. Session Properties (Properties 9, 10, 11)
  - [ ] 39.1 Implement Property 9: Session ID Uniqueness test
  - [ ] 39.2 Implement Property 10: Session Summary Chronological Order test
  - [ ] 39.3 Implement Property 11: Relevance Score Validity test

---

### Phase 13: Unit & Integration Testing

- [ ] 40. Backend Unit Tests
  - [ ] 40.1 Write unit tests for InputHandler service
  - [ ] 40.2 Write unit tests for ContentExtractor service
  - [ ] 40.3 Write unit tests for TopicAnalyzer service (with mocked OpenAI)
  - [ ] 40.4 Write unit tests for ExplanationGenerator service (with mocked OpenAI)
  - [ ] 40.5 Write unit tests for QuizGenerator service (with mocked OpenAI)
  - [ ] 40.6 Write unit tests for SessionManager service
  - [ ] 40.7 Write unit tests for AccuracyController service

- [ ] 41. Backend Integration Tests
  - [ ] 41.1 Write integration test for PDF extraction pipeline
  - [ ] 41.2 Write integration test for full AI pipeline (end-to-end)
  - [ ] 41.3 Write integration test for session TTL expiry
  - [ ] 41.4 Write integration test for concurrent session handling
  - [ ] 41.5 Write integration test for error response formats

- [ ] 42. Frontend Component Tests
  - [ ] 42.1 Write React Testing Library tests for all shared components
  - [ ] 42.2 Write tests for Dashboard screen components
  - [ ] 42.3 Write tests for Workspace screen components
  - [ ] 42.4 Write tests for Quiz screen components
  - [ ] 42.5 Write tests for Library screen components

- [ ] 43. Frontend E2E Tests (Playwright)
  - [ ] 43.1 Write E2E test: Paste notes → view explanations → take quiz
  - [ ] 43.2 Write E2E test: Upload PDF → analyze → chat follow-up
  - [ ] 43.3 Write E2E test: Session reset flow
  - [ ] 43.4 Write E2E test: Quiz bookmark and review flow
  - [ ] 43.5 Write E2E test: Dashboard navigation and recent sessions

---

### Phase 14: Security & Performance

- [ ] 44. Security Implementation
  - [ ] 44.1 Implement JWT token generation and validation
  - [ ] 44.2 Implement user authentication endpoints (login/register)
  - [ ] 44.3 Add HTTPS/TLS configuration for production
  - [ ] 44.4 Implement file upload encryption during transmission
  - [ ] 44.5 Implement session isolation validation (user_id filtering)
  - [ ] 44.6 Add rate limiting middleware (per-user, per-endpoint)
  - [ ] 44.7 Implement document expiry cleanup job

- [ ] 45. Performance Optimization
  - [ ] 45.1 Add database query optimization (indexes on session_id, user_id, created_at)
  - [ ] 45.2 Implement Redis connection pooling
  - [ ] 45.3 Add response caching for dashboard data
  - [ ] 45.4 Optimize frontend bundle size (code splitting, lazy loading)
  - [ ] 45.5 Add frontend performance monitoring (Web Vitals)

---

### Phase 15: Deployment & Documentation

- [ ] 46. Deployment Configuration
  - [ ] 46.1 Create production Dockerfile for backend
  - [ ] 46.2 Create production Dockerfile for frontend
  - [ ] 46.3 Create docker-compose.yml for full stack deployment
  - [ ] 46.4 Create Kubernetes manifests (optional)
  - [ ] 46.5 Set up CI/CD pipeline (GitHub Actions or similar)

- [ ] 47. Documentation
  - [ ] 47.1 Write API documentation (OpenAPI/Swagger)
  - [ ] 47.2 Write deployment guide
  - [ ] 47.3 Write developer setup guide
  - [ ] 47.4 Write user guide with screenshots
  - [ ] 47.5 Document environment variables and configuration

- [ ] 48. Final Testing & Launch Preparation
  - [ ] 48.1 Run full test suite (unit + integration + property + E2E)
  - [ ] 48.2 Perform load testing (100 concurrent sessions)
  - [ ] 48.3 Verify all 30 requirements are met
  - [ ] 48.4 Verify all 13 correctness properties pass
  - [ ] 48.5 Perform security audit
  - [ ] 48.6 Create production deployment checklist

---

## Notes

- **Dependency Order**: Tasks are ordered by dependency. Infrastructure and data models must be completed before services, services before API routes, and backend before frontend integration.
- **Parallel Work**: Within each phase, many tasks can be worked on in parallel (e.g., different service modules, different frontend screens).
- **Testing**: Property-based tests should be written alongside service implementation to catch bugs early.
- **Incremental Delivery**: After Phase 11 (Frontend-Backend Integration), you have a working MVP. Phases 12-15 add robustness, security, and production readiness.
