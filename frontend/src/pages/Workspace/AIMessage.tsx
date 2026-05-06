import React from 'react'

interface AIMessageProps {
  content: string
}

export function AIMessage({ content }: AIMessageProps) {
  return (
    <div className="flex justify-start mb-3">
      <div className="max-w-xs lg:max-w-sm bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-2.5">
        <p className="text-sm text-gray-700 leading-relaxed">{content}</p>
      </div>
    </div>
  )
}
