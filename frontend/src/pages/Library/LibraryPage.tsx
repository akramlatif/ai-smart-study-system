import React from 'react'
import { SessionHistoryList } from './SessionHistoryList'
import { SavedQuizList } from './SavedQuizList'

export function LibraryPage() {
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Library</h1>
      <div className="grid grid-cols-1 gap-8">
        <SessionHistoryList />
        <SavedQuizList />
      </div>
    </div>
  )
}
