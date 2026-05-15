import React, { useState } from 'react'
import { BookMarked, Sparkles, Layers, BookOpen, Quote, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Flashcard } from '../../components/ui/Flashcard'
import { generateRevisionMaterials } from '../../api/revision'
import { useSessionStore } from '../../store/sessionStore'

export function RevisionPanel() {
  const { currentSession, revisionMaterial, setRevisionMaterial } = useSessionStore()
  const [loading, setLoading] = useState(false)
  const [activeFlashcardIndex, setActiveFlashcardIndex] = useState(0)

  const handleGenerate = async () => {
    if (!currentSession) return
    setLoading(true)
    try {
      const material = await generateRevisionMaterials(currentSession.id)
      setRevisionMaterial(material)
      setActiveFlashcardIndex(0)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (!currentSession) {
    return <div className="p-4 text-gray-500">Please start a session first.</div>
  }

  if (!revisionMaterial) {
    return (
      <div className="flex flex-col items-center justify-center p-8 h-full bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="w-16 h-16 bg-primary-50 rounded-2xl flex items-center justify-center mb-4">
          <BookMarked className="w-8 h-8 text-primary-600" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Revision Materials</h2>
        <p className="text-gray-500 text-center max-w-md mb-8">
          Generate comprehensive revision notes, flashcards, key definitions, and practice exam questions tailored to your current topic.
        </p>
        <Button onClick={handleGenerate} loading={loading} size="lg">
          <Sparkles className="w-4 h-4 mr-2" /> Generate Revision Hub
        </Button>
      </div>
    )
  }

  const { flashcards, summary_notes, key_definitions, formulas, exam_questions } = revisionMaterial

  return (
    <div className="flex flex-col h-full bg-gray-50 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookMarked className="w-5 h-5 text-primary-600" />
          <h2 className="font-semibold text-gray-900">Revision Hub</h2>
        </div>
        <Button variant="secondary" size="sm" onClick={handleGenerate} loading={loading}>
          <RefreshCw className="w-4 h-4 mr-2" /> Regenerate
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        
        {/* Flashcards Section */}
        {flashcards && flashcards.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Layers className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-bold text-gray-900">Flashcards</h3>
            </div>
            <div className="max-w-xl mx-auto">
              <Flashcard 
                front={flashcards[activeFlashcardIndex].front} 
                back={flashcards[activeFlashcardIndex].back} 
              />
              <div className="flex items-center justify-between mt-4">
                <Button 
                  variant="secondary" 
                  onClick={() => setActiveFlashcardIndex(Math.max(0, activeFlashcardIndex - 1))}
                  disabled={activeFlashcardIndex === 0}
                >
                  <ChevronLeft className="w-4 h-4 mr-1" /> Prev
                </Button>
                <span className="text-sm font-medium text-gray-500">
                  {activeFlashcardIndex + 1} / {flashcards.length}
                </span>
                <Button 
                  variant="secondary" 
                  onClick={() => setActiveFlashcardIndex(Math.min(flashcards.length - 1, activeFlashcardIndex + 1))}
                  disabled={activeFlashcardIndex === flashcards.length - 1}
                >
                  Next <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          </section>
        )}

        <hr className="border-gray-200" />

        {/* Summary Notes */}
        {summary_notes && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <BookOpen className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-bold text-gray-900">Summary Notes</h3>
            </div>
            <Card className="p-6 prose prose-primary max-w-none">
              <div className="whitespace-pre-wrap">{summary_notes}</div>
            </Card>
          </section>
        )}

        {/* Key Definitions */}
        {key_definitions && key_definitions.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Quote className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-bold text-gray-900">Key Definitions</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {key_definitions.map((def, idx) => (
                <Card key={idx} className="p-4 bg-white border-l-4 border-l-primary-500">
                  <h4 className="font-bold text-gray-900 mb-1">{def.term}</h4>
                  <p className="text-gray-600 text-sm">{def.definition}</p>
                </Card>
              ))}
            </div>
          </section>
        )}

        {/* Formulas (if any) */}
        {formulas && formulas.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <span className="font-mono text-lg font-bold text-primary-600">∑</span>
              <h3 className="text-lg font-bold text-gray-900">Formulas</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {formulas.map((f, idx) => (
                <Card key={idx} className="p-4 bg-gray-50 flex items-center gap-4">
                  <div className="bg-white px-3 py-2 rounded border border-gray-200 font-mono text-primary-700 font-bold">
                    {f.formula}
                  </div>
                  <p className="text-sm text-gray-600 flex-1">{f.description}</p>
                </Card>
              ))}
            </div>
          </section>
        )}

        {/* Exam Questions */}
        {exam_questions && exam_questions.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-bold text-gray-900">Practice Exam Questions</h3>
            </div>
            <div className="space-y-4">
              {exam_questions.map((eq, idx) => (
                <details key={idx} className="group bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <summary className="p-4 font-medium cursor-pointer list-none flex items-center justify-between hover:bg-gray-50 transition-colors">
                    <span className="flex-1 pr-4">{idx + 1}. {eq.question}</span>
                    <span className="text-xs font-bold uppercase tracking-wider text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {eq.difficulty}
                    </span>
                  </summary>
                  <div className="p-4 bg-gray-50 border-t border-gray-100">
                    <p className="text-sm font-semibold text-gray-900 mb-2">Expected Answer:</p>
                    <p className="text-sm text-gray-600 leading-relaxed">{eq.expected_answer}</p>
                  </div>
                </details>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
