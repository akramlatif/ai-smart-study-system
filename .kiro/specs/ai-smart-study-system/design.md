# Design Document: AI-Powered Smart Study System

## Overview

The AI-Powered Smart Study System is a full-stack web application that transforms raw educational content into structured, personalized learning experiences. Users can paste notes, upload documents, or ask questions; the system responds with multi-level explanations, context-aware quizzes, and a conversational AI tutor — all within a persistent study session.

### Key Design Goals

- **Grounded responses**: All AI output is anchored to user-provided content or clearly flagged as general knowledge.
- **Session continuity**: A session context window accumulates inputs and outputs so follow-up questions resolve naturally.
- **Multi-level pedagogy**: Every topic produces Basic, Intermediate, and Advanced explanations in a single pipeline pass.
- **Latency targets**: Text input → explanations ≤ 5 s; quiz generation ≤ 10 s; PDF extraction ≤ 15 s.
- **Isolation**: Each user's session is fully isolated; no cross-session data leakage.

### Technology Choices

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite | Component model maps cleanly to the multi-panel UI; strong typing reduces runtime errors |
| Styling | Tailwind CSS | Rapid utility-first styling; consistent design tokens |
| State management | Zustand | Lightweight; avoids Redux boilerplate for session/UI state |
| Backend | Python FastAPI | Async-native; excellent OpenAI SDK support; fast startup |
| AI | OpenAI GPT-4o | Best-in-class instruction following; structured JSON output mode |
| PDF parsing | PyMuPDF (fitz) | Fast, reliable text + structure extraction; handles complex layouts |
| Session storage | Redis (TTL = 2 h) | In-memory speed; built-in expiry satisfies the 2-hour retention requirement |
| Database | PostgreSQL + SQLAlchemy | Relational integrity for users, sessions, topics, quizzes |
| File storage | Local disk / S3-compatible | Uploaded files stored with per-user access controls; deleted after session end or 24 h |
| Auth | JWT (Bearer tokens) | Stateless; pairs well with FastAPI dependency injection |
| Transport security | HTTPS / TLS 1.3 | Encrypts documents in transit (Requirement 26.1) |

---

## Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (React SPA)                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐  │
│  │Dashboard │  │  Workspace   │  │  Quiz    │  │  Library   │  │
│  │  Screen  │  │   Screen     │  │  Screen  │  │  Screen    │  │
│  └──────────┘  └──────────────┘  └──────────┘  └────────────┘  │
│                        Zustand Store                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / REST + SSE
┌───────────────────────────▼─────────────────────────────────────┐
│                     FastAPI Application                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Input      │  │  Session     │  │  AI Pipeline         │   │
│  │  Router     │  │  Router      │  │  Router              │   │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                │                      │               │
│  ┌──────▼──────────────────────────────────────▼───────────┐   │
│  │                    Service Layer                         │   │
│  │  InputHandler │ ContentExtractor │ TopicAnalyzer        │   │
│  │  ExplanationGenerator │ QuizGenerator │ SessionManager  │   │
│  │  AccuracyController                                      │   │
│  └──────┬──────────────────────────────────────────────────┘   │
│         │                                                        │
│  ┌──────▼──────────────────────────────────────────────────┐   │
│  │              Infrastructure Layer                        │   │
│  │   PostgreSQL  │  Redis  │  OpenAI API  │  File Storage  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow (Text Input → Explanations + Quiz)

```
User types question
      │
      ▼
InputHandler.validate()          ← length, whitespace, char checks
      │
      ▼
SessionManager.get_or_create()   ← Redis lookup by session_id
      │
      ▼
TopicAnalyzer.analyze()          ← GPT-4o structured call → topics + confidence
      │
      ├─ confidence < 70% → return clarification request
      │
      ▼
ExplanationGenerator.generate()  ← single GPT-4o call, JSON mode
      │  returns {basic, intermediate, advanced}
      ▼
AccuracyController.validate()    ← relevance score ≥ 80%, grounding check
      │
      ▼
QuizGenerator.generate()         ← GPT-4o call with explanation context
      │  returns [{question, type, difficulty, options, answer, explanation}]
      ▼
SessionManager.append()          ← persist interaction to Redis + Postgres
      │
      ▼
HTTP Response → React UI
```

