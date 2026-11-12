import React, { useEffect, useState } from 'react'
import { Lightbulb } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { useAuthStore } from '../../store/authStore'
import { getSynthesisSuggestions } from '../../api/dashboard'
import type { SynthesisSuggestion } from '../../types'

export function SynthesisSuggestionsPanel() {
  const { user } = useAuthStore()
  const [suggestions, setSuggestions] = useState<SynthesisSuggestion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.id) {
      getSynthesisSuggestions(user.id)
        .then(setSuggestions)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [user?.id])

  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="h-4 w-4 text-primary-600 dark:text-primary-400" />
        <h2 className="font-semibold text-gray-900 dark:text-slate-100">AI Suggestions</h2>
      </div>
      {loading ? (
        <div className="flex flex-col gap-3 animate-pulse">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <div className="h-3 bg-gray-200 dark:bg-slate-800 rounded w-2/3" />
              <div className="h-4 w-16 bg-gray-100 dark:bg-slate-800/60 rounded-full" />
            </div>
          ))}
        </div>
      ) : suggestions.length === 0 ? (
        <p className="text-sm text-gray-400 dark:text-slate-500">
          Study more topics to get personalized suggestions.
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {suggestions.map((s, i) => (
            <div key={i} className="flex items-center justify-between gap-2">
              <p className="text-sm text-gray-700 dark:text-slate-300 truncate">{s.topic}</p>
              <Badge variant={s.relevance_tag === 'high_relevance' ? 'high-relevance' : 'review-needed'}>
                {s.relevance_tag === 'high_relevance' ? 'High Relevance' : 'Review Needed'}
              </Badge>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
