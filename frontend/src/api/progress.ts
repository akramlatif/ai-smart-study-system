import apiClient from './client'

export interface UserMetrics {
  total_sessions: number
  total_topics: number
  mastered_topics: number
  accuracy_percentage: number
  questions_to_review: number
}

export const getUserMetrics = async (): Promise<UserMetrics> => {
  const { data } = await apiClient.get('/progress/metrics')
  return data
}