---

## Components and Interfaces

### Frontend Component Hierarchy

```
App
├── Layout
│   ├── Sidebar
│   │   ├── Logo
│   │   ├── StartNewSessionButton
│   │   └── NavMenu (Dashboard | Workspace | Quizzes | Library | Settings)
│   └── MainContent (route-based)
│
├── DashboardScreen
│   ├── WelcomeBanner
│   ├── QuickActionCards
│   │   ├── DeepDiveCard (resume last session)
│   │   └── QuickQuizCard (jump to quiz)
│   ├── CognitiveLoadChart (weekly bar chart)
│   ├── RecentNodesPanel
│   │   └── RecentNodeItem (subject icon, name, time ago, duration)
│   └── SynthesisSuggestionsPanel
│       └── SuggestionTag (High Relevance | Review Needed)
│
├── WorkspaceScreen
│   ├── InputPanel (left ~65%)
│   │   ├── InputSourceHeader
│   │   │   ├── UploadPDFButton
│   │   │   └── URLInputButton
│   │   ├── TextInputArea (paste notes / questions)
│   │   ├── MicrophoneButton
│   │   ├── AnalyzeButton
│   │   └── KnowledgeBreakdown
│   │       ├── LevelTabSwitcher (Basic | Intermediate | Advanced)
│   │       └── ExplanationCards
│   │           └── SubtopicCard (expandable, SYNTHESIZED badge)
│   └── ChatPanel (right ~35%)
│       ├── TutorHeader (avatar, "Online & Listening")
│       ├── MessageList
│       │   ├── AIMessage
│       │   └── UserMessage
│       ├── LoadingIndicator ("Synthesizing formulas...")
│       └── ChatInput (text box + send button)
│
├── QuizScreen
│   ├── QuizHeader (topic title, question counter "Q 2 of 5")
│   ├── QuestionDisplay
│   ├── AnswerOptionList
│   │   └── AnswerOption (A/B/C/D card, teal highlight on correct)
│   ├── AnswerExplanationCallout (blue left-border, shown after selection)
│   ├── SaveForReviewButton (bookmark)
│   └── NextQuestionButton
│
└── LibraryScreen
    ├── SessionHistoryList
    └── SavedQuizList
```

### Backend Service Interfaces

```python
# InputHandler
async def validate_text(text: str) -> ValidationResult
async def validate_file(file: UploadFile) -> ValidationResult
async def extract_url_content(url: str) -> str

# ContentExtractor
async def extract_pdf(file_path: str) -> ExtractionResult
async def extract_text_file(file_path: str) -> ExtractionResult
async def assess_quality(text: str) -> QualityAssessment

# TopicAnalyzer
async def analyze(text: str, session_context: SessionContext) -> TopicAnalysis

# ExplanationGenerator
async def generate(topic: TopicAnalysis, session_context: SessionContext) -> ExplanationSet

# QuizGenerator
async def generate(topic: TopicAnalysis, explanations: ExplanationSet,
                   session_context: SessionContext) -> list[QuizQuestion]

# SessionManager
async def create_session(user_id: str) -> StudySession
async def get_session(session_id: str) -> StudySession | None
async def append_interaction(session_id: str, interaction: Interaction) -> None
async def reset_session(session_id: str) -> StudySession
async def get_summary(session_id: str) -> SessionSummary

# AccuracyController
async def validate_explanation(explanation: ExplanationSet,
                                topic: TopicAnalysis,
                                source_text: str) -> ValidationResult
async def validate_quiz(questions: list[QuizQuestion],
                         session_context: SessionContext) -> ValidationResult
```

