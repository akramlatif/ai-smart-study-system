import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css' // We'll use the dark theme for code blocks by default since it looks good in both modes

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div
      className={`prose prose-sm md:prose-base dark:prose-invert max-w-none 
      prose-headings:font-semibold prose-headings:text-gray-900 dark:prose-headings:text-slate-100
      prose-p:text-gray-700 dark:prose-p:text-slate-300
      prose-a:text-primary-600 dark:prose-a:text-primary-400
      prose-strong:text-gray-900 dark:prose-strong:text-slate-200
      prose-code:text-pink-500 dark:prose-code:text-pink-400
      prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-800
      prose-li:marker:text-gray-400 dark:prose-li:marker:text-slate-500
      prose-table:border-collapse prose-td:border prose-td:border-gray-200 dark:prose-td:border-slate-700 prose-th:border prose-th:border-gray-200 dark:prose-th:border-slate-700
      transition-colors ${className}`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
