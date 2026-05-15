import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Plus, Sun, Moon } from 'lucide-react'
import { NavMenu } from './NavMenu'
import { Button } from '../ui/Button'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'
import { useAuthStore } from '../../store/authStore'
import { createSession } from '../../api/sessions'

export function Sidebar() {
  const navigate = useNavigate()
  const { setCurrentSession } = useSessionStore()
  const { setLoading, setError, theme, toggleTheme } = useUIStore()
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
    <aside className="w-52 flex-shrink-0 bg-white dark:bg-slate-900 border-r border-gray-200 dark:border-slate-800 flex flex-col h-full transition-colors">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5 border-b border-gray-100 dark:border-slate-800">
        <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <span className="font-bold text-gray-900 dark:text-white text-sm">SmartStudy AI</span>
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

      {/* Bottom section with User Info and Theme Toggle */}
      <div className="mt-auto border-t border-gray-100 dark:border-slate-800 p-4">
        {user && (
          <div className="mb-4">
            <p className="text-xs text-gray-500 dark:text-slate-400 truncate">{user.name}</p>
            <p className="text-xs text-gray-400 dark:text-slate-500 truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={toggleTheme}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </aside>
  )
}