---

## Data Models

### PostgreSQL Schema

```sql
-- Users
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Study Sessions (persistent record)
CREATE TABLE study_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    previous_id     UUID REFERENCES study_sessions(id),  -- for recovery after reset
    created_at      TIMESTAMPTZ DEFAULT now(),
    ended_at        TIMESTAMPTZ,
    interaction_count INT DEFAULT 0
);

-- Topics identified within a session
CREATE TABLE topics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES study_sessions(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    is_main         BOOLEAN DEFAULT TRUE,
    parent_id       UUID REFERENCES topics(id),  -- NULL for main topics
    confidence      FLOAT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Explanations generated per topic
CREATE TABLE explanations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id        UUID REFERENCES topics(id) ON DELETE CASCADE,
    level           TEXT CHECK (level IN ('basic', 'intermediate', 'advanced')) NOT NULL,
    content         TEXT NOT NULL,
    word_count      INT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Quiz questions
CREATE TABLE quiz_questions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES study_sessions(id) ON DELETE CASCADE,
    topic_id        UUID REFERENCES topics(id),
    question_type   TEXT CHECK (question_type IN ('multiple_choice', 'short_answer')) NOT NULL,
    difficulty      TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')) NOT NULL,
    question_text   TEXT NOT NULL,
    options         JSONB,          -- [{label, text}] for MCQ; NULL for short_answer
    correct_answer  TEXT NOT NULL,
    explanation     TEXT,
    saved_for_review BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Uploaded documents (metadata only; content stored in file storage)
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES study_sessions(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    file_type       TEXT NOT NULL,
    file_size_bytes INT NOT NULL,
    storage_path    TEXT NOT NULL,
    quality_flag    TEXT CHECK (quality_flag IN ('ok', 'low_quality', 'unreadable')),
    expires_at      TIMESTAMPTZ NOT NULL,  -- session end or +24h
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

### Python Pydantic Models (API layer)

```python
class ValidationResult(BaseModel):
    valid: bool
    error_code: str | None = None
    error_message: str | None = None

class TopicAnalysis(BaseModel):
    main_topic: str
    subtopics: list[str]          # up to 5
    confidence: float             # 0.0–1.0
    needs_clarification: bool

class ExplanationSet(BaseModel):
    topic_id: str
    basic: ExplanationContent
    intermediate: ExplanationContent
    advanced: ExplanationContent

class ExplanationContent(BaseModel):
    level: Literal["basic", "intermediate", "advanced"]
    content: str
    word_count: int
    source_references: list[str]  # cited sections from uploaded docs

class QuizQuestion(BaseModel):
    id: str
    question_type: Literal["multiple_choice", "short_answer"]
    difficulty: Literal["easy", "medium", "hard"]
    question_text: str
    options: list[AnswerOption] | None   # MCQ only
    correct_answer: str
    explanation: str | None
    saved_for_review: bool = False

class AnswerOption(BaseModel):
    label: Literal["A", "B", "C", "D"]
    text: str
    is_correct: bool

class StudySession(BaseModel):
    id: str
    user_id: str
    previous_id: str | None
    topics: list[TopicAnalysis]
    explanations: list[ExplanationSet]
    quiz_questions: list[QuizQuestion]
    interactions: list[Interaction]
    created_at: datetime
    last_active: datetime

class Interaction(BaseModel):
    index: int                    # 1-based, max 50
    role: Literal["user", "assistant"]
    content: str
    input_type: Literal["text", "pdf", "file", "url", "shortcut"]
    timestamp: datetime

class SessionSummary(BaseModel):
    session_id: str
    topics_studied: list[str]
    questions_asked: int
    quiz_questions_generated: int
    duration_minutes: float
    interactions: list[Interaction]  # chronological

class QualityAssessment(BaseModel):
    char_count: int
    flag: Literal["ok", "low_quality", "unreadable"]
    message: str | None
