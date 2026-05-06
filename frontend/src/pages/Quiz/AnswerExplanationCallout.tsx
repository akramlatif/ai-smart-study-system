import React from 'react'
import { Info } from 'lucide-react'

interface AnswerExplanationCalloutProps {
  explanation: string
}

export function AnswerExplanationCallout({ explanation }: AnswerExplanationCalloutProps) {
  return (
    <div className="flex gap-3 p-4 bg-blue-50 border-l-4 border-blue-400 rounded-r-lg mt-4">
      <Info className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
      <p className="text-sm text-blue-800 leading-relaxed">{explanation}</p>
    </div>
  )
}
