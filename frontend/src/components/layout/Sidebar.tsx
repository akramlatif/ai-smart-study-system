import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Plus } from 'lucide-react'
import { NavMenu } from './NavMenu'
import { Button } from '../ui/Button'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'
import { useAuthStore } from '../../store/authStore'
import { createSession } from '../../api/sessions'

export function Sidebar() {
  const navigate = useNavigate()
  const { setCurrentSession } = useSessionStore()
  const { setLoading, setError } = useUIStore()
  const { user } = useAuthStore()

  const handleNewSession = async () => {
    setLoading(true)
    setError(null)
    try {
      const { session_id } = await createSession()
      setCurrentSession({
        id: session_id,
        user_id: user?.id ?? '',
        previous_id: null,
        topics: [],
        explanations: [],
        quiz_questions: [],
        interactions: [],
        created_at: new Date().toISOString(),
        last_active: new Date().toISOString(),
      })
      navigate('/workspace')
    } catch {
      setError('Failed to create session.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <aside className="w-52 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5 border-b border-gray-100">
        <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <span className="font-bold text-gray-900 text-sm">SmartStudy AI</span>
      </div>

      {/* New Session Button */}
      <div className="px-3 py-4">
        <Button
          variant="primary"
          size="sm"
          className="w-full"
          onClick={handleNewSession}
        >
          <Plus className="h-4 w-4" />
          New Session
        </Button>
      </div>

      {/* Navigation */}
      <NavMenu />

      {/* User info at bottom */}
      {user && (
        <div className="mt-auto px-4 py-4 border-t border-gray-100">
          <p className="text-xs text-gray-500 truncate">{user.name}</p>
          <p className="text-xs text-gray-400 truncate">{user.email}</p>
        </div>
      )}
    </aside>
  )
}