```

### Redis Session Cache Schema

```
Key:   session:{session_id}
Type:  JSON string (compressed)
TTL:   7200 seconds (2 hours, reset on each interaction)
Value: StudySession (serialized)
```

---

## AI Pipeline Design

### Pipeline Overview

```
Raw Input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Stage 1: Input Normalization                        │
│  • Text: trim, validate length (3–500 chars for Q,  │
│    3–10,000 for notes)                               │
│  • PDF: PyMuPDF extraction → structured text blocks  │
│  • File: UTF-8 decode → plain text                   │
│  • URL: httpx fetch → readability extraction         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Stage 2: Topic Analysis (GPT-4o, JSON mode)         │
│  System prompt: "You are a topic extractor..."       │
│  Input: normalized text + session context summary    │
│  Output: {main_topic, subtopics[], confidence}       │
│  Fallback: confidence < 0.7 → clarification request  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Stage 3: Explanation Generation (GPT-4o, JSON mode) │
│  Single API call requesting all 3 levels at once     │
│  System prompt enforces:                             │
│  • basic: 150–300 words, no jargon                   │
│  • intermediate: 300–500 words, key terms + examples │
│  • advanced: 400–700 words, formal notation          │
│  Context window includes: source text + prior turns  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Stage 4: Accuracy Validation                        │
│  • Relevance scoring: cosine similarity of           │
│    explanation embeddings vs. source text            │
│  • Grounding check: flag claims not in source        │
│  • Reject if relevance < 0.80; retry once            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Stage 5: Quiz Generation (GPT-4o, JSON mode)        │
│  Input: topic + all 3 explanations + source text     │
│  Output: ≥5 questions with mixed difficulty          │
│  Constraints enforced in prompt:                     │
│  • ≥1 easy, ≥1 medium, ≥1 hard                       │
│  • MCQ: exactly 4 options, 1 correct                 │
│  • Questions grounded in session context only        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Stage 6: Session Update                             │
│  • Append interaction to Redis (TTL reset)           │
│  • Persist topic/explanation/quiz to PostgreSQL      │
│  • Update interaction_count (max 50)                 │
└─────────────────────────────────────────────────────┘
```

### Shortcut Detection (Requirement 29)

Before Stage 2, the `InputHandler` runs a lightweight regex/keyword classifier:

| Pattern | Action |
|---|---|
| `simplify this`, `explain simply`, `make it easier` | Skip Stage 2; use last topic; force `basic` level only |
| `go deeper`, `more advanced`, `technical details` | Skip Stage 2; use last topic; force `advanced` level only |
| `hard questions from this topic` | Skip Stages 2–4; jump to Stage 5 with `difficulty=hard` filter |

### Follow-Up Context Injection

For every non-shortcut follow-up, the session context is injected into the Stage 2 and Stage 3 prompts as a structured summary:

```
[Session Context]
Main topic: Quantum Mechanics
Subtopics: Superposition, Entanglement, Wave function collapse
Prior interactions: 3
Last explanation level: intermediate
Source material: [first 2000 chars of uploaded PDF]
```

This allows the model to resolve pronouns ("this", "that topic") and maintain topical coherence.

### Prompt Engineering Strategy

- **JSON mode** is used for all structured outputs (topic analysis, explanations, quiz questions) to guarantee parseable responses.
- **System prompts** are versioned and stored in `prompts/` directory; swappable without code changes.
- **Temperature**: 0.3 for explanations (consistency), 0.7 for quiz generation (variety).
- **Max tokens**: 2000 for explanations, 3000 for quiz batch.

---

## Session Context Management Design

### Context Lifecycle

```
Session Created (Redis + Postgres)
        │
        ▼
Interaction 1: Input → Topics stored in context
        │
        ▼
Interaction 2–50: Each interaction appends to context
        │         TTL reset to 2h on each write
        ▼
Inactivity > 2h: Redis evicts; Postgres record preserved
        │
        ├── User returns: session reconstructed from Postgres
        │
        └── User resets: previous_id saved; new session created
