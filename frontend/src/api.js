import axios from 'axios'

const configuredUrl =
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000'

export const API_URL =
  configuredUrl.replace(/\/+$/, '')

const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
})

let refreshPromise = null

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')

  if (token) {
    config.headers.Authorization =
      `Bearer ${token}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const original = error.config

    const refresh =
      localStorage.getItem('refresh')

    if (
      error.response?.status === 401 &&
      refresh &&
      original &&
      !original._retry &&
      !original.url?.includes(
        '/auth/token-refresh'
      )
    ) {
      original._retry = true

      try {
        refreshPromise ||= axios
          .post(
            `${API_URL}/auth/token-refresh`,
            { refresh },
          )
          .finally(() => {
            refreshPromise = null
          })

        const { data } =
          await refreshPromise

        localStorage.setItem(
          'access',
          data.access,
        )

        if (data.refresh) {
          localStorage.setItem(
            'refresh',
            data.refresh,
          )
        }

        original.headers.Authorization =
          `Bearer ${data.access}`

        return api(original)

      } catch (refreshError) {

        localStorage.removeItem(
          'access',
        )

        localStorage.removeItem(
          'refresh',
        )

        if (
          window.location.pathname !==
          '/login'
        ) {
          window.location.href =
            '/login'
        }

        return Promise.reject(
          refreshError
        )
      }
    }

    return Promise.reject(error)
  },
)

export default api