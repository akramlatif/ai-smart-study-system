import apiClient from './client'

export async function uploadDocument(
  sessionId: string,
  file: File
): Promise<{ document_id: string; quality_flag: string; extracted_char_count: number }> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await apiClient.post(`/sessions/${sessionId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function deleteDocument(documentId: string): Promise<{ deleted: boolean }> {
  const response = await apiClient.delete(`/documents/${documentId}`)
  return response.data
}
