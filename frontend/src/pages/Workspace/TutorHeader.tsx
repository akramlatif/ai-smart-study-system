import React from 'react'
import { Bot } from 'lucide-react'

export function TutorHeader() {
  return (
    <div className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-slate-800 bg-white dark:bg-slate-950 transition-colors">
      <div className="h-10 w-10 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
        <Bot className="h-5 w-5 text-primary-600 dark:text-primary-400" />
      </div>
      <div>
        <h3 className="font-semibold text-gray-900 dark:text-slate-100 text-sm">Quantum Tutor</h3>
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 bg-green-500 rounded-full" />
          <span className="text-xs text-green-600">Online &amp; Listening</span>
        </div>
      </div>
    </div>
  )
}
