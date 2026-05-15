import React, { useState, useEffect } from 'react'
import clsx from 'clsx'
import { BookOpen, AlertCircle, HelpCircle, FastForward, CheckCircle2 } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Badge } from '../../components/ui/Badge'
import { TutorProgressBar } from './TutorProgressBar'
import { startTutorSession, submitTutorAnswer, skipTutorSubtopic, getTutorProgress } from '../../api/tutor'
import { useSessionStore } from '../../store/sessionStore'

export function TutorPanel() {
  const { currentSession, tutorProgress, setTutorProgress } = useSessionStore()
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState('')
  const [difficulty, setDifficulty] = useState('medium')
  const [feedback, setFeedback] = useState<{ isCorrect: boolean; text: string; hint?: string } | null>(null)

  // Load progress if exists
  useEffect(() => {
    if (currentSession && !tutorProgress) {
      getTutorProgress(currentSession.id)
        .then(setTutorProgress)
        .catch(() => {
          // No active tutor session
        })
    }
  }, [currentSession, tutorProgress, setTutorProgress])

  const handleStart = async () => {
    if (!currentSession) return
    setLoading(true)
    try {
      const data = await startTutorSession(currentSession.id, difficulty)
      const newProgress = await getTutorProgress(currentSession.id)
      setTutorProgress(newProgress)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitAnswer = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!currentSession || !tutorProgress || !answer.trim()) return
    setLoading(true)
    setFeedback(null)
    try {
      const data = await submitTutorAnswer(currentSession.id, tutorProgress.tutor_session_id, answer)
      
      setFeedback({
        isCorrect: data.evaluation.is_correct,
        text: data.evaluation.feedback,
        hint: data.evaluation.hint || undefined,
      })

      if (data.advanced) {
        setAnswer('')
        // Optionally add a slight delay before moving on to let user read feedback
        setTimeout(() => {
          setFeedback(null)
          getTutorProgress(currentSession.id).then(setTutorProgress)
        }, 3000)
      } else {
        // Retry logic: keep the answer input
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleSkip = async () => {
    if (!currentSession || !tutorProgress) return
    setLoading(true)
    setFeedback(null)
    try {
      await skipTutorSubtopic(currentSession.id, tutorProgress.tutor_session_id)
      const data = await getTutorProgress(currentSession.id)
      setTutorProgress(data)
      setAnswer('')
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (!currentSession) {
    return <div className="p-4 text-gray-500">Please start a session first.</div>
  }

  if (!tutorProgress) {
    return (
      <div className="flex flex-col items-center justify-center p-8 h-full bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="w-16 h-16 bg-primary-50 rounded-2xl flex items-center justify-center mb-4">
          <BookOpen className="w-8 h-8 text-primary-600" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Interactive Tutor</h2>
        <p className="text-gray-500 text-center max-w-md mb-8">
          Master this topic step-by-step. The AI tutor will explain concepts piece by piece and ask questions to ensure you understand before moving on.
        </p>
        <div className="flex items-center gap-4 mb-8">
          <span className="text-sm font-medium text-gray-700">Initial Difficulty:</span>
          <select 
            value={difficulty} 
            onChange={(e) => setDifficulty(e.target.value)}
            className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
        <Button onClick={handleStart} loading={loading} size="lg">
          Start Tutoring
        </Button>
      </div>
    )
  }

  const { is_complete, steps, current_index, subtopics, difficulty: currentDiff } = tutorProgress
  const currentStep = steps[steps.length - 1] // Get latest step

  if (is_complete) {
    return (
      <Card className="p-8 flex flex-col items-center justify-center text-center">
        <CheckCircle2 className="w-16 h-16 text-green-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Topic Completed!</h2>
        <p className="text-gray-600 mb-6">
          You've successfully worked through all subtopics.
        </p>
        <div className="flex gap-4">
          <div className="bg-gray-50 px-6 py-4 rounded-xl border border-gray-100">
            <p className="text-sm text-gray-500 mb-1">Correct Answers</p>
            <p className="text-2xl font-bold text-green-600">{tutorProgress.correct_count}</p>
          </div>
          <div className="bg-gray-50 px-6 py-4 rounded-xl border border-gray-100">
            <p className="text-sm text-gray-500 mb-1">Incorrect Answers</p>
            <p className="text-2xl font-bold text-red-600">{tutorProgress.incorrect_count}</p>
          </div>
        </div>
        <Button className="mt-8" onClick={() => setTutorProgress(null)}>Start Over</Button>
      </Card>
    )
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary-600" />
          <h2 className="font-semibold text-gray-900">Interactive Tutor</h2>
        </div>
        <Badge variant={currentDiff as 'easy' | 'medium' | 'hard'} className="capitalize">{currentDiff} Difficulty</Badge>
      </div>

      {/* Progress Bar */}
      <div className="bg-white px-6 py-2 border-b border-gray-100">
        <TutorProgressBar 
          subtopics={subtopics.map(s => ({ name: s }))} 
          currentIndex={current_index} 
          isComplete={is_complete} 
        />
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {currentStep && (
          <div className="max-w-3xl mx-auto space-y-6">
            <Card className="p-6 prose prose-primary max-w-none">
              <h3 className="text-xl font-bold text-gray-900 mb-4">{currentStep.subtopic_name}</h3>
              <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {currentStep.explanation}
              </div>
            </Card>

            <Card className="p-6 bg-primary-50 border-primary-100">
              <div className="flex gap-3 mb-4">
                <HelpCircle className="w-6 h-6 text-primary-600 flex-shrink-0" />
                <p className="font-medium text-gray-900">{currentStep.question_text}</p>
              </div>

              <form onSubmit={handleSubmitAnswer} className="space-y-4">
                <Input
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                  disabled={loading || (feedback?.isCorrect && !loading)} // Disable temporarily while advancing
                  className="w-full bg-white"
                />
                
                {feedback && (
                  <div className={clsx("p-4 rounded-lg flex gap-3 text-sm", {
                    "bg-green-100 text-green-800 border border-green-200": feedback.isCorrect,
                    "bg-red-50 text-red-800 border border-red-200": !feedback.isCorrect
                  })}>
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <div>
                      <p className="font-medium">{feedback.text}</p>
                      {feedback.hint && <p className="mt-2 text-sm opacity-90"><span className="font-semibold">Hint:</span> {feedback.hint}</p>}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between pt-2">
                  <Button 
                    type="button" 
                    variant="ghost" 
                    onClick={handleSkip} 
                    disabled={loading}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <FastForward className="w-4 h-4 mr-2" /> Skip
                  </Button>
                  <Button type="submit" loading={loading} disabled={!answer.trim() || feedback?.isCorrect}>
                    Submit Answer
                  </Button>
                </div>
              </form>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
