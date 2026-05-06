import React from 'react'
import { SubtopicCard } from './SubtopicCard'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'

export function ExplanationCards() {
  const { explanations, topics } = useSessionStore()
  const { activeExplanationLevel } = useUIStore()

  if (explanations.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">
        Analyze some content to see explanations here.
      </p>
    )
  }

  const latestExplanation = explanations[explanations.length - 1]
  const latestTopic = topics[topics.length - 1]
  const levelContent = latestExplanation[activeExplanationLevel]

  return (
    <SubtopicCard
      title={latestTopic?.main_topic ?? 'Topic'}
      content={levelContent.content}
      sourceReferences={levelContent.source_references}
    />
  )
}
