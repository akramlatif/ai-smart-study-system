import React, { useState } from 'react'
import type { FeynmanFeedback } from '../../types'

interface FeedbackCardProps {
  feedback: FeynmanFeedback
}

function ScoreGauge({ score }: { score: number }) {
  const radius = 40
  const circumference = 2 * Math.PI * radius
  const progress = (score / 100) * circumference
  const dashOffset = circumference - progress

  const color =
    score >= 80 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444'

  const label =
    score >= 80 ? 'Strong' : score >= 50 ? 'Developing' : 'Needs Work'

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="100" height="100" viewBox="0 0 100 100" aria-label={`Comprehension score: ${score} out of 100`}>
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="10"
        />
        {/* Progress circle */}
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
        {/* Score text */}
        <text
          x="50"
          y="46"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="20"
          fontWeight="bold"
          fill={color}
        >
          {score}
        </text>
        <text
          x="50"
          y="62"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="9"
          fill="#6b7280"
        >
          / 100
        </text>
      </svg>
      <span className="text-sm font-medium" style={{ color }}>{label}</span>
    </div>
  )
}

export function FeedbackCard({ feedback }: FeedbackCardProps) {
  const [showCorrection, setShowCorrection] = useState(false)

  return (
    <div className="mt-4 rounded-xl border border-purple-100 bg-white shadow-sm overflow-hidden">
      {/* Header with score */}
      <div className="bg-purple-50 px-5 py-4 flex items-center gap-5">
        <ScoreGauge score={feedback.comprehension_score} />
        <div>
          <h4 className="font-semibold text-gray-900 text-base">Comprehension Score</h4>
          <p className="text-sm text-gray-500 mt-0.5">Based on Feynman Technique rubric</p>
        </div>
      </div>

      <div className="px-5 py-4 space-y-4">
        {/* Strengths */}
        {feedback.strengths.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-green-700 mb-2 flex items-center gap-1.5">
              <span>✓</span> Strengths
            </h5>
            <ul className="space-y-1.5">
              {feedback.strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-green-500 mt-0.5 shrink-0">✓</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Gaps */}
        {feedback.gaps.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-yellow-700 mb-2 flex items-center gap-1.5">
              <span>⚠</span> Gaps to Address
            </h5>
            <ul className="space-y-1.5">
              {feedback.gaps.map((g, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-yellow-500 mt-0.5 shrink-0">⚠</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Misconceptions */}
        {feedback.misconceptions.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-red-700 mb-2 flex items-center gap-1.5">
              <span>✗</span> Misconceptions
            </h5>
            <ul className="space-y-1.5">
              {feedback.misconceptions.map((m, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-red-500 mt-0.5 shrink-0">✗</span>
                  <span>{m}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Simplified Correction — collapsible */}
        <div className="border border-gray-100 rounded-lg overflow-hidden">
          <button
            onClick={() => setShowCorrection((v) => !v)}
            className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 transition-colors"
            aria-expanded={showCorrection}
          >
            <span>Show Corrected Explanation</span>
            <span className="text-gray-400">{showCorrection ? '▲' : '▼'}</span>
          </button>
          {showCorrection && (
            <div className="px-4 py-3 text-sm text-gray-700 leading-relaxed bg-white">
              {feedback.simplified_correction}
            </div>
          )}
        </div>

        {/* Encouragement message */}
        <div className="rounded-lg bg-purple-50 border border-purple-100 px-4 py-3">
          <p className="text-sm text-purple-800 italic leading-relaxed">
            {feedback.encouragement_message}
          </p>
        </div>
      </div>
    </div>
  )
}
