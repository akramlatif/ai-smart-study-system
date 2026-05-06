import apiClient from './client'
import type { StudySession, SessionSummary } from '../types'

export async function createSession(): Promise<{ session_id: string; created_at: string }> {
  const response = await apiClient.post('/sessions')
  return response.data
}

export async function getSession(sessionId: string): Promise<StudySession> {
  const response = await apiClient.get<StudySession>(`/sessions/${sessionId}`)
  return response.data
}

export async function resetSession(
  sessionId: string
): Promise<{ new_session_id: string; previous_session_id: string }> {
  const response = await apiClient.post(`/sessions/${sessionId}/reset`)
  return response.data
}

export async function getSessionSummary(sessionId: string): Promise<SessionSummary> {
  const response = await apiClient.get<SessionSummary>(`/sessions/${sessionId}/summary`)
  return response.data
}

export async function deleteSession(sessionId: string): Promise<{ deleted: boolean }> {
  const response = await apiClient.delete(`/sessions/${sessionId}`)
  return response.data
}
