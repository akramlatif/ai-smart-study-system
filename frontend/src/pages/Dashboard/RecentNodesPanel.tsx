import React, { useEffect, useState } from 'react'
import { BookOpen, Clock } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { Card } from '../../components/ui/Card'
import { useAuthStore } from '../../store/authStore'
import { getUserSessions } from '../../api/dashboard'
import type { SessionHistoryItem } from '../../types'

export function RecentNodesPanel() {
  const { user } = useAuthStore()
  const [sessions, setSessions] = useState<SessionHistoryItem[]>([])

  useEffect(() => {
    if (user?.id) {
      getUserSessions(user.id, 5).then(setSessions).catch(() => {})
    }
  }, [user?.id])

  return (
    <Card className="p-5 mb-6">
      <h2 className="font-semibold text-gray-900 mb-4">Recent Sessions</h2>
      {sessions.length === 0 ? (
        <p className="text-sm text-gray-400">No sessions yet. Start studying!</p>
      ) : (
        <div className="flex flex-col gap-3">
          {sessions.map((session) => (
            <div key={session.id} className="flex items-center gap-3">
              <div className="h-9 w-9 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <BookOpen className="h-4 w-4 text-primary-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">
                  Session #{session.id.slice(0, 8)}
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-400">
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
