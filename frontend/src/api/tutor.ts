import apiClient from './client'
import type {
  TutorStartRequest,
  TutorStartResponse,
  TutorAnswerRequest,
  TutorAnswerResponse,
  TutorProgress,
} from '../types'

export const startTutorSession = async (
  sessionId: string,
  difficulty: string = 'medium'
): Promise<TutorStartResponse> => {
  const { data } = await apiClient.post(`/sessions/${sessionId}/tutor/start`, {
    difficulty,
  } as TutorStartRequest)
  return data
}

export const submitTutorAnswer = async (
  sessionId: string,
  tutorSessionId: string,
  answer: string
): Promise<TutorAnswerResponse> => {
  const { data } = await apiClient.post(`/sessions/${sessionId}/tutor/answer`, {
    tutor_session_id: tutorSessionId,
    answer,
  } as TutorAnswerRequest)
  return data
}

export const skipTutorSubtopic = async (
  sessionId: string,
  tutorSessionId: string
) => {
  const { data } = await apiClient.post(`/sessions/${sessionId}/tutor/skip`, {
    tutor_session_id: tutorSessionId,
  })
  return data
}

export const getTutorProgress = async (
  sessionId: string
): Promise<TutorProgress> => {
  const { data } = await apiClient.get(`/sessions/${sessionId}/tutor/progress`)
  return data
}
