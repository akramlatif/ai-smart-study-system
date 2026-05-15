import { create } from 'zustand'
import type {
  StudySession,
  TopicAnalysis,
  ExplanationSet,
  QuizQuestion,
  Interaction,
  FeynmanFeedback,
  SocraticQuestion,
  SocraticComplete,
  QuestionAnswerPair,
  TutorProgress,
  RevisionMaterial,
} from '../types'

interface SessionState {
  currentSession: StudySession | null
  topics: TopicAnalysis[]
  explanations: ExplanationSet[]
  quizQuestions: QuizQuestion[]
  interactions: Interaction[]
  // Feynman state
  feynmanFeedback: FeynmanFeedback | null
  // Socratic state
  socraticSessionId: string | null
  currentSocraticQuestion: SocraticQuestion | null
  socraticChain: QuestionAnswerPair[]
  socraticComplete: SocraticComplete | null
  // Tutor state
  tutorProgress: TutorProgress | null
  // Revision state
  revisionMaterial: RevisionMaterial | null
  // Actions
  setCurrentSession: (session: StudySession | null) => void
  addTopic: (topic: TopicAnalysis) => void
  addExplanations: (explanations: ExplanationSet) => void
  setQuizQuestions: (questions: QuizQuestion[]) => void
  addQuizQuestions: (questions: QuizQuestion[]) => void
  addInteraction: (interaction: Interaction) => void
  updateQuizQuestion: (id: string, updates: Partial<QuizQuestion>) => void
  clearSession: () => void
  // Feynman actions
  setFeynmanFeedback: (feedback: FeynmanFeedback | null) => void
  // Socratic actions
  setSocraticSession: (sessionId: string, question: SocraticQuestion) => void
  addSocraticQA: (pair: QuestionAnswerPair) => void
  completeSocratic: (completion: SocraticComplete) => void
  resetSocratic: () => void
  // Tutor actions
  setTutorProgress: (progress: TutorProgress | null) => void
  // Revision actions
  setRevisionMaterial: (material: RevisionMaterial | null) => void
}

export const useSessionStore = create<SessionState>((set) => ({
  currentSession: null,
  topics: [],
  explanations: [],
  quizQuestions: [],
  interactions: [],
  feynmanFeedback: null,
  socraticSessionId: null,
  currentSocraticQuestion: null,
  socraticChain: [],
  socraticComplete: null,
  tutorProgress: null,
  revisionMaterial: null,

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
      feynmanFeedback: null,
      socraticSessionId: null,
      currentSocraticQuestion: null,
      socraticChain: [],
      socraticComplete: null,
      tutorProgress: null,
      revisionMaterial: null,
    }),

  // Feynman actions
  setFeynmanFeedback: (feedback) => set({ feynmanFeedback: feedback }),

  // Socratic actions
  setSocraticSession: (sessionId, question) =>
    set({
      socraticSessionId: sessionId,
      currentSocraticQuestion: question,
      socraticChain: [],
      socraticComplete: null,
    }),

  addSocraticQA: (pair) =>
    set((state) => ({ socraticChain: [...state.socraticChain, pair] })),

  completeSocratic: (completion) =>
    set({
      socraticComplete: completion,
      currentSocraticQuestion: null,
    }),

  resetSocratic: () =>
    set({
      socraticSessionId: null,
      currentSocraticQuestion: null,
      socraticChain: [],
      socraticComplete: null,
    }),

  // Tutor actions
  setTutorProgress: (progress) => set({ tutorProgress: progress }),

  // Revision actions
  setRevisionMaterial: (material) => set({ revisionMaterial: material }),
}))
