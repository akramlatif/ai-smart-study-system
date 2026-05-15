import React, { useEffect, useRef } from 'react'
import { AIMessage } from './AIMessage'
import { UserMessage } from './UserMessage'
import { LoadingIndicator } from './LoadingIndicator'
import type { Interaction } from '../../types'

interface MessageListProps {
  interactions: Interaction[]
  isLoading?: boolean
}

export function MessageList({ interactions, isLoading = false }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [interactions, isLoading])

  if (interactions.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <p className="text-sm text-gray-400 dark:text-slate-500 text-center">
          Ask a question or analyze content to start the conversation.
        </p>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {interactions.map((interaction, i) =>
        interaction.role === 'user' ? (
          <UserMessage key={i} content={interaction.content} />
        ) : (
          <AIMessage key={i} content={interaction.content} />
        )
      )}
      {isLoading && <LoadingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
