import React, { useState } from 'react'
import { QuizHeader } from './QuizHeader'
import { QuestionDisplay } from './QuestionDisplay'
import { AnswerOptionList } from './AnswerOptionList'
import { AnswerExplanationCallout } from './AnswerExplanationCallout'
import { SaveForReviewButton } from './SaveForReviewButton'
import { NextQuestionButton } from './NextQuestionButton'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'

export function QuizPage() {
  const { quizQuestions } = useSessionStore()
  const { currentQuizIndex, setCurrentQuizIndex } = useUIStore()
  const [selectedLabel, setSelectedLabel] = useState<string | null>(null)
  const [textAnswer, setTextAnswer] = useState('')
  const [revealed, setRevealed] = useState(false)

  const question = quizQuestions[currentQuizIndex]

  const handleSelect = (label: string) => {
    if (revealed) return
    setSelectedLabel(label)
    setRevealed(true)
  }

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!textAnswer.trim() || revealed) return
    setRevealed(true)
  }

  const handleNext = () => {
    setSelectedLabel(null)
    setTextAnswer('')
    setRevealed(false)
    setCurrentQuizIndex(currentQuizIndex + 1)
  }

  if (quizQuestions.length === 0) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="text-center py-16">
          <p className="text-gray-400 dark:text-slate-500 text-lg">No quiz questions yet.</p>
          <p className="text-gray-400 dark:text-slate-500 text-sm mt-2">
            Analyze some content in the Workspace to generate quiz questions.
          </p>
        </div>
      </div>
    )
  }

  if (!question) return null

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <QuizHeader />
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
              disabled={revealed}
              placeholder="Type your answer..."
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500 bg-white dark:bg-slate-800 dark:text-slate-100 dark:disabled:bg-slate-900 transition-colors"
            />
            {!revealed && (
              <button
                type="submit"
                disabled={!textAnswer.trim()}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
              >
                Check
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

      <div className="flex items-center justify-between mt-4">
        <SaveForReviewButton
          questionId={question.id}
          isSaved={question.saved_for_review}
        />
        <NextQuestionButton />
      </div>
    </div>
  )
}
