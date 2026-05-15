import apiClient from './client'
import type {
  FeynmanAttemptResponse,
  SocraticSessionResponse,
  SocraticResponse,
} from '../types'

export const submitFeynmanExplanation = async (
  sessionId: string,
  explanation: string,
): Promise<FeynmanAttemptResponse> => {
  const { data } = await apiClient.post(`/sessions/${sessionId}/feynman`, { explanation })
  return data
}

export const getFeynmanHistory = async (sessionId: string) => {
  const { data } = await apiClient.get(`/sessions/${sessionId}/feynman/history`)
  return data
}

export const startSocraticSession = async (
  sessionId: string,
): Promise<SocraticSessionResponse> => {
  const { data } = await apiClient.post(`/sessions/${sessionId}/socratic/start`, {})
  return data
}

export const respondToSocratic = async (
  sessionId: string,
  socraticSessionId: string,
  answer: string,
): Promise<SocraticResponse> => {
  const { data } = await apiClient.post(`/sessions/${sessionId}/socratic/respond`, {
    socratic_session_id: socraticSessionId,
    answer,
  })
  return data
}

export const getSocraticHistory = async (
  sessionId: string,
  socraticSessionId: string,
) => {
  const { data } = await apiClient.get(
    `/sessions/${sessionId}/socratic/${socraticSessionId}`,
  )
  return data
}
