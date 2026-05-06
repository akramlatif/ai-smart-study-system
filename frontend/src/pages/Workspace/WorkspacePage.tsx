import React from 'react'
import { InputPanel } from './InputPanel'
import { ChatPanel } from './ChatPanel'

export function WorkspacePage() {
  return (
    <div className="flex h-full">
      <div className="flex-[65] overflow-hidden">
        <InputPanel />
      </div>
      <div className="flex-[35] overflow-hidden">
        <ChatPanel />
      </div>
    </div>
  )
}
