import { create } from 'zustand'

type ExplanationLevel = 'basic' | 'intermediate' | 'advanced'

interface UIState {
  isLoading: boolean
  error: string | null
  activeExplanationLevel: ExplanationLevel
  currentQuizIndex: number
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setActiveExplanationLevel: (level: ExplanationLevel) => void
  setCurrentQuizIndex: (index: number) => void
  nextQuizQuestion: (total: number) => void
}

export const useUIStore = create<UIState>((set) => ({
  isLoading: false,
  error: null,
  activeExplanationLevel: 'basic',
  currentQuizIndex: 0,
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setActiveExplanationLevel: (level) => set({ activeExplanationLevel: level }),
  setCurrentQuizIndex: (index) => set({ currentQuizIndex: index }),
  nextQuizQuestion: (total) =>
    set((state) => ({
      currentQuizIndex: Math.min(state.currentQuizIndex + 1, total - 1),
    })),
}))
