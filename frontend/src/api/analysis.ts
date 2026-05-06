import apiClient from './client'
import type { AnalyzeResponse, ChatResponse } from '../types'

export async function analyzeText(
  sessionId: string,
  content: string
): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('input_type', 'text')
  formData.append('content', content)
  const response = await apiClient.post<AnalyzeResponse>(
    `/sessions/${sessionId}/analyze`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

export async function analyzeFile(
  sessionId: string,
  file: File
): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('input_type', file.name.endsWith('.pdf') ? 'pdf' : 'file')
  formData.append('file', file)
  const response = await apiClient.post<AnalyzeResponse>(
    `/sessions/${sessionId}/analyze`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

export async function analyzeUrl(
  sessionId: string,
  url: string
): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('input_type', 'url')
  formData.append('url', url)
  const response = await apiClient.post<AnalyzeResponse>(
    `/sessions/${sessionId}/analyze`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

export async function chat(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>(`/sessions/${sessionId}/chat`, {
    message,
  })
  return response.data
}
