import React from 'react'
import clsx from 'clsx'

type BadgeVariant =
  | 'easy'
  | 'medium'
  | 'hard'
  | 'high-relevance'
  | 'review-needed'
  | 'synthesized'
  | 'default'

interface BadgeProps {
  variant?: BadgeVariant
  children: React.ReactNode
  className?: string
}

const variantClasses: Record<BadgeVariant, string> = {
  easy: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  hard: 'bg-red-100 text-red-700',
  'high-relevance': 'bg-purple-100 text-purple-700',
  'review-needed': 'bg-orange-100 text-orange-700',
  synthesized: 'bg-cyan-100 text-cyan-700',
  default: 'bg-gray-100 text-gray-700',
}

export function Badge({ variant = 'default', children, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wide',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  )
}
