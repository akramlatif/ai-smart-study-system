import React, { useEffect, useState } from 'react'
import { reviewApi } from '../../api/review'
import { quizApi } from '../../api/quiz'
import { ReviewItem } from '../../types'
import { QuestionDisplay } from '../Quiz/QuestionDisplay'
import { AnswerOptionList } from '../Quiz/AnswerOptionList'
import { AnswerExplanationCallout } from '../Quiz/AnswerExplanationCallout'
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react'

export function ReviewPage() {
  const [queue, setQueue] = useState<ReviewItem[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [selectedLabel, setSelectedLabel] = useState<string | null>(null)
  const [textAnswer, setTextAnswer] = useState('')
  const [revealed, setRevealed] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    loadQueue()
  }, [])

  const loadQueue = async () => {
    try {
      setLoading(true)
      const data = await reviewApi.getReviewQueue()
      setQueue(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load review queue')
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = async (label: string) => {
    if (revealed || isSubmitting) return
    setSelectedLabel(label)
    await submitAnswer(label)
  }

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!textAnswer.trim() || revealed || isSubmitting) return
    await submitAnswer(textAnswer)
  }

  const submitAnswer = async (answer: string) => {
    try {
      setIsSubmitting(true)
      const item = queue[currentIndex]
      
      // Submit to backend - this creates a new QuestionAttempt and updates SM-2 timing automatically
      if (item.question) {
        await quizApi.submitAnswer(item.session_id, item.question.id, { answer })
      }
      
      setRevealed(true)
    } catch (err) {
      console.error('Failed to submit answer', err)
      // For now, even if it fails, we show the correct answer
      setRevealed(true)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleNext = () => {
    setSelectedLabel(null)
    setTextAnswer('')
    setRevealed(false)
    setCurrentIndex(currentIndex + 1)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-xl flex gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      </div>
    )
  }

  if (queue.length === 0 || currentIndex >= queue.length) {
    return (
      <div className="p-6 max-w-2xl mx-auto text-center mt-12">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2">You're all caught up!</h2>
        <p className="text-gray-500 dark:text-slate-400">
          You have reviewed all due items. Take a break or study new topics!
        </p>
      </div>
    )
  }

  const item = queue[currentIndex]
  const question = item.question
  
  // If this item has no question attached, just skip it (failsafe)
  if (!question) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <p>Invalid review item. <button onClick={handleNext} className="text-primary-500 underline">Skip</button></p>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6 pb-6 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400">
          <Clock className="w-5 h-5" />
          <h1 className="text-xl font-bold">Spaced Repetition Review</h1>
        </div>
        <div className="text-sm font-medium text-gray-500 dark:text-slate-400">
          {currentIndex + 1} of {queue.length}
        </div>
      </div>

      <QuestionDisplay question={question} />

      {['multiple_choice', 'true_false'].includes(question.question_type) && question.options ? (
        <AnswerOptionList
          options={question.options}
          selectedLabel={selectedLabel}
          revealed={revealed}
          onSelect={handleSelect}
        />
      ) : (
        <form onSubmit={handleTextSubmit} className="space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={textAnswer}
              onChange={(e) => setTextAnswer(e.target.value)}
              disabled={revealed || isSubmitting}
              placeholder="Type your answer..."
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500 bg-white dark:bg-slate-800 dark:text-slate-100 dark:disabled:bg-slate-900 transition-colors"
            />
            {!revealed && (
              <button
                type="submit"
                disabled={!textAnswer.trim() || isSubmitting}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
              >
                {isSubmitting ? 'Checking...' : 'Check'}
              </button>
            )}
          </div>
          
          {revealed && (
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
              <p className="text-sm text-green-800 dark:text-green-400 font-medium mb-1">Correct Answer:</p>
              <p className="text-gray-900 dark:text-slate-100">{question.correct_answer}</p>
            </div>
          )}
        </form>
      )}

      {revealed && question.explanation && (
        <AnswerExplanationCallout explanation={question.explanation} />
      )}

      {revealed && (
        <div className="flex justify-end mt-6">
          <button
            onClick={handleNext}
            className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium transition-colors"
          >
            {currentIndex === queue.length - 1 ? 'Finish Review' : 'Next Question'}
          </button>
        </div>
      )}
    </div>
  )
}
