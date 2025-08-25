// API configuration
const isDevelopment = import.meta.env.DEV
const API_BASE_URL = isDevelopment 
  ? '/api' 
  : 'https://bible-outline-backend.onrender.com/api'

export const getApiUrl = (endpoint) => {
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  return `${API_BASE_URL}/${cleanEndpoint}`
}

export default API_BASE_URL