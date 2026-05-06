import React from 'react'
import { Sparkles } from 'lucide-react'
import { Button } from '../../components/ui/Button'

interface AnalyzeButtonProps {
  onClick: () => void
  loading?: boolean
}

export function AnalyzeButton({ onClick, loading = false }: AnalyzeButtonProps) {
  return (
    <Button
      variant="primary"
      size="lg"
      onClick={onClick}
      loading={loading}
      className="w-full mt-3"
    >
      <Sparkles className="h-4 w-4" />
      Analyze ✦
    </Button>
  )
}
