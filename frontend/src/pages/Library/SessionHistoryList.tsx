import React, { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { SessionHistoryItem } from './SessionHistoryItem'
import { Button } from '../../components/ui/Button'
import { useAuthStore } from '../../store/authStore'
import { getUserSessions } from '../../api/dashboard'
import type { SessionHistoryItem as SessionHistoryItemType } from '../../types'

const PAGE_SIZE = 5

export function SessionHistoryList() {
  const { user } = useAuthStore()
  const [sessions, setSessions] = useState<SessionHistoryItemType[]>([])
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)

  useEffect(() => {
    if (!user?.id) return
    getUserSessions(user.id, PAGE_SIZE, page * PAGE_SIZE)
      .then((data) => {
        setSessions(data)
        setHasMore(data.length === PAGE_SIZE)
      })
      .catch(() => {})
  }, [user?.id, page])

  return (
    <div>
      <h2 className="font-semibold text-gray-900 mb-4">Session History</h2>
      <div className="flex flex-col gap-3">
        {sessions.length === 0 ? (
          <p className="text-sm text-gray-400">No sessions found.</p>
        ) : (
          sessions.map((s) => <SessionHistoryItem key={s.id} session={s} />)
        )}
      </div>
      <div className="flex items-center gap-2 mt-4">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
        >
          <ChevronLeft className="h-4 w-4" />
          Prev
        </Button>
        <span className="text-sm text-gray-500">Page {page + 1}</span>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setPage((p) => p + 1)}
          disabled={!hasMore}
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
