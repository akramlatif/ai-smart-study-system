import React, { useRef } from 'react'
import { Upload, Link } from 'lucide-react'
import { Button } from '../../components/ui/Button'

interface InputSourceHeaderProps {
  onFileSelect: (file: File) => void
  onUrlClick: () => void
}

export function InputSourceHeader({ onFileSelect, onUrlClick }: InputSourceHeaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onFileSelect(file)
  }

  return (
    <div className="flex items-center justify-between mb-3">
      <h2 className="font-semibold text-gray-900">Input Source</h2>
      <div className="flex gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md,.rtf"
          className="hidden"
          onChange={handleFileChange}
        />
        <Button
          variant="secondary"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="h-3.5 w-3.5" />
          Upload PDF
        </Button>
        <Button variant="secondary" size="sm" onClick={onUrlClick}>
          <Link className="h-3.5 w-3.5" />
          URL
        </Button>
      </div>
    </div>
  )
}
