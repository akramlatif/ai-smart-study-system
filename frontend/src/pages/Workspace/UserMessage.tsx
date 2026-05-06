import React from 'react'

interface UserMessageProps {
  content: string
}

export function UserMessage({ content }: UserMessageProps) {
  return (
    <div className="flex justify-end mb-3">
      <div className="max-w-xs lg:max-w-sm bg-primary-600 rounded-2xl rounded-tr-sm px-4 py-2.5">
        <p className="text-sm text-white leading-relaxed">{content}</p>
      </div>
    </div>
  )
}
