import React from 'react'

interface UserMessageProps {
  content: string
}

export function UserMessage({ content }: UserMessageProps) {
  return (
    <div className="flex justify-end mb-4">
      <div className="max-w-[85%] lg:max-w-md bg-primary-600 dark:bg-primary-700 rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm transition-colors">
        <p className="text-sm text-white leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  )
}
