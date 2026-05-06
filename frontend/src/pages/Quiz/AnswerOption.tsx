import React from 'react'
import clsx from 'clsx'
import { Check, X } from 'lucide-react'
import type { AnswerOption as AnswerOptionType } from '../../types'

interface AnswerOptionProps {
  option: AnswerOptionType
  selected: boolean
  revealed: boolean
  onSelect: () => void
}

export function AnswerOption({ option, selected, revealed, onSelect }: AnswerOptionProps) {
  const isCorrect = option.is_correct
  const showCorrect = revealed && isCorrect
  const showWrong = revealed && selected && !isCorrect

  return (
    <button
      onClick={onSelect}
      disabled={revealed}
      className={clsx(
        'w-full flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all',
        !revealed && 'hover:border-primary-300 hover:bg-primary-50',
        !revealed && selected && 'border-primary-500 bg-primary-50',
        !revealed && !selected && 'border-gray-200 bg-white',
        showCorrect && 'border-cyan-500 bg-cyan-500 text-white',
        showWrong && 'border-red-400 bg-red-50',
        revealed && !selected && !isCorrect && 'border-gray-200 bg-gray-50 opacity-60'
      )}
    >
      <span
        className={clsx(
          'h-8 w-8 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0',
          showCorrect ? 'bg-white text-cyan-600' : 'bg-gray-100 text-gray-700',
          showWrong && 'bg-red-100 text-red-600'
        )}
      >
        {option.label}
      </span>
      <span className="flex-1 text-sm">{option.text}</span>
      {showCorrect && <Check className="h-5 w-5 flex-shrink-0" />}
      {showWrong && <X className="h-5 w-5 text-red-500 flex-shrink-0" />}
    </button>
  )
}
