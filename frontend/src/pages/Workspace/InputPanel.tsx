import React, { useState } from 'react'
import { InputSourceHeader } from './InputSourceHeader'
import { TextInputArea } from './TextInputArea'
import { AnalyzeButton } from './AnalyzeButton'
import { KnowledgeBreakdown } from './KnowledgeBreakdown'
import { LearningModesPanel } from './LearningModesPanel'
import { TutorPanel } from './TutorPanel'
import { RevisionPanel } from './RevisionPanel'
import { ErrorMessage } from '../../components/ui/ErrorMessage'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'
import { useAuthStore } from '../../store/authStore'
import { analyzeText, analyzeFile } from '../../api/analysis'
import { createSession } from '../../api/sessions'

type ContentTab = 'breakdown' | 'learning' | 'tutor' | 'revision'

export function InputPanel() {
  const [text, setText] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<ContentTab>('breakdown')
  const { currentSession, setCurrentSession, addTopic, addExplanations, addQuizQuestions } =
    useSessionStore()
  const { isLoading, setLoading } = useUIStore()
  const { user } = useAuthStore()

  const ensureSession = async () => {
    if (currentSession) return currentSession
    const { session_id } = await createSession()
    const newSession = {
      id: session_id,
      user_id: user?.id ?? '',
      previous_id: null,
      topics: [],
      explanations: [],
      quiz_questions: [],
      interactions: [],
      created_at: new Date().toISOString(),
      last_active: new Date().toISOString(),
    }
    setCurrentSession(newSession)
    return newSession
  }

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setLocalError('Please enter some text to analyze.')
      return
    }
    setLocalError(null)
    setLoading(true)
    try {
      const session = await ensureSession()
      const result = await analyzeText(session.id, text)
      if (result.topic) addTopic(result.topic)
      if (result.explanations) addExplanations(result.explanations)
      if (result.quiz_questions) addQuizQuestions(result.quiz_questions)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Analysis failed.'
      setLocalError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = async (file: File) => {
    setLocalError(null)
    setLoading(true)
    try {
      const session = await ensureSession()
      const result = await analyzeFile(session.id, file)
      if (result.topic) addTopic(result.topic)
      if (result.explanations) addExplanations(result.explanations)
      if (result.quiz_questions) addQuizQuestions(result.quiz_questions)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'File analysis failed.'
      setLocalError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full p-6 overflow-y-auto bg-white dark:bg-slate-950 transition-colors">
      <InputSourceHeader
        onFileSelect={handleFileSelect}
        onUrlClick={() => {}}
      />
      <TextInputArea value={text} onChange={setText} disabled={isLoading} />
      {localError && <ErrorMessage message={localError} onRetry={handleAnalyze} />}
      <AnalyzeButton onClick={handleAnalyze} loading={isLoading} />

      {/* Content tabs */}
      <div className="mt-6 border-b border-gray-200 dark:border-slate-800 transition-colors">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('breakdown')}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'breakdown'
                ? 'border-purple-600 text-purple-700 dark:border-primary-500 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-300'
            }`}
          >
            Knowledge Breakdown
          </button>
          <button
            onClick={() => setActiveTab('learning')}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'learning'
                ? 'border-purple-600 text-purple-700 dark:border-primary-500 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-300'
            }`}
          >
            Learning Modes
          </button>
          <button
            onClick={() => setActiveTab('tutor')}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'tutor'
                ? 'border-purple-600 text-purple-700 dark:border-primary-500 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-300'
            }`}
          >
            Interactive Tutor
          </button>
          <button
            onClick={() => setActiveTab('revision')}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'revision'
                ? 'border-purple-600 text-purple-700 dark:border-primary-500 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-300'
            }`}
          >
            Revision Hub
          </button>
        </div>
      </div>

      {/* Active tab content */}
      <div className="mt-6 flex-1 min-h-0">
        {activeTab === 'breakdown' && <KnowledgeBreakdown />}
        {activeTab === 'learning' && <LearningModesPanel />}
        {activeTab === 'tutor' && <TutorPanel />}
        {activeTab === 'revision' && <RevisionPanel />}
      </div>
    </div>
  )
}
