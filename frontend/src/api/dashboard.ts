import apiClient from './client'
import type { SessionHistoryItem, SynthesisSuggestion } from '../types'

export async function getUserSessions(
  userId: string,
  limit = 10,
  offset = 0
): Promise<SessionHistoryItem[]> {
  const response = await apiClient.get<SessionHistoryItem[]>(`/users/${userId}/sessions`, {
    params: { limit, offset },
  })
  return response.data
}

export async function getSynthesisSuggestions(userId: string): Promise<SynthesisSuggestion[]> {
  const response = await apiClient.get<SynthesisSuggestion[]>(
    `/users/${userId}/synthesis-suggestions`
  )
  return response.data
}
