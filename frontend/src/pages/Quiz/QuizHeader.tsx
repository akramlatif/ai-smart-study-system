import React from 'react'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'

export function QuizHeader() {
  const { topics, quizQuestions } = useSessionStore()
  const { currentQuizIndex } = useUIStore()
  const topicName = topics[topics.length - 1]?.main_topic ?? 'Quiz'

  return (
    <div className="mb-6">
      <p className="text-sm text-primary-600 font-medium mb-1">{topicName}</p>
      <h2 className="text-xl font-bold text-gray-900">
        Question {currentQuizIndex + 1} of {quizQuestions.length}
      </h2>
    </div>
  )
}
