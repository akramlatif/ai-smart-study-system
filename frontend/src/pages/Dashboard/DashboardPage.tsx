import React, { useEffect, useState } from 'react'
import { WelcomeBanner } from './WelcomeBanner'
import { QuickActionCards } from './QuickActionCards'
import { CognitiveLoadChart } from './CognitiveLoadChart'
import { RecentNodesPanel } from './RecentNodesPanel'
import { SynthesisSuggestionsPanel } from './SynthesisSuggestionsPanel'
import { ProgressOverviewCards } from './ProgressOverviewCards'
import { getUserMetrics, type UserMetrics } from '../../api/progress'

export function DashboardPage() {
  const [metrics, setMetrics] = useState<UserMetrics | null>(null)

  useEffect(() => {
    getUserMetrics()
      .then(setMetrics)
      .catch((e) => console.error('Failed to load metrics', e))
  }, [])

  return (
    <div className="p-6 max-w-5xl mx-auto dark:bg-slate-950 transition-colors">
      <WelcomeBanner />
      <ProgressOverviewCards metrics={metrics} />
      <QuickActionCards />
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
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
