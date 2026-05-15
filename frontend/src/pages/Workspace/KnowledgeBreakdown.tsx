import React from 'react'
import { LevelTabSwitcher } from './LevelTabSwitcher'
import { ExplanationCards } from './ExplanationCards'

export function KnowledgeBreakdown() {
  return (
    <div className="mt-6">
      <h3 className="font-semibold text-gray-900 dark:text-slate-100 mb-3">Knowledge Breakdown</h3>
      <LevelTabSwitcher />
      <ExplanationCards />
    </div>
  )
}