```

### Context Window Management

The full session history is stored in Redis. When building the AI prompt context window, the `SessionManager` applies a sliding window strategy:

1. Always include the **first interaction** (establishes the main topic).
2. Always include the **last 5 interactions** (recent context).
3. Include the **source document excerpt** (up to 2000 chars) if available.
4. Summarize older interactions into a compact bullet list if total tokens would exceed 6000.

This keeps prompt costs bounded while preserving topical coherence across long sessions.

### Session Isolation

- Each session has a UUID; Redis keys are namespaced as `session:{uuid}`.
- File storage paths are `uploads/{user_id}/{session_id}/{filename}`.
- Database queries always filter by `user_id` in addition to `session_id`.
- JWT claims include `user_id`; all service calls validate ownership before returning data.

---

## API Contract

### Base URL: `/api/v1`

#### Input & Analysis

```
POST /sessions
  Body: {}
  Response: { session_id, created_at }

POST /sessions/{session_id}/analyze
  Body: {
    input_type: "text" | "pdf" | "file" | "url",
    content?: string,          // for text input
    url?: string               // for URL input
  }
  Multipart: file              // for pdf/file uploads
  Response: {
    session_id,
    topic: TopicAnalysis,
    explanations: ExplanationSet,
    quiz_questions: QuizQuestion[]
  }

POST /sessions/{session_id}/chat
  Body: { message: string }
  Response: {
    response_type: "explanation" | "quiz" | "clarification" | "summary",
    topic?: TopicAnalysis,
    explanations?: ExplanationSet,
    quiz_questions?: QuizQuestion[],
    message?: string
  }
```

#### Session Management

```
GET  /sessions/{session_id}
  Response: StudySession

GET  /sessions/{session_id}/summary
  Response: SessionSummary

POST /sessions/{session_id}/reset
  Response: { new_session_id, previous_session_id }

DELETE /sessions/{session_id}
  Response: { deleted: true }
```

#### Quiz

```
GET  /sessions/{session_id}/quiz
  Query: ?difficulty=easy|medium|hard&type=multiple_choice|short_answer
  Response: QuizQuestion[]

PATCH /quiz-questions/{question_id}/save-for-review
  Response: { saved: true }

GET  /sessions/{session_id}/quiz/{question_id}/answer
  Response: { correct_answer, explanation }
```

#### Documents

```
POST /sessions/{session_id}/documents
  Multipart: file (PDF, .txt, .md, .rtf)
  Response: { document_id, quality_flag, extracted_char_count }

DELETE /documents/{document_id}
  Response: { deleted: true }
```

#### Dashboard

```
GET  /users/{user_id}/sessions
  Query: ?limit=10&offset=0
  Response: StudySession[]  (recent sessions for dashboard)

GET  /users/{user_id}/synthesis-suggestions
  Response: [{ topic, relevance_tag, last_studied }]
```

### Server-Sent Events (SSE) for Streaming

For long-running operations, the backend streams progress events:

```
GET /sessions/{session_id}/analyze/stream
  Events:
    data: {"stage": "extracting", "progress": 30}
    data: {"stage": "analyzing_topics", "progress": 50}
    data: {"stage": "generating_explanations", "progress": 75}
    data: {"stage": "generating_quiz", "progress": 90}
    data: {"stage": "complete", "progress": 100, "result": {...}}
