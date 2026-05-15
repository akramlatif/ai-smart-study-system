import React from 'react'
import clsx from 'clsx'
import { Check, Circle, CircleDot } from 'lucide-react'

interface TutorProgressBarProps {
  subtopics: { name: string }[]
  currentIndex: number
  isComplete: boolean
}

export function TutorProgressBar({ subtopics, currentIndex, isComplete }: TutorProgressBarProps) {
  return (
    <div className="w-full py-4 px-2">
      <div className="relative flex items-center justify-between">
        {/* Connecting Line */}
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-gray-200 rounded" />
        <div
          className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-primary-500 rounded transition-all duration-300"
          style={{ width: `${(Math.min(currentIndex, subtopics.length - 1) / Math.max(subtopics.length - 1, 1)) * 100}%` }}
        />

        {/* Steps */}
        {subtopics.map((sub, idx) => {
          const isPast = idx < currentIndex || isComplete
          const isCurrent = idx === currentIndex && !isComplete
          const isFuture = idx > currentIndex && !isComplete

          return (
            <div key={idx} className="relative z-10 flex flex-col items-center group">
              <div
                className={clsx(
                  'w-6 h-6 rounded-full flex items-center justify-center bg-white border-2 transition-colors',
                  {
                    'border-primary-500 text-primary-500': isPast,
                    'border-primary-600 text-primary-600 bg-primary-50': isCurrent,
                    'border-gray-300 text-gray-300': isFuture,
                  }
                )}
                title={sub.name}
              >
                {isPast ? (
                  <Check className="w-4 h-4" />
                ) : isCurrent ? (
                  <CircleDot className="w-4 h-4" />
                ) : (
                  <Circle className="w-3 h-3" />
                )}
              </div>
              
              {/* Tooltip on hover */}
              <div className="absolute top-8 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 text-white text-xs py-1 px-2 rounded whitespace-nowrap pointer-events-none z-20">
                {sub.name}
              </div>
            </div>
          )
        })}
      </div>
      <div className="mt-4 flex justify-between items-end">
        <div>
          <p className="text-sm font-medium text-primary-700">
            {isComplete ? 'Session Complete' : `Step ${currentIndex + 1} of ${subtopics.length}`}
          </p>
          <p className="text-xs text-gray-500">
            {isComplete ? 'Great job!' : subtopics[currentIndex]?.name}
          </p>
        </div>
      </div>
    </div>
  )
}
