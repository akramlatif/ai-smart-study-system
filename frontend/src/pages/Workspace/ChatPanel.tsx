import React, { useState } from 'react'
import { TutorHeader } from './TutorHeader'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'
import { useSessionStore } from '../../store/sessionStore'
import { useUIStore } from '../../store/uiStore'
import { chat } from '../../api/analysis'

export function ChatPanel() {
  const { currentSession, interactions, addInteraction, addTopic, addExplanations, addQuizQuestions } =
    useSessionStore()
  const { isLoading, setLoading } = useUIStore()
  const [chatLoading, setChatLoading] = useState(false)

  const handleSend = async (message: string) => {
    if (!currentSession) return

    const userInteraction = {
      index: interactions.length + 1,
      role: 'user' as const,
      content: message,
      input_type: 'text' as const,
      timestamp: new Date().toISOString(),
    }
    addInteraction(userInteraction)
    setChatLoading(true)

    try {
      const result = await chat(currentSession.id, message)
      const aiContent =
        result.message ??
        (result.explanations
          ? result.explanations.basic.content
          : 'Here is the response.')

      const aiInteraction = {
        index: interactions.length + 2,
        role: 'assistant' as const,
        content: aiContent,
        input_type: 'text' as const,
        timestamp: new Date().toISOString(),
      }
      addInteraction(aiInteraction)

      if (result.topic) addTopic(result.topic)
      if (result.explanations) addExplanations(result.explanations)
      if (result.quiz_questions) addQuizQuestions(result.quiz_questions)
    } catch {
      const errInteraction = {
        index: interactions.length + 2,
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error. Please try again.',
        input_type: 'text' as const,
        timestamp: new Date().toISOString(),
      }
      addInteraction(errInteraction)
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-slate-900 border-l border-gray-200 dark:border-slate-800 transition-colors">
      <TutorHeader />
      <MessageList interactions={interactions} isLoading={chatLoading} />
      <ChatInput onSend={handleSend} disabled={chatLoading || isLoading || !currentSession} />
    </div>
  )
}
