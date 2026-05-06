import React from 'react'

interface TextInputAreaProps {
  value: string
  onChange: (value: string) => void
  disabled?: boolean
}

export function TextInputArea({ value, onChange, disabled }: TextInputAreaProps) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      placeholder="Paste your notes, essay, or raw text here..."
      className="w-full h-48 px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent placeholder-gray-400 bg-white"
    />
  )
}