```

### Error Response Format

```json
{
  "error": {
    "code": "INPUT_TOO_LONG",
    "message": "Input exceeds the 10,000 character limit for notes.",
    "user_facing": true,
    "guidance": "Please shorten your notes or split them into multiple sessions.",
    "retry_allowed": true
  }
}
```

Error codes: `INPUT_TOO_SHORT`, `INPUT_TOO_LONG`, `FILE_TOO_LARGE`, `UNSUPPORTED_FORMAT`, `PDF_UNREADABLE`, `LOW_QUALITY_DOCUMENT`, `TOPIC_UNCLEAR`, `RELEVANCE_BELOW_THRESHOLD`, `SESSION_NOT_FOUND`, `SESSION_EXPIRED`, `RATE_LIMITED`, `INTERNAL_ERROR`.

---

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Input Length Validation

*For any* text input submitted to the Input_Handler, the handler SHALL accept the input if and only if its trimmed length is within the valid range for its input type (3–500 characters for questions; 3–10,000 characters for notes), and SHALL reject inputs that are empty, whitespace-only, or exceed the maximum length with an appropriate error code.

**Validates: Requirements 1.1, 1.2, 1.4, 2.1, 2.5**

### Property 2: Input Preservation Round-Trip

*For any* valid text input submitted to the system, the original input text stored in the session context SHALL equal the text that was submitted — no truncation, mutation, or encoding loss.

**Validates: Requirements 1.5**

### Property 3: Topic Structure Constraints

*For any* valid input processed by the Topic_Analyzer, the resulting TopicAnalysis SHALL contain exactly one main topic and between 0 and 5 subtopics (inclusive).

**Validates: Requirements 2.4, 5.1**

### Property 4: Confidence Score Validity and Clarification Threshold

*For any* TopicAnalysis result produced by the Topic_Analyzer, the confidence score SHALL be a float in the range [0.0, 1.0], and the `needs_clarification` flag SHALL be true if and only if the confidence score is strictly less than 0.70.

**Validates: Requirements 5.4, 5.5, 19.5**

### Property 5: Explanation Word Count Bounds

*For any* ExplanationSet generated by the Explanation_Generator, each explanation level SHALL have a word count within its specified bounds: basic in [150, 300], intermediate in [300, 500], and advanced in [400, 700].

**Validates: Requirements 6.4, 7.5, 8.4**

### Property 6: Explanation Set Completeness

*For any* topic processed by the Explanation_Generator, the resulting ExplanationSet SHALL contain all three levels — basic, intermediate, and advanced — each with non-empty content.

**Validates: Requirements 9.2**

### Property 7: Quiz Difficulty Distribution

*For any* quiz set generated by the Quiz_Generator, the set SHALL contain at least 5 questions, every question SHALL have a difficulty label in {easy, medium, hard}, and the set SHALL include at least one question of each difficulty level.

**Validates: Requirements 10.1, 11.1, 11.2, 11.3, 11.4**

### Property 8: MCQ Structure and Answer Key Completeness

*For any* multiple-choice question generated by the Quiz_Generator, the question SHALL have exactly 4 answer options, exactly one of which is marked correct, and the correct_answer field SHALL be non-empty for all question types.

**Validates: Requirements 12.3, 28.1**

### Property 9: Session ID Uniqueness

*For any* two study sessions created by the Session_Manager, their session identifiers SHALL be distinct — no two sessions share the same ID.

**Validates: Requirements 13.2**

### Property 10: Session Summary Chronological Order

*For any* session summary produced by the Session_Manager, the interactions in the summary SHALL be ordered by timestamp in strictly ascending (chronological) order.

**Validates: Requirements 17.5**

### Property 11: Relevance Score Validity and Output Threshold

*For any* response produced by the Accuracy_Controller, the relevance score SHALL be a float in [0.0, 1.0], and any response with a relevance score below 0.80 SHALL be rejected and not returned to the user.

**Validates: Requirements 20.4, 20.5**

### Property 12: Shortcut Phrase Recognition

*For any* user input that contains a recognized simplification shortcut phrase (e.g., "simplify this", "explain simply", "make it easier"), the Input_Handler SHALL classify it as a simplification shortcut; and for any input containing a depth shortcut phrase (e.g., "go deeper", "more advanced", "technical details"), the Input_Handler SHALL classify it as a depth shortcut — regardless of surrounding text.

**Validates: Requirements 29.1, 29.2**

### Property 13: Document Quality Flag Threshold

*For any* document processed by the Content_Extractor, if the extracted text length is less than 50 characters, the quality_flag SHALL be set to `low_quality`; otherwise it SHALL be `ok` (assuming the document is readable).

**Validates: Requirements 3.5, 22.2**

---

## Error Handling

### Error Classification

| Category | Examples | Handling Strategy |
|---|---|---|
| User input errors | Too long, wrong format, empty | Return 400 with `user_facing: true`, specific guidance, `retry_allowed: true` |
| Document errors | Corrupted PDF, unreadable file, low quality | Return 422 with quality flag and guidance |
| AI pipeline errors | Topic unclear, relevance below threshold | Retry once; if still failing, return 422 with clarification request |
| Session errors | Session not found, expired, capacity exceeded | Return 404/410 with session recovery guidance |
| System errors | DB down, Redis unavailable, OpenAI timeout | Return 503; preserve session state; do not expose stack traces |

### Error Handling Rules

1. **Session preservation**: Errors during explanation or quiz generation MUST NOT corrupt or clear the session context (Requirement 27.4).
2. **User vs. system distinction**: HTTP 4xx for user-correctable errors; HTTP 5xx for system faults (Requirement 27.2).
3. **Retry guidance**: All user-correctable errors include a `guidance` field with actionable instructions (Requirement 27.3).
4. **No technical leakage**: Stack traces, SQL errors, and internal paths are logged server-side only; never returned to the client (Requirement 27.5).
5. **Graceful AI degradation**: If the OpenAI API is unavailable, return a 503 with an estimated retry time rather than a generic error.
6. **Validation short-circuit**: Input validation runs before any AI call; invalid inputs are rejected immediately without incurring API costs.

### Retry Logic

```
AI call fails (timeout / rate limit)
    │
    ├── Retry 1 (after 1s exponential backoff)
    │       │
    │       ├── Success → continue pipeline
    │       └── Fail → Retry 2 (after 2s)
    │                   │
    │                   ├── Success → continue pipeline
    │                   └── Fail → return 503 to client
    │
