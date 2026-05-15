import React from 'react'
import type { SocraticComplete } from '../../types'

interface SocraticCompletionCardProps {
  completion: SocraticComplete
  onStartNew: () => void
}

export function SocraticCompletionCard({
  completion,
  onStartNew,
}: SocraticCompletionCardProps) {
  return (
    <div className="mt-4 rounded-xl border border-blue-100 bg-white shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-blue-50 px-5 py-3 flex items-center gap-2">
        <span className="text-2xl">🎓</span>
        <div>
          <h4 className="font-semibold text-gray-900 text-base">Session Complete</h4>
          <p className="text-xs text-gray-500">
            Depth reached: Level {completion.depth_reached} of 5
          </p>
        </div>
      </div>

      <div className="px-5 py-4 space-y-4">
        {/* Summary */}
        <div>
          <h5 className="text-sm font-semibold text-gray-700 mb-2">Summary</h5>
          <p className="text-sm text-gray-700 leading-relaxed">{completion.summary}</p>
        </div>

        {/* Key insights */}
        <div>
          <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1.5">
            <span>💡</span> Key Insights
          </h5>
          <ol className="space-y-2">
            {completion.key_insights.map((insight, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-gray-700">
                <span className="font-semibold text-blue-600 shrink-0">{i + 1}.</span>
                <span>{insight}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Start new button */}
        <button
          onClick={onStartNew}
          className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 transition-colors"
        >
          Start New Socratic Session
        </button>
      </div>
    </div>
  )
}
