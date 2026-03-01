import axios from 'axios'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error?.response?.data?.detail || error.message || 'Request failed'
    return Promise.reject(new Error(message))
  }
)

export type ApiEnvelope<T> = {
  code: number
  message: string
  data: T
}

export async function unwrap<T>(promise: Promise<ApiEnvelope<T> | T>): Promise<T> {
  const payload = await promise
  if ((payload as ApiEnvelope<T>).data !== undefined) {
    return (payload as ApiEnvelope<T>).data
  }
  return payload as T
}

export default http
