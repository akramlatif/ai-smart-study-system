import React from 'react'
import { Sparkles } from 'lucide-react'

export function LoadingIndicator() {
  return (
    <div className="flex items-center gap-2 px-4 py-2 text-gray-500">
      <Sparkles className="h-4 w-4 animate-spin text-primary-500" />
      <span className="text-sm italic">Synthesizing formulas...</span>
    </div>
  )
}
