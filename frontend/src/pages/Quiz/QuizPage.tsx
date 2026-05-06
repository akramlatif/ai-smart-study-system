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
  const [revealed, setRevealed] = useState(false)

  const question = quizQuestions[currentQuizIndex]

  const handleSelect = (label: string) => {
    if (revealed) return
    setSelectedLabel(label)
    setRevealed(true)
  }

  const handleNext = () => {
    setSelectedLabel(null)
    setRevealed(false)
    setCurrentQuizIndex(currentQuizIndex + 1)
  }

  if (quizQuestions.length === 0) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="text-center py-16">
          <p className="text-gray-400 text-lg">No quiz questions yet.</p>
          <p className="text-gray-400 text-sm mt-2">
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

      {question.question_type === 'multiple_choice' && question.options ? (
        <AnswerOptionList
          options={question.options}
          selectedLabel={selectedLabel}
          revealed={revealed}
          onSelect={handleSelect}
        />
      ) : (
        <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
          <p className="text-sm text-gray-500 italic">Short answer question</p>
          <p className="text-sm font-medium text-gray-800 mt-2">
            Answer: {question.correct_answer}
          </p>
        </div>
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
