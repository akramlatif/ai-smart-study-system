import React, { useState } from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { submitFeynmanExplanation } from '../../api/learningModes'
import { FeedbackCard } from './FeedbackCard'

const MIN_LENGTH = 50
const MAX_LENGTH = 5000

export function FeynmanPanel() {
  const [explanation, setExplanation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { currentSession, topics, feynmanFeedback, setFeynmanFeedback } = useSessionStore()
  const currentTopic = topics.length > 0 ? topics[topics.length - 1] : null

  const charCount = explanation.length
  const isValid = charCount >= MIN_LENGTH && charCount <= MAX_LENGTH

  const handleSubmit = async () => {
    if (!currentSession || !isValid) return
    setError(null)
    setLoading(true)
    try {
      const result = await submitFeynmanExplanation(currentSession.id, explanation)
      setFeynmanFeedback(result.feedback)
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Failed to evaluate explanation.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-xl bg-purple-50/40 border border-purple-100 p-5">
      {/* Topic display */}
      <div className="mb-4">
        {currentTopic ? (
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-purple-600 uppercase tracking-wide">
              Current Topic
            </span>
            <span className="text-sm font-semibold text-gray-800 bg-white border border-purple-200 rounded-full px-3 py-0.5">
              {currentTopic.main_topic}
            </span>
          </div>
        ) : (
          <p className="text-sm text-gray-500 italic">
            No topic yet — analyze some content first to get started.
          </p>
        )}
      </div>

      {/* Explanation textarea */}
      <div className="mb-3">
        <label
          htmlFor="feynman-explanation"
          className="block text-sm font-medium text-gray-700 mb-1.5"
        >
          {currentTopic
            ? `Explain "${currentTopic.main_topic}" in your own words, as if teaching it to someone who has never heard of it...`
            : 'Explain the topic in your own words, as if teaching it to someone who has never heard of it...'}
        </label>
        <textarea
          id="feynman-explanation"
          value={explanation}
          onChange={(e) => setExplanation(e.target.value)}
          disabled={loading || !currentTopic}
          rows={7}
          maxLength={MAX_LENGTH}
          placeholder="Start explaining here. Don't worry about being perfect — just write what you understand..."
          className="w-full rounded-lg border border-purple-200 bg-white px-3 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed"
        />
        {/* Character counter */}
        <div className="flex justify-between items-center mt-1">
          <span
            className={`text-xs ${
              charCount < MIN_LENGTH
                ? 'text-gray-400'
                : charCount > MAX_LENGTH
                ? 'text-red-500'
                : 'text-green-600'
            }`}
          >
            {charCount < MIN_LENGTH
              ? `${MIN_LENGTH - charCount} more characters needed`
              : `${charCount} / ${MAX_LENGTH}`}
          </span>
          {charCount > 0 && charCount < MIN_LENGTH && (
            <span className="text-xs text-gray-400">Minimum {MIN_LENGTH} characters</span>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-3 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={loading || !isValid || !currentTopic}
        className="w-full rounded-lg bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300 disabled:cursor-not-allowed text-white font-medium text-sm py-2.5 transition-colors flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Evaluating...
          </>
        ) : (
          'Evaluate My Understanding'
        )}
      </button>

      {/* Feedback card */}
      {feynmanFeedback && <FeedbackCard feedback={feynmanFeedback} />}
    </div>
  )
}
