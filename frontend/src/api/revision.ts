import apiClient from './client'
import type { RevisionMaterial } from '../types'

export const generateRevisionMaterials = async (
  sessionId: string
): Promise<RevisionMaterial> => {
  const { data } = await apiClient.post(`/sessions/${sessionId}/revision`)
  return data
}
