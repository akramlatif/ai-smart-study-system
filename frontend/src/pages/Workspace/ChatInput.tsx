import React, { useState } from 'react'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage('')
    }
  }

  return (
    <div className="p-4 bg-white dark:bg-slate-950 border-t border-gray-200 dark:border-slate-800 transition-colors">
      <form onSubmit={handleSubmit} className="flex gap-2 relative">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={disabled}
          placeholder="Ask a follow-up question..."
          className="flex-1 px-4 py-2 bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500 disabled:opacity-50 transition-colors"
        />
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="h-10 w-10 bg-primary-600 text-white rounded-xl flex items-center justify-center hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  )
}
