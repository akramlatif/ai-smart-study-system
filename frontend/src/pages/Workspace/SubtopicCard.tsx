import React, { useState } from 'react'
import { ChevronDown, ChevronUp, Quote } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { MarkdownRenderer } from '../../components/ui/MarkdownRenderer'

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
          <span className="font-medium text-gray-800 dark:text-slate-200 text-sm">{title}</span>
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
          <MarkdownRenderer content={content} />
          {sourceReferences.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-100 dark:border-slate-800">
              <div className="flex items-center gap-1.5 mb-2">
                <Quote className="w-3 h-3 text-primary-500" />
                <span className="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider">Source Grounding</span>
              </div>
              <ul className="space-y-2">
                {sourceReferences.map((ref, idx) => (
                  <li key={idx} className="text-xs text-gray-500 dark:text-slate-400 pl-3 border-l-2 border-primary-200 dark:border-primary-800/50 italic bg-gray-50/50 dark:bg-slate-900/50 py-1.5 pr-2 rounded-r-md">
                    "{ref}"
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
