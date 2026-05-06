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
  question_type: 'multiple_choice' | 'short_answer'
  difficulty: 'easy' | 'medium' | 'hard'
  question_text: string
  options: AnswerOption[] | null
  correct_answer: string
  explanation: string | null
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
