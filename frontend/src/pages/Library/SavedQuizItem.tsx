import React from 'react'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import type { QuizQuestion } from '../../types'

interface SavedQuizItemProps {
  question: QuizQuestion
}

export function SavedQuizItem({ question }: SavedQuizItemProps) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-2 mb-2">
        <p className="text-sm font-medium text-gray-800 flex-1">{question.question_text}</p>
        <Badge variant={question.difficulty as 'easy' | 'medium' | 'hard'}>
          {question.difficulty}
        </Badge>
      </div>
      <p className="text-xs text-gray-500">
        <span className="font-medium">Answer:</span> {question.correct_answer}
      </p>
    </Card>
  )
}
