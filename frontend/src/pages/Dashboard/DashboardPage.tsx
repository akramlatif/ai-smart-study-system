import React, { useEffect, useState } from 'react'
import { WelcomeBanner } from './WelcomeBanner'
import { QuickActionCards } from './QuickActionCards'
import { CognitiveLoadChart } from './CognitiveLoadChart'
import { RecentNodesPanel } from './RecentNodesPanel'
import { SynthesisSuggestionsPanel } from './SynthesisSuggestionsPanel'
import { ProgressOverviewCards } from './ProgressOverviewCards'
import { getUserMetrics, getStudyStreak, type UserMetrics, type StudyStreak } from '../../api/progress'

export function DashboardPage() {
  const [metrics, setMetrics] = useState<UserMetrics | null>(null)
  const [streak, setStreak] = useState<StudyStreak | null>(null)

  useEffect(() => {
    getUserMetrics()
      .then(setMetrics)
      .catch((e) => console.error('Failed to load metrics', e))
    getStudyStreak()
      .then(setStreak)
      .catch((e) => console.error('Failed to load streak', e))
  }, [])

  return (
    <div className="p-6 max-w-6xl mx-auto dark:bg-slate-950 transition-colors">
      <WelcomeBanner streak={streak} />
      <ProgressOverviewCards metrics={metrics} />
      <QuickActionCards />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-1 lg:col-span-2">
          <CognitiveLoadChart />
          <RecentNodesPanel />
        </div>
        <div className="col-span-1">
          <SynthesisSuggestionsPanel />
        </div>
      </div>
    </div>
  )
}
