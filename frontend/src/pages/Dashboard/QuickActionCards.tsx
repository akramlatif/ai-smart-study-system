import React from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, Zap, Library, Sparkles } from 'lucide-react'
import { Card } from '../../components/ui/Card'

const actions = [
  {
    label: 'Deep Dive',
    sub: 'Resume last session',
    desc: 'Continue where you left off with full context preserved.',
    icon: BookOpen,
    iconBg: 'bg-primary-100 dark:bg-primary-900/30',
    iconColor: 'text-primary-600 dark:text-primary-400',
    hoverBorder: 'hover:border-primary-200 dark:hover:border-primary-800',
    to: '/workspace',
  },
  {
    label: 'Quick Quiz',
    sub: 'Jump to quiz',
    desc: 'Test your knowledge with questions from your last session.',
    icon: Zap,
    iconBg: 'bg-cyan-100 dark:bg-cyan-900/30',
    iconColor: 'text-cyan-600 dark:text-cyan-400',
    hoverBorder: 'hover:border-cyan-200 dark:hover:border-cyan-800',
    to: '/quiz',
  },
  {
    label: 'My Library',
    sub: 'Browse documents',
    desc: 'Revisit your uploaded notes and study documents.',
    icon: Library,
    iconBg: 'bg-purple-100 dark:bg-purple-900/30',
    iconColor: 'text-purple-600 dark:text-purple-400',
    hoverBorder: 'hover:border-purple-200 dark:hover:border-purple-800',
    to: '/library',
  },
  {
    label: 'Spaced Review',
    sub: 'Revisit weak areas',
    desc: 'Strengthen topics flagged for review with spaced repetition.',
    icon: Sparkles,
    iconBg: 'bg-amber-100 dark:bg-amber-900/30',
    iconColor: 'text-amber-600 dark:text-amber-400',
    hoverBorder: 'hover:border-amber-200 dark:hover:border-amber-800',
    to: '/review',
  },
]

export function QuickActionCards() {
  const navigate = useNavigate()

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {actions.map((action) => (
        <Card
          key={action.label}
          className={`p-5 cursor-pointer transition-colors ${action.hoverBorder}`}
          onClick={() => navigate(action.to)}
        >
          <div className="flex items-center gap-3 mb-3">
            <div className={`h-10 w-10 ${action.iconBg} rounded-lg flex items-center justify-center`}>
              <action.icon className={`h-5 w-5 ${action.iconColor}`} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-slate-100 text-sm">{action.label}</h3>
              <p className="text-xs text-gray-500 dark:text-slate-400">{action.sub}</p>
            </div>
          </div>
          <p className="text-xs text-gray-400 dark:text-slate-500">{action.desc}</p>
        </Card>
      ))}
    </div>
  )
}
