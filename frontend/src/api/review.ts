import api from './client'
import { ReviewItem } from '../types'
import { useAuthStore } from '../store/authStore'

export const reviewApi = {
  getReviewQueue: async (): Promise<ReviewItem[]> => {
    const user = useAuthStore.getState().user
    if (!user) throw new Error('User not authenticated')
      
    const response = await api.get(`/users/${user.id}/review-queue`)
    return response.data
  }
}
