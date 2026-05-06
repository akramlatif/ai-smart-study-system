import React from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, Zap } from 'lucide-react'
import { Card } from '../../components/ui/Card'

export function QuickActionCards() {
  const navigate = useNavigate()

  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <Card
        className="p-5 cursor-pointer hover:border-primary-200 transition-colors"
        onClick={() => navigate('/workspace')}
      >
        <div className="flex items-center gap-3 mb-3">
          <div className="h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <BookOpen className="h-5 w-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">Deep Dive</h3>
            <p className="text-xs text-gray-500">Resume last session</p>
          </div>
        </div>
        <p className="text-xs text-gray-400">
          Continue where you left off with full context preserved.
        </p>
      </Card>

      <Card
        className="p-5 cursor-pointer hover:border-cyan-200 transition-colors"
        onClick={() => navigate('/quiz')}
      >
        <div className="flex items-center gap-3 mb-3">
          <div className="h-10 w-10 bg-cyan-100 rounded-lg flex items-center justify-center">
            <Zap className="h-5 w-5 text-cyan-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">Quick Quiz</h3>
            <p className="text-xs text-gray-500">Jump to quiz</p>
          </div>
        </div>
        <p className="text-xs text-gray-400">
          Test your knowledge with questions from your last session.
        </p>
      </Card>
    </div>
  )
}
