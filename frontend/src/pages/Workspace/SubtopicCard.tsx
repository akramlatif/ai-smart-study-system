import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'

interface SubtopicCardProps {
  title: string
  content: string
  sourceReferences?: string[]
}

export function SubtopicCard({ title, content, sourceReferences = [] }: SubtopicCardProps) {
  const [expanded, setExpanded] = useState(true)

  return (
    <Card className="p-4 mb-3">
      <button
        className="w-full flex items-center justify-between text-left"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-800 text-sm">{title}</span>
          <Badge variant="synthesized">SYNTHESIZED</Badge>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
        )}
      </button>
      {expanded && (
        <div className="mt-3">
          <p className="text-sm text-gray-600 leading-relaxed">{content}</p>
          {sourceReferences.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <p className="text-xs text-gray-400">Sources: {sourceReferences.join(', ')}</p>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
