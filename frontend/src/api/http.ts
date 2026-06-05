import axios from 'axios'

const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 60000)

const http = axios.create({
  baseURL: '/api/v1',
  timeout: DEFAULT_TIMEOUT_MS,
})

async function extractErrorMessage(error: any): Promise<string> {
  if (error?.code === 'ECONNABORTED') {
    return '请求处理时间较长，请稍后重试；如果正在生成报告或 AI 建议，请确认后端仍在运行。'
  }
  if (!error?.response) {
    return '无法连接后端服务，请确认后端已启动且前端代理地址正确。'
  }
  const data = error.response.data
  if (data instanceof Blob) {
    try {
      const text = await data.text()
      const parsed = JSON.parse(text)
      return parsed?.detail || parsed?.message || text || '请求失败'
    } catch {
      return '请求失败，请稍后重试。'
    }
  }
  if (typeof data === 'string') return data
  return data?.detail || data?.message || error.message || '请求失败'
}

http.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const message = await extractErrorMessage(error)
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
