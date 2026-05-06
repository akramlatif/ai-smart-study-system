import apiClient from './client'
import type { TokenResponse } from '../types'

export async function login(email: string, password: string): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', { email, password })
  return response.data
}

export async function register(
  name: string,
  email: string,
  password: string
): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/register', { name, email, password })
  return response.data
}