Relevance check fails (score < 0.80)
    │
    ├── Regenerate once with stricter grounding prompt
    │       │
    │       ├── Passes → return result
    │       └── Fails → return 422 RELEVANCE_BELOW_THRESHOLD
```

---

## Testing Strategy

### Dual Testing Approach

The system uses both unit/example-based tests and property-based tests for comprehensive coverage.

**Unit tests** cover:
- Specific input validation examples (exact boundary values, known error cases)
- PDF extraction with representative fixture files
- Session CRUD operations with known data
- API endpoint integration with mocked AI service
- Error response format and HTTP status codes

**Property-based tests** cover:
- All 13 correctness properties defined above
- Run with [Hypothesis](https://hypothesis.readthedocs.io/) (Python) on the backend
- Minimum **100 iterations** per property test
- AI service calls are **mocked** in property tests to keep execution fast and deterministic

### Property Test Configuration

```python
# Example: Property 1 — Input Length Validation
# Feature: ai-smart-study-system, Property 1: Input length validation

from hypothesis import given, settings
from hypothesis import strategies as st

@given(st.text(min_size=0, max_size=600))
@settings(max_examples=200)
def test_text_question_length_validation(text):
    result = InputHandler.validate_text(text, input_type="question")
    trimmed = text.strip()
    if 3 <= len(trimmed) <= 500:
        assert result.valid
    else:
        assert not result.valid
        assert result.error_code in ("INPUT_TOO_SHORT", "INPUT_TOO_LONG")
```

```python
# Feature: ai-smart-study-system, Property 7: Quiz difficulty distribution

@given(st.lists(quiz_question_strategy(), min_size=5, max_size=20))
@settings(max_examples=100)
def test_quiz_difficulty_distribution(questions):
    difficulties = {q.difficulty for q in questions}
    assert difficulties == {"easy", "medium", "hard"}
