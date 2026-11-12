import React, { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { getWeeklyActivity, type WeeklyActivity } from '../../api/progress'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const options = {
  responsive: true,
  plugins: {
    legend: { position: 'top' as const },
    title: { display: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { precision: 0 },
      grid: { color: 'rgba(148, 163, 184, 0.15)' },
    },
    x: { grid: { display: false } },
  },
}

export function CognitiveLoadChart() {
  const [activity, setActivity] = useState<WeeklyActivity | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getWeeklyActivity()
      .then(setActivity)
      .catch((e) => console.error('Failed to load weekly activity', e))
      .finally(() => setLoading(false))
  }, [])

  const data = activity
    ? {
        labels: activity.days.map((d) => d.label),
        datasets: [
          {
            label: 'Study Sessions',
            data: activity.days.map((d) => d.sessions),
            backgroundColor: '#7c3aed',
            borderRadius: 6,
          },
          {
            label: 'Quiz Questions',
            data: activity.days.map((d) => d.quiz_questions),
            backgroundColor: '#06b6d4',
            borderRadius: 6,
          },
        ],
      }
    : null

  const badge =
    activity && activity.total_sessions >= 7
      ? { variant: 'synthesized' as const, text: 'ACTIVE' }
      : { variant: 'review-needed' as const, text: 'KEEP GOING' }

  return (
    <Card className="p-5 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="font-semibold text-gray-900 dark:text-slate-100">Weekly Activity</h2>
          {activity && (
            <p className="text-xs text-gray-400 dark:text-slate-500 mt-0.5">
              {activity.total_sessions} sessions · {activity.total_questions} questions in the last 7 days
            </p>
          )}
        </div>
        <Badge variant={badge.variant}>{badge.text}</Badge>
      </div>
      {loading ? (
        <div className="h-48 flex items-center justify-center">
          <div className="animate-pulse text-sm text-gray-400 dark:text-slate-500">Loading activity…</div>
        </div>
      ) : data ? (
        <Bar data={data} options={options} />
      ) : (
        <div className="h-48 flex items-center justify-center text-sm text-gray-400 dark:text-slate-500">
          Unable to load activity data.
        </div>
      )}
    </Card>
  )
}
