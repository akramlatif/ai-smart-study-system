import React from 'react'
import { Flame } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import type { StudyStreak } from '../../api/progress'

interface WelcomeBannerProps {
  streak: StudyStreak | null
}

export function WelcomeBanner({ streak }: WelcomeBannerProps) {
  const { user } = useAuthStore()
  const firstName = user?.name?.split(' ')[0] ?? 'Student'

  return (
    <div className="mb-6 bg-gradient-to-r from-primary-600 via-purple-600 to-cyan-500 rounded-2xl p-6 text-white shadow-lg shadow-primary-600/20">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Welcome Back, {firstName} 👋</h1>
          <p className="text-white/80 mt-1">Ready to continue your learning journey?</p>
        </div>
        {streak && (
          <div className="flex items-center gap-2 bg-white/15 backdrop-blur-sm rounded-xl px-4 py-2.5 border border-white/20">
            <Flame
              className={`h-5 w-5 ${streak.current_streak > 0 ? 'text-orange-300 animate-pulse' : 'text-white/60'}`}
            />
            <div>
              <p className="text-sm font-bold leading-tight">
                {streak.current_streak} day{streak.current_streak === 1 ? '' : 's'} streak
              </p>
              <p className="text-xs text-white/70">
                Longest: {streak.longest_streak} · {streak.days_active} active days
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
