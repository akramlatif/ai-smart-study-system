import React, { useState } from 'react'
import { useSessionStore } from '../../store/sessionStore'
import {
  startSocraticSession,
  respondToSocratic,
} from '../../api/learningModes'
import { SocraticCompletionCard } from './SocraticCompletionCard'
import type { SocraticQuestion } from '../../types'

const MIN_ANSWER_LENGTH = 10
const MAX_ANSWER_LENGTH = 2000

function DepthIndicator({ current }: { current: number }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-xs font-medium text-gray-600 mr-1">Depth:</span>
      {[1, 2, 3, 4, 5].map((level) => (
        <div
          key={level}
          className={`w-2.5 h-2.5 rounded-full ${
            level <= current ? 'bg-purple-600' : 'bg-gray-300'
          }`}
          title={`Level ${level}`}
        />
      ))}
    </div>
  )
}

function QuestionTypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    probing: 'bg-purple-100 text-purple-700 border-purple-200',
    clarifying: 'bg-blue-100 text-blue-700 border-blue-200',
    hypothetical: 'bg-orange-100 text-orange-700 border-orange-200',
    evaluative: 'bg-teal-100 text-teal-700 border-teal-200',
  }
  return (
    <span
      className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full border ${
        colors[type] || 'bg-gray-100 text-gray-700 border-gray-200'
      }`}
    >
      {type}
    </span>
  )
}

function QuestionDisplay({ question }: { question: SocraticQuestion }) {
  return (
    <div className="rounded-lg bg-blue-50 border border-blue-200 px-4 py-3">
      <div className="flex items-center justify-between mb-2">
        <QuestionTypeBadge type={question.question_type} />
        <DepthIndicator current={question.depth_level} />
      </div>
      <p className="text-sm text-gray-800 leading-relaxed font-medium">
        {question.question_text}
      </p>
    </div>
  )
}

function QuestionChainHistory({
  chain,
}: {
  chain: Array<{ question: SocraticQuestion; answer?: string; index: number }>
}) {
  const [expanded, setExpanded] = useState(false)

  if (chain.length === 0) return null

  return (
    <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 transition-colors"
        aria-expanded={expanded}
      >
        <span>Question History ({chain.length})</span>
        <span className="text-gray-400">{expanded ? '▲' : '▼'}</span>
      </button>
      {expanded && (
        <div className="px-4 py-3 space-y-3 bg-white max-h-64 overflow-y-auto">
          {chain.map((item) => (
            <div key={item.index} className="border-l-2 border-blue-300 pl-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-gray-500">Q{item.index}</span>
                <QuestionTypeBadge type={item.question.question_type} />
              </div>
              <p className="text-xs text-gray-700 mb-1.5">{item.question.question_text}</p>
              {item.answer && (
                <p className="text-xs text-gray-600 italic bg-gray-50 rounded px-2 py-1">
                  Your answer: {item.answer}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function SocraticPanel() {
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    currentSession,
    topics,
    socraticSessionId,
    currentSocraticQuestion,
    socraticChain,
    socraticComplete,
    setSocraticSession,
    addSocraticQA,
    completeSocratic,
    resetSocratic,
  } = useSessionStore()

  const currentTopic = topics.length > 0 ? topics[topics.length - 1] : null

  const charCount = answer.length
  const isValidAnswer =
    charCount >= MIN_ANSWER_LENGTH && charCount <= MAX_ANSWER_LENGTH

  const handleStart = async () => {
    if (!currentSession) return
    setError(null)
    setLoading(true)
    try {
      const result = await startSocraticSession(currentSession.id)
      setSocraticSession(result.socratic_session_id, result.question)
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Failed to start Socratic session.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitAnswer = async () => {
    if (!currentSession || !socraticSessionId || !isValidAnswer) return
    setError(null)
    setLoading(true)
    try {
      // Add current Q&A to chain before submitting
      if (currentSocraticQuestion) {
        addSocraticQA({
          question_index: socraticChain.length + 1,
          question: currentSocraticQuestion,
          student_answer: answer,
        })
      }

      const result = await respondToSocratic(
        currentSession.id,
        socraticSessionId,
        answer,
      )

      if (result.is_complete && result.completion) {
        completeSocratic(result.completion)
      } else if (result.question) {
        setSocraticSession(socraticSessionId, result.question)
      }

      setAnswer('')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit answer.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleStartNew = () => {
    resetSocratic()
    setAnswer('')
    setError(null)
    handleStart()
  }

  // If session is complete, show completion card
  if (socraticComplete) {
    return (
      <div className="rounded-xl bg-blue-50/40 border border-blue-100 p-5">
        <SocraticCompletionCard
          completion={socraticComplete}
          onStartNew={handleStartNew}
        />
      </div>
    )
  }

  return (
    <div className="rounded-xl bg-blue-50/40 border border-blue-100 p-5">
      {/* Topic display */}
      <div className="mb-4">
        {currentTopic ? (
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-blue-600 uppercase tracking-wide">
              Current Topic
            </span>
            <span className="text-sm font-semibold text-gray-800 bg-white border border-blue-200 rounded-full px-3 py-0.5">
              {currentTopic.main_topic}
            </span>
          </div>
        ) : (
          <p className="text-sm text-gray-500 italic">
            No topic yet — analyze some content first to get started.
          </p>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-3 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Not started yet */}
      {!socraticSessionId && (
        <button
          onClick={handleStart}
          disabled={loading || !currentTopic}
          className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed text-white font-medium text-sm py-2.5 transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8H4z"
                />
              </svg>
              Starting...
            </>
          ) : (
            'Start Socratic Session'
          )}
        </button>
      )}

      {/* Session in progress */}
      {socraticSessionId && currentSocraticQuestion && (
        <>
          {/* Current question */}
          <QuestionDisplay question={currentSocraticQuestion} />

          {/* Answer textarea */}
          <div className="mt-4">
            <label
              htmlFor="socratic-answer"
              className="block text-sm font-medium text-gray-700 mb-1.5"
            >
              Your Answer
            </label>
            <textarea
              id="socratic-answer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              disabled={loading}
              rows={4}
              maxLength={MAX_ANSWER_LENGTH}
              placeholder="Think carefully and share your thoughts..."
              className="w-full rounded-lg border border-blue-200 bg-white px-3 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <div className="flex justify-between items-center mt-1">
              <span
                className={`text-xs ${
                  charCount < MIN_ANSWER_LENGTH
                    ? 'text-gray-400'
                    : charCount > MAX_ANSWER_LENGTH
                    ? 'text-red-500'
                    : 'text-green-600'
                }`}
              >
                {charCount < MIN_ANSWER_LENGTH
                  ? `${MIN_ANSWER_LENGTH - charCount} more characters needed`
                  : `${charCount} / ${MAX_ANSWER_LENGTH}`}
              </span>
            </div>
          </div>

          {/* Submit button */}
          <button
            onClick={handleSubmitAnswer}
            disabled={loading || !isValidAnswer}
            className="w-full mt-3 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed text-white font-medium text-sm py-2.5 transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8H4z"
                  />
                </svg>
                Submitting...
              </>
            ) : (
              'Submit Answer'
            )}
          </button>

          {/* Question chain history */}
          <QuestionChainHistory
            chain={socraticChain.map((pair) => ({
              question: pair.question,
              answer: pair.student_answer,
              index: pair.question_index,
            }))}
          />
        </>
      )}
    </div>
  )
}
