import React from 'react'
import { AnswerOption } from './AnswerOption'
import type { AnswerOption as AnswerOptionType } from '../../types'

interface AnswerOptionListProps {
  options: AnswerOptionType[]
  selectedLabel: string | null
  revealed: boolean
  onSelect: (label: string) => void
}

export function AnswerOptionList({
  options,
  selectedLabel,
  revealed,
  onSelect,
}: AnswerOptionListProps) {
  return (
    <div className="flex flex-col gap-3">
      {options.map((option) => (
        <AnswerOption
          key={option.label}
          option={option}
          selected={selectedLabel === option.label}
          revealed={revealed}
          onSelect={() => onSelect(option.label)}
        />
      ))}
    </div>
  )
}
