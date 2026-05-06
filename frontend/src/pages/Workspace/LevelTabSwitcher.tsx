import React from 'react'
import clsx from 'clsx'
import { useUIStore } from '../../store/uiStore'

const levels = [
  { key: 'basic' as const, label: 'Basic' },
  { key: 'intermediate' as const, label: 'Intermediate' },
  { key: 'advanced' as const, label: 'Advanced' },
]

export function LevelTabSwitcher() {
  const { activeExplanationLevel, setActiveExplanationLevel } = useUIStore()

  return (
    <div className="flex gap-1 p-1 bg-gray-100 rounded-lg w-fit mb-4">
      {levels.map(({ key, label }) => (
        <button
          key={key}
          onClick={() => setActiveExplanationLevel(key)}
          className={clsx(
            'px-4 py-1.5 rounded-md text-sm font-medium transition-all',
            activeExplanationLevel === key
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          )}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
