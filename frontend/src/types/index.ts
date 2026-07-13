export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface AnswerOption {
  label: 'A' | 'B' | 'C' | 'D'
  text: string
  is_correct: boolean
}

export interface QuizQuestion {
  id: string
  question_type: 'multiple_choice' | 'short_answer' | 'true_false' | 'fill_blank'
  difficulty: 'easy' | 'medium' | 'hard'
  question_text: string
  options?: AnswerOption[]
  correct_answer: string
  explanation?: string
  hint?: string
  saved_for_review: boolean
}

export interface TopicAnalysis {
  main_topic: string
  subtopics: string[]
  confidence: number
  needs_clarification: boolean
}

export interface ExplanationContent {
  level: 'basic' | 'intermediate' | 'advanced'
  content: string
  word_count: number
  source_references: string[]
}

export interface ExplanationSet {
  topic_id: string
  basic: ExplanationContent
  intermediate: ExplanationContent
  advanced: ExplanationContent
}

export interface Interaction {
  index: number
  role: 'user' | 'assistant'
  content: string
  input_type: 'text' | 'pdf' | 'file' | 'url' | 'shortcut'
  timestamp: string
}

export interface StudySession {
  id: string
  user_id: string
  previous_id: string | null
  topics: TopicAnalysis[]
  explanations: ExplanationSet[]
  quiz_questions: QuizQuestion[]
  interactions: Interaction[]
  created_at: string
  last_active: string
}

export interface SessionSummary {
  session_id: string
  topics_studied: string[]
  questions_asked: number
  quiz_questions_generated: number
  duration_minutes: number
  interactions: Interaction[]
}

export interface AnalyzeResponse {
  session_id: string
  topic: TopicAnalysis
  explanations: ExplanationSet
  quiz_questions: QuizQuestion[]
  response_type?: string
  message?: string
}

export interface ChatResponse {
  session_id: string
  response_type: 'explanation' | 'quiz' | 'clarification' | 'summary'
  topic?: TopicAnalysis
  explanations?: ExplanationSet
  quiz_questions?: QuizQuestion[]
  message?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface SessionHistoryItem {
  id: string
  user_id: string
  previous_id: string | null
  created_at: string
  ended_at: string | null
  interaction_count: number
}

export interface SynthesisSuggestion {
  topic: string
  relevance_tag: 'high_relevance' | 'review_needed'
  last_studied: string
}

export interface FeynmanFeedback {
  comprehension_score: number
  strengths: string[]
  gaps: string[]
  misconceptions: string[]
  simplified_correction: string
  encouragement_message: string
}

export interface FeynmanAttemptResponse {
  attempt_id: string
  feedback: FeynmanFeedback
  topic: string
  created_at: string
}

export interface SocraticQuestion {
  question_text: string
  question_type: 'probing' | 'clarifying' | 'hypothetical' | 'evaluative'
  depth_level: number
}

export interface SocraticComplete {
  summary: string
  key_insights: string[]
  depth_reached: number
}

export interface SocraticResponse {
  is_complete: boolean
  question?: SocraticQuestion
  completion?: SocraticComplete
}

export interface SocraticSessionResponse {
  socratic_session_id: string
  question: SocraticQuestion
}

export interface QuestionAnswerPair {
  question_index: number
  question: SocraticQuestion
  student_answer?: string
}

// Tutor Mode Types
export interface SubtopicPlan {
  name: string
  description: string
  prerequisite: string | null
}

export interface TutorStartRequest {
  difficulty: string
}

export interface TutorStartResponse {
  tutor_session_id: string
  topic: string
  subtopics: SubtopicPlan[]
  current_subtopic: string
  current_index: number
  total_subtopics: number
  explanation: string
  question: string
  difficulty: string
}

export interface TutorEvaluation {
  is_correct: boolean
  score: number
  feedback: string
  hint: string | null
  simplified_explanation: string | null
  should_retry: boolean
}

export interface TutorAnswerRequest {
  tutor_session_id: string
  answer: string
}

export interface TutorAnswerResponse {
  evaluation: TutorEvaluation
  advanced: boolean
  is_session_complete: boolean
  next_subtopic: string | null
  next_explanation: string | null
  next_question: string | null
  current_index: number
  total_subtopics: number
  correct_count: number
  incorrect_count: number
  difficulty: string
}

export interface TutorStepDetail {
  subtopic_name: string
  subtopic_index: number
  explanation: string
  question_text: string
  student_answer: string | null
  is_correct: boolean | null
  score: number | null
  feedback: string | null
  attempts: number
  is_skipped: boolean
}

export interface TutorProgress {
  tutor_session_id: string
  topic: string
  subtopics: string[]
  current_index: number
  total_subtopics: number
  correct_count: number
  incorrect_count: number
  difficulty: string
  is_complete: boolean
  weak_areas: string[]
  steps: TutorStepDetail[]
}

// Revision System Types
export interface FlashcardData {
  front: string
  back: string
}

export interface FormulaData {
  formula: string
  description: string
}

export interface KeyDefinition {
  term: string
  definition: string
}

export interface ExamQuestion {
  question: string
  expected_answer: string
  difficulty: string
}

export interface RevisionMaterial {
  session_id: string
  topic: string
  summary_notes: string
  flashcards: FlashcardData[]
  formulas: FormulaData[]
  key_definitions: KeyDefinition[]
  exam_questions: ExamQuestion[]
}

export interface ReviewItem {
  attempt_id: string
  topic_id: string | null
  session_id: string
  source_mode: string
  difficulty: string
  next_review_at: string
  review_interval_days: number
  ease_factor: number
  question: QuizQuestion | null
}
