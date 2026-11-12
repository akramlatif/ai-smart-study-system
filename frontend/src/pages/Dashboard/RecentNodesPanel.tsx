import React, { useEffect, useState } from 'react'
import { BookOpen, Clock, ArrowRight } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { useNavigate } from 'react-router-dom'
import { Card } from '../../components/ui/Card'
import { useAuthStore } from '../../store/authStore'
import { getUserSessions } from '../../api/dashboard'
import type { SessionHistoryItem } from '../../types'

export function RecentNodesPanel() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [sessions, setSessions] = useState<SessionHistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.id) {
      getUserSessions(user.id, 5)
        .then(setSessions)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [user?.id])

  return (
    <Card className="p-5 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-900 dark:text-slate-100">Recent Sessions</h2>
        <button
          onClick={() => navigate('/library')}
          className="flex items-center gap-1 text-xs font-medium text-primary-600 dark:text-primary-400 hover:underline"
        >
          View all <ArrowRight className="h-3 w-3" />
        </button>
      </div>
      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center gap-3 animate-pulse">
              <div className="h-9 w-9 rounded-lg bg-gray-200 dark:bg-slate-800" />
              <div className="flex-1 space-y-1.5">
                <div className="h-3 bg-gray-200 dark:bg-slate-800 rounded w-1/3" />
                <div className="h-2.5 bg-gray-100 dark:bg-slate-800/60 rounded w-1/4" />
              </div>
            </div>
          ))}
        </div>
      ) : sessions.length === 0 ? (
        <p className="text-sm text-gray-400 dark:text-slate-500">
          No sessions yet. Click “New Session” to start studying!
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="flex items-center gap-3 p-2 -m-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
              onClick={() => navigate('/workspace')}
            >
              <div className="h-9 w-9 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
                <BookOpen className="h-4 w-4 text-primary-600 dark:text-primary-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 dark:text-slate-200 truncate">
                  Session #{session.id.slice(0, 8)}
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-400 dark:text-slate-500">
                  <Clock className="h-3 w-3" />
                  <span>{formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}</span>
                  <span>·</span>
                  <span>{session.interaction_count} interactions</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
