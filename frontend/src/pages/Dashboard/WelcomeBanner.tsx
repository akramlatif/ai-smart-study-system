import React from 'react'
import { useAuthStore } from '../../store/authStore'

export function WelcomeBanner() {
  const { user } = useAuthStore()
  const firstName = user?.name?.split(' ')[0] ?? 'Student'

  return (
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Welcome Back, {firstName} 👋</h1>
      <p className="text-gray-500 dark:text-slate-400 mt-1">Ready to continue your learning journey?</p>
    </div>
  )
}
