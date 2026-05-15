import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type ExplanationLevel = 'basic' | 'intermediate' | 'advanced'

interface UIState {
  isLoading: boolean
  error: string | null
  activeExplanationLevel: ExplanationLevel
  currentQuizIndex: number
  theme: 'light' | 'dark'
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setActiveExplanationLevel: (level: ExplanationLevel) => void
  setCurrentQuizIndex: (index: number) => void
  nextQuizQuestion: (total: number) => void
  toggleTheme: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      isLoading: false,
      error: null,
      activeExplanationLevel: 'basic',
      currentQuizIndex: 0,
      theme: 'light',
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      setActiveExplanationLevel: (level) => set({ activeExplanationLevel: level }),
      setCurrentQuizIndex: (index) => set({ currentQuizIndex: index }),
      nextQuizQuestion: (total) =>
        set((state) => ({
          currentQuizIndex: Math.min(state.currentQuizIndex + 1, total - 1),
        })),
      toggleTheme: () =>
        set((state) => ({
          theme: state.theme === 'light' ? 'dark' : 'light',
        })),
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({ theme: state.theme }), // Only persist theme
    }
  )
)
