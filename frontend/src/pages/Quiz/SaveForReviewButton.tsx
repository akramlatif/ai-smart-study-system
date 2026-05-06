import React, { useState } from 'react'
import { Bookmark, BookmarkCheck } from 'lucide-react'
import { saveForReview } from '../../api/quiz'
import { useSessionStore } from '../../store/sessionStore'

interface SaveForReviewButtonProps {
  questionId: string
  isSaved: boolean
}

export function SaveForReviewButton({ questionId, isSaved: initialSaved }: SaveForReviewButtonProps) {
  const [saved, setSaved] = useState(initialSaved)
  const { updateQuizQuestion } = useSessionStore()

  const handleSave = async () => {
    try {
      await saveForReview(questionId)
      setSaved(true)
      updateQuizQuestion(questionId, { saved_for_review: true })
    } catch {
      // ignore
    }
  }

  return (
    <button
      onClick={handleSave}
      disabled={saved}
      className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-primary-600 disabled:text-primary-600 transition-colors"
      title={saved ? 'Saved for review' : 'Save for review'}
    >
      {saved ? (
        <BookmarkCheck className="h-4 w-4 text-primary-600" />
      ) : (
        <Bookmark className="h-4 w-4" />
      )}
      {saved ? 'Saved' : 'Save for Review'}
    </button>
  )
}
