import React, { useState } from 'react'
import clsx from 'clsx'
import { RefreshCw } from 'lucide-react'

interface FlashcardProps {
  front: string
  back: string
  className?: string
}

export function Flashcard({ front, back, className }: FlashcardProps) {
  const [isFlipped, setIsFlipped] = useState(false)

  return (
    <div
      className={clsx('relative w-full h-64 perspective-1000 cursor-pointer group', className)}
      onClick={() => setIsFlipped(!isFlipped)}
    >
      <div
        className={clsx(
          'w-full h-full transition-transform duration-500 transform-style-3d relative',
          isFlipped ? 'rotate-y-180' : ''
        )}
      >
        {/* Front */}
        <div className="absolute inset-0 backface-hidden bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col justify-center items-center text-center">
          <p className="text-lg font-medium text-gray-900 mb-4">{front}</p>
          <div className="absolute bottom-4 text-gray-400 group-hover:text-primary-500 transition-colors flex items-center gap-2 text-sm">
            <RefreshCw className="w-4 h-4" /> Click to flip
          </div>
        </div>

        {/* Back */}
        <div className="absolute inset-0 backface-hidden bg-primary-50 rounded-xl shadow-sm border border-primary-200 p-6 flex flex-col justify-center items-center text-center rotate-y-180">
          <p className="text-gray-800 leading-relaxed overflow-y-auto">{back}</p>
        </div>
      </div>
    </div>
  )
}
