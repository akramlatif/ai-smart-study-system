import React from 'react'
import { ArrowRight } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { useUIStore } from '../../store/uiStore'
import { useSessionStore } from '../../store/sessionStore'

export function NextQuestionButton() {
  const { currentQuizIndex, nextQuizQuestion } = useUIStore()
  const { quizQuestions } = useSessionStore()
  const isLast = currentQuizIndex >= quizQuestions.length - 1

  if (isLast) return null

  return (
    <Button
      variant="primary"
      size="md"
      onClick={() => nextQuizQuestion(quizQuestions.length)}
      className="mt-4"
    >
      Next Question
      <ArrowRight className="h-4 w-4" />
    </Button>
  )
}
