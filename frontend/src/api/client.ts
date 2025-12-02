import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors (unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

export interface VendorInvoice {
  id: number
  invoice_number: string
  vendor_name: string
  invoice_date: string | null
  due_date: string | null
  total_amount: number | null
  tax_amount: number | null
  subtotal: number | null
  po_numbers: string[]
  file_path: string | null
  parsed_data: any
  confidence_score: number | null  // Backend uses confidence_score
  confidence?: number | null  // Legacy field for compatibility
  status: string
  created_at: string
  updated_at: string
}

export interface SyncResponse {
  success: boolean
  message: string
  sync_operation?: any
  error?: string
}

export interface DashboardStats {
  total_invoices: number
  pending_sync: number
  synced: number
  failed: number
  total_amount: number
  recent_invoices: VendorInvoice[]
}

// Auth API
export const authAPI = {
  register: async (email: string, password: string, fullName: string, username?: string) => {
    const response = await apiClient.post('/api/auth/register', {
      email,
      username: username || email.split('@')[0], // Use email prefix as default username
      password,
      full_name: fullName,
    })
    return response.data
  },

  login: async (email: string, password: string) => {
    // Backend expects OAuth2PasswordRequestForm (form data) with username field
    // But we're using email as the username value
    const formData = new URLSearchParams()
    formData.append('username', email)  // OAuth2 uses 'username' field but we send email
    formData.append('password', password)
    
    const response = await apiClient.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/api/auth/me')
    return response.data
  },
}

// Invoice API
export const invoiceAPI = {
  upload: async (file: File): Promise<VendorInvoice> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/api/invoices/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  list: async (): Promise<VendorInvoice[]> => {
    const response = await apiClient.get('/api/invoices')
    return response.data
  },

  get: async (id: number): Promise<VendorInvoice> => {
    const response = await apiClient.get(`/api/invoices/${id}`)
    return response.data
  },

  update: async (id: number, data: Partial<VendorInvoice>): Promise<VendorInvoice> => {
    const response = await apiClient.patch(`/api/invoices/${id}`, data)
    return response.data
  },
}

// Sync API
export const syncAPI = {
  sync: async (vendorInvoiceId: number, poNumber: string): Promise<SyncResponse> => {
    const response = await apiClient.post('/api/sync', {
      vendor_invoice_id: vendorInvoiceId,
      po_number: poNumber,
    })
    return response.data
  },

  getPurchaseOrder: async (poNumber: string): Promise<any> => {
    const response = await apiClient.get(`/api/sync/purchase-order/${poNumber}`)
    return response.data
  },
}

// Analytics API
export const analyticsAPI = {
  getDashboard: async (): Promise<DashboardStats> => {
    const response = await apiClient.get('/api/analytics/dashboard')
    return response.data
  },
}

export default apiClient

