import React, { useState } from 'react'
import { Lightbulb } from 'lucide-react'
import { Badge } from '../../components/ui/Badge'
import type { QuizQuestion } from '../../types'

interface QuestionDisplayProps {
  question: QuizQuestion
}

export function QuestionDisplay({ question }: QuestionDisplayProps) {
  const [showHint, setShowHint] = useState(false)

  // Reset hint state when question changes
  React.useEffect(() => {
    setShowHint(false)
  }, [question.id])

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Badge variant={question.difficulty as 'easy' | 'medium' | 'hard'}>
            {question.difficulty}
          </Badge>
          <span className="text-xs text-gray-400 capitalize">{question.question_type.replace('_', ' ')}</span>
        </div>
        {question.hint && (
          <button
            onClick={() => setShowHint(!showHint)}
            className="flex items-center gap-1 text-sm text-yellow-600 hover:text-yellow-700 transition-colors"
          >
            <Lightbulb className="w-4 h-4" />
            {showHint ? 'Hide Hint' : 'Show Hint'}
          </button>
        )}
      </div>
      <p className="text-lg font-medium text-gray-900 dark:text-slate-100 leading-relaxed mb-3">{question.question_text}</p>
      
      {showHint && question.hint && (
        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-800 rounded-lg text-sm text-yellow-800 dark:text-yellow-300 flex gap-2">
          <Lightbulb className="w-4 h-4 flex-shrink-0 mt-0.5 text-yellow-600" />
          <p>{question.hint}</p>
        </div>
      )}
    </div>
  )
}
