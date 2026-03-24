import axios from 'axios'

const apiBaseFromEnv = import.meta.env.VITE_API_BASE_URL
const API_BASE = apiBaseFromEnv && apiBaseFromEnv.trim().length > 0 ? apiBaseFromEnv : '/api/v1'

export const api = axios.create({
  baseURL: API_BASE,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.dispatchEvent(new Event('auth:unauthorized'))
    }
    return Promise.reject(error)
  },
)
