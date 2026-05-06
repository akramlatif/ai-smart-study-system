import React from 'react'
import { Badge } from '../../components/ui/Badge'
import type { QuizQuestion } from '../../types'

interface QuestionDisplayProps {
  question: QuizQuestion
}

export function QuestionDisplay({ question }: QuestionDisplayProps) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Badge variant={question.difficulty as 'easy' | 'medium' | 'hard'}>
          {question.difficulty}
        </Badge>
        <span className="text-xs text-gray-400 capitalize">{question.question_type.replace('_', ' ')}</span>
      </div>
      <p className="text-lg font-medium text-gray-900 leading-relaxed">{question.question_text}</p>
    </div>
  )
}
