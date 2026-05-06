import React from 'react'
import { BookOpen, Clock, MessageSquare } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { Card } from '../../components/ui/Card'
import type { SessionHistoryItem as SessionHistoryItemType } from '../../types'

interface SessionHistoryItemProps {
  session: SessionHistoryItemType
}

export function SessionHistoryItem({ session }: SessionHistoryItemProps) {
  const duration = session.ended_at
    ? Math.round(
        (new Date(session.ended_at).getTime() - new Date(session.created_at).getTime()) / 60000
      )
    : null

  return (
    <Card className="p-4 flex items-center gap-4">
      <div className="h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
        <BookOpen className="h-5 w-5 text-primary-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-800 text-sm truncate">
          Session #{session.id.slice(0, 8)}
        </p>
        <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
          </span>
          {duration !== null && <span>{duration} min</span>}
          <span className="flex items-center gap-1">
            <MessageSquare className="h-3 w-3" />
            {session.interaction_count} interactions
          </span>
        </div>
      </div>
    </Card>
  )
}
