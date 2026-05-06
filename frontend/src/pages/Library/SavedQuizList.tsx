import React from 'react'
import { SavedQuizItem } from './SavedQuizItem'
import { useSessionStore } from '../../store/sessionStore'

export function SavedQuizList() {
  const { quizQuestions } = useSessionStore()
  const saved = quizQuestions.filter((q) => q.saved_for_review)

  return (
    <div>
      <h2 className="font-semibold text-gray-900 mb-4">Saved for Review</h2>
      {saved.length === 0 ? (
        <p className="text-sm text-gray-400">
          No saved questions yet. Bookmark questions in the Quiz screen.
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {saved.map((q) => (
            <SavedQuizItem key={q.id} question={q} />
          ))}
        </div>
      )}
    </div>
  )
}