```

### Test Organization

```
tests/
├── unit/
│   ├── test_input_handler.py
│   ├── test_content_extractor.py
│   ├── test_topic_analyzer.py
│   ├── test_explanation_generator.py
│   ├── test_quiz_generator.py
│   ├── test_session_manager.py
│   └── test_accuracy_controller.py
├── property/
│   ├── test_input_validation_properties.py    # Properties 1, 2, 12, 13
│   ├── test_topic_analysis_properties.py      # Properties 3, 4
│   ├── test_explanation_properties.py         # Properties 5, 6
│   ├── test_quiz_properties.py                # Properties 7, 8
│   └── test_session_properties.py             # Properties 9, 10, 11
├── integration/
│   ├── test_pdf_extraction.py
│   ├── test_ai_pipeline_e2e.py
│   ├── test_session_ttl.py
│   └── test_concurrent_sessions.py
└── fixtures/
    ├── sample_notes.txt
    ├── sample_lecture.pdf
    └── corrupted.pdf
```

### Frontend Testing

- **Component tests**: React Testing Library for all UI components
- **Snapshot tests**: Storybook + Chromatic for visual regression on explanation cards, quiz options, and dashboard widgets
- **E2E tests**: Playwright covering the primary user flows (paste notes → view explanations → take quiz → reset session)

---

## Key Design Decisions and Tradeoffs

### Decision 1: Single GPT-4o Call for All Three Explanation Levels

**Decision**: Request all three explanation levels (basic, intermediate, advanced) in a single structured JSON API call rather than three separate calls.

**Rationale**: Reduces latency by ~60% (one round-trip vs. three), lowers API costs, and ensures the model maintains consistent terminology across levels since it generates them in the same context window.

**Tradeoff**: A single call failure means all three levels fail together. Mitigated by the retry logic described in Error Handling.

### Decision 2: Redis for Session Context, PostgreSQL for Persistence

**Decision**: Hot session data lives in Redis (fast reads, automatic TTL expiry); cold/historical data is persisted to PostgreSQL.

**Rationale**: Redis provides sub-millisecond session lookups needed for follow-up question processing. PostgreSQL provides durable storage for session recovery after Redis eviction and for the dashboard's recent sessions list.

**Tradeoff**: Two storage systems to maintain. Mitigated by a thin `SessionRepository` abstraction that handles write-through to both stores.

### Decision 3: Accuracy Validation via Embedding Cosine Similarity

**Decision**: Use OpenAI's `text-embedding-3-small` to compute cosine similarity between generated explanations and source text as the relevance score.

**Rationale**: Provides a quantitative, automatable relevance check without requiring a second LLM call. Fast and cheap.

**Tradeoff**: Embedding similarity is a proxy for semantic relevance, not a perfect measure. A high similarity score doesn't guarantee factual accuracy. Mitigated by the grounding prompt that restricts the model to source material.

### Decision 4: SSE for Progress Streaming

**Decision**: Use Server-Sent Events (SSE) rather than WebSockets for progress updates during document processing.

**Rationale**: SSE is unidirectional (server → client), which matches the use case perfectly. Simpler to implement and proxy than WebSockets; works over standard HTTP/2.

**Tradeoff**: No bidirectional communication over the same connection. The chat panel uses standard REST POST calls for user messages, which is acceptable given the non-real-time nature of AI response generation.

### Decision 5: Shortcut Detection Before AI Pipeline

**Decision**: Detect shortcut phrases (Requirement 29) with a lightweight regex classifier in the `InputHandler` before invoking any AI service.

**Rationale**: Shortcuts are deterministic pattern matches — no need to spend an AI call on topic re-analysis. This also ensures shortcuts work even when the AI service is slow or degraded.

**Tradeoff**: Regex patterns may miss paraphrased shortcuts. Mitigated by including a small set of common variants and allowing the chat interface to handle unrecognized variants through the normal pipeline.
