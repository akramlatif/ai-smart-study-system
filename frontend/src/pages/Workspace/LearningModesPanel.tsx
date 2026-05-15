import React, { useState } from 'react'
import { FeynmanPanel } from './FeynmanPanel'
import { SocraticPanel } from './SocraticPanel'

type Mode = 'feynman' | 'socratic'

export function LearningModesPanel() {
  const [mode, setMode] = useState<Mode>('feynman')

  return (
    <div className="mt-6">
      <h3 className="font-semibold text-gray-900 mb-3">Learning Modes</h3>

      {/* Mode selector toggle */}
      <div className="flex rounded-lg border border-gray-200 bg-gray-100 p-1 mb-4 w-fit">
        <button
          onClick={() => setMode('feynman')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            mode === 'feynman'
              ? 'bg-white text-purple-700 shadow-sm border border-purple-200'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Feynman Technique
        </button>
        <button
          onClick={() => setMode('socratic')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            mode === 'socratic'
              ? 'bg-white text-blue-700 shadow-sm border border-blue-200'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Socratic Method
        </button>
      </div>

      {/* Mode descriptions */}
      {mode === 'feynman' && (
        <p className="text-xs text-gray-500 mb-3">
          Explain the topic in your own words. Get scored feedback on your understanding.
        </p>
      )}
      {mode === 'socratic' && (
        <p className="text-xs text-gray-500 mb-3">
          Explore the topic through guided questions. Deepen your understanding step by step.
        </p>
      )}

      {/* Active panel */}
      {mode === 'feynman' ? <FeynmanPanel /> : <SocraticPanel />}
    </div>
  )
}
