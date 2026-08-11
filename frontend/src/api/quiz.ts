import apiClient from './client'
import type { QuizQuestion } from '../types'

export async function getQuiz(
  sessionId: string,
  difficulty?: string,
  type?: string
): Promise<QuizQuestion[]> {
  const params: Record<string, string> = {}
  if (difficulty) params.difficulty = difficulty
  if (type) params.type = type
  const response = await apiClient.get<QuizQuestion[]>(`/sessions/${sessionId}/quiz`, { params })
  return response.data
}

export async function saveForReview(questionId: string): Promise<{ saved: boolean }> {
  const response = await apiClient.patch(`/quiz-questions/${questionId}/save-for-review`)
  return response.data
}

export async function getAnswer(
  sessionId: string,
  questionId: string
): Promise<{ correct_answer: string; explanation: string | null }> {
  const response = await apiClient.get(`/sessions/${sessionId}/quiz/${questionId}/answer`)
  return response.data
}

export async function submitAnswer(
  sessionId: string,
  questionId: string,
  body: { answer: string }
): Promise<{ is_correct: boolean; correct_answer: string; explanation: string | null }> {
  const response = await apiClient.post(`/sessions/${sessionId}/quiz/${questionId}/answer`, body)
  return response.data
}

export const quizApi = {
  getQuiz,
  saveForReview,
  getAnswer,
  submitAnswer
}
