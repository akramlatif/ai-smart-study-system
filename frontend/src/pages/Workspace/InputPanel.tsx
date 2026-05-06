import React, { useState } from 'react'
import { InputSourceHeader } from './InputSourceHeader'
import { TextInputArea } from './TextInputArea'
import { AnalyzeButton } from './AnalyzeButton'
import { KnowledgeBreakdown } from './KnowledgeBreakdown'
import { ErrorMessage } from '../../components/ui/ErrorMessage'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'
import { useAuthStore } from '../../store/authStore'
import { analyzeText, analyzeFile } from '../../api/analysis'
import { createSession } from '../../api/sessions'

export function InputPanel() {
  const [text, setText] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)
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
    <div className="flex flex-col h-full p-6 overflow-y-auto">
      <InputSourceHeader
        onFileSelect={handleFileSelect}
        onUrlClick={() => {}}
      />
      <TextInputArea value={text} onChange={setText} disabled={isLoading} />
      {localError && <ErrorMessage message={localError} onRetry={handleAnalyze} />}
      <AnalyzeButton onClick={handleAnalyze} loading={isLoading} />
      <KnowledgeBreakdown />
    </div>
  )
}
