import React from 'react'
import { MarkdownRenderer } from '../../components/ui/MarkdownRenderer'

interface AIMessageProps {
  content: string
}

export function AIMessage({ content }: AIMessageProps) {
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[85%] lg:max-w-md bg-gray-100 dark:bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 transition-colors">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  )
}
