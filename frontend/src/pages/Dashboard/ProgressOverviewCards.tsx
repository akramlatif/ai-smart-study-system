import React from 'react'
import { Card } from '../../components/ui/Card'
import { Activity, BookOpen, GraduationCap, Target, Bookmark } from 'lucide-react'
import type { UserMetrics } from '../../api/progress'

interface ProgressOverviewCardsProps {
  metrics: UserMetrics | null
}

export function ProgressOverviewCards({ metrics }: ProgressOverviewCardsProps) {
  if (!metrics) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="p-4 animate-pulse bg-gray-100 dark:bg-slate-800 h-24">
            <div />
          </Card>
        ))}
      </div>
    )
  }

  const statCards = [
    { label: 'Total Sessions', value: metrics.total_sessions, icon: <Activity className="w-5 h-5" />, color: 'text-blue-500', bg: 'bg-blue-100 dark:bg-blue-900/30' },
    { label: 'Topics Explored', value: metrics.total_topics, icon: <BookOpen className="w-5 h-5" />, color: 'text-purple-500', bg: 'bg-purple-100 dark:bg-purple-900/30' },
    { label: 'Mastered Topics', value: metrics.mastered_topics, icon: <GraduationCap className="w-5 h-5" />, color: 'text-green-500', bg: 'bg-green-100 dark:bg-green-900/30' },
    { label: 'Quiz Accuracy', value: `${metrics.accuracy_percentage}%`, icon: <Target className="w-5 h-5" />, color: 'text-orange-500', bg: 'bg-orange-100 dark:bg-orange-900/30' },
    { label: 'Saved for Review', value: metrics.questions_to_review, icon: <Bookmark className="w-5 h-5" />, color: 'text-red-500', bg: 'bg-red-100 dark:bg-red-900/30' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      {statCards.map((stat, idx) => (
        <Card key={idx} className="p-4 flex flex-col justify-between hover:shadow-md transition-shadow dark:bg-slate-900 dark:border-slate-800">
          <div className="flex items-start justify-between">
            <p className="text-xs font-medium text-gray-500 dark:text-slate-400">{stat.label}</p>
            <div className={`p-1.5 rounded-lg ${stat.bg} ${stat.color}`}>
              {stat.icon}
            </div>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-slate-100 mt-2">{stat.value}</p>
        </Card>
      ))}
    </div>
  )
}
