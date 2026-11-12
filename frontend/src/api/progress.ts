import apiClient from './client'

export interface UserMetrics {
  total_sessions: number
  total_topics: number
  mastered_topics: number
  accuracy_percentage: number
  questions_to_review: number
}

export interface DailyActivity {
  date: string
  label: string
  sessions: number
  quiz_questions: number
}

export interface WeeklyActivity {
  days: DailyActivity[]
  total_sessions: number
  total_questions: number
}

export interface StudyStreak {
  current_streak: number
  longest_streak: number
  days_active: number
  last_active_date: string | null
}

export const getUserMetrics = async (): Promise<UserMetrics> => {
  const { data } = await apiClient.get('/progress/metrics')
  return data
}

export const getWeeklyActivity = async (): Promise<WeeklyActivity> => {
  const { data } = await apiClient.get('/progress/weekly-activity')
  return data
}

export const getStudyStreak = async (): Promise<StudyStreak> => {
  const { data } = await apiClient.get('/progress/streak')
  return data
}
