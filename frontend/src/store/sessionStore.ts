import { create } from 'zustand'
import type {
  StudySession,
  TopicAnalysis,
  ExplanationSet,
  QuizQuestion,
  Interaction,
} from '../types'

interface SessionState {
  currentSession: StudySession | null
  topics: TopicAnalysis[]
  explanations: ExplanationSet[]
  quizQuestions: QuizQuestion[]
  interactions: Interaction[]
  setCurrentSession: (session: StudySession | null) => void
  addTopic: (topic: TopicAnalysis) => void
  addExplanations: (explanations: ExplanationSet) => void
  setQuizQuestions: (questions: QuizQuestion[]) => void
  addQuizQuestions: (questions: QuizQuestion[]) => void
  addInteraction: (interaction: Interaction) => void
  updateQuizQuestion: (id: string, updates: Partial<QuizQuestion>) => void
  clearSession: () => void
}

export const useSessionStore = create<SessionState>((set) => ({
  currentSession: null,
  topics: [],
  explanations: [],
  quizQuestions: [],
  interactions: [],

  setCurrentSession: (session) =>
    set({
      currentSession: session,
      topics: session?.topics ?? [],
      explanations: session?.explanations ?? [],
      quizQuestions: session?.quiz_questions ?? [],
      interactions: session?.interactions ?? [],
    }),

  addTopic: (topic) =>
    set((state) => ({ topics: [...state.topics, topic] })),

  addExplanations: (explanations) =>
    set((state) => ({ explanations: [...state.explanations, explanations] })),

  setQuizQuestions: (questions) => set({ quizQuestions: questions }),

  addQuizQuestions: (questions) =>
    set((state) => ({ quizQuestions: [...state.quizQuestions, ...questions] })),

  addInteraction: (interaction) =>
    set((state) => ({ interactions: [...state.interactions, interaction] })),

  updateQuizQuestion: (id, updates) =>
    set((state) => ({
      quizQuestions: state.quizQuestions.map((q) =>
        q.id === id ? { ...q, ...updates } : q
      ),
    })),

  clearSession: () =>
    set({
      currentSession: null,
      topics: [],
      explanations: [],
      quizQuestions: [],
      interactions: [],
    }),
}))
