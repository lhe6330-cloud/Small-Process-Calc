import axios from 'axios'

// 获取 API 基础 URL
// 优先级：1. 环境变量 2. 当前域名 + /api 路径 3. 默认 /api
const getBaseURL = () => {
  // 检查是否有环境变量配置（Docker 构建时注入）
  if (import.meta.env && import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }

  // 生产环境：使用相对路径，由 Nginx 代理
  // 开发环境：使用 Vite 代理
  return '/api'
}

// 创建 axios 实例
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加日志
api.interceptors.request.use(
  (config) => {
    console.log('[API Request]', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一处理响应和错误
api.interceptors.response.use(
  (response) => {
    console.log('[API Response]', response.config.url, response.data)
    return response.data
  },
  (error) => {
    console.error('[API Response Error]', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message,
    })

    // 返回友好的错误信息
    let errorMsg = '网络错误'
    if (error.response) {
      errorMsg = `服务器错误：${error.response.status}`
    } else if (error.request) {
      errorMsg = '无法连接到服务器，请检查后端是否正常运行'
    }

    return Promise.reject({ ...error, userMessage: errorMsg })
  }
)

export default api
