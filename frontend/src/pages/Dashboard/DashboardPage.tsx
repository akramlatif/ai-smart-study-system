import React from 'react'
import { WelcomeBanner } from './WelcomeBanner'
import { QuickActionCards } from './QuickActionCards'
import { CognitiveLoadChart } from './CognitiveLoadChart'
import { RecentNodesPanel } from './RecentNodesPanel'
import { SynthesisSuggestionsPanel } from './SynthesisSuggestionsPanel'

export function DashboardPage() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <WelcomeBanner />
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
