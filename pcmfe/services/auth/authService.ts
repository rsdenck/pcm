/**
 * Authentication Service
 * Handles user authentication, login, logout, and token refresh
 * Integrates with backend API for authentication
 */

import { tokenManager, TokenManager } from './tokenManager'

interface LoginCredentials {
  email: string
  password: string
}

interface AuthResponse {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
  user: {
    id: string
    email: string
    name: string
    roles: string[]
    permissions: string[]
    tenant_id: string
  }
}

interface RefreshResponse {
  access_token: string
  expires_in: number
  token_type: string
}

export class AuthService {
  private apiBase: string
  private tokenManager: TokenManager

  constructor(apiBase: string = '/api/v1') {
    this.apiBase = apiBase
    this.tokenManager = tokenManager
  }

  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.apiBase}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data: AuthResponse = await response.json()

      // Store tokens
      this.tokenManager.setTokens({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in,
        tokenType: data.token_type
      })

      return data
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      const token = this.tokenManager.getAccessToken()
      if (token) {
        await fetch(`${this.apiBase}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      this.tokenManager.clearTokens()
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<RefreshResponse> {
    try {
      const refreshToken = this.tokenManager.getRefreshToken()
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      const response = await fetch(`${this.apiBase}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data: RefreshResponse = await response.json()

      // Update tokens
      this.tokenManager.setTokens({
        accessToken: data.access_token,
        refreshToken: refreshToken, // Keep the same refresh token
        expiresIn: data.expires_in,
        tokenType: data.token_type
      })

      return data
    } catch (error) {
      console.error('Token refresh error:', error)
      this.tokenManager.clearTokens()
      throw error
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !this.tokenManager.isTokenExpired() && this.tokenManager.getAccessToken() !== null
  }

  /**
   * Get current user information from token
   */
  getCurrentUser() {
    return this.tokenManager.getTokenInfo()
  }

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return this.tokenManager.getAccessToken()
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    try {
      const response = await fetch(`${this.apiBase}/auth/password-reset/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Password reset request failed')
      }
    } catch (error) {
      console.error('Password reset request error:', error)
      throw error
    }
  }

  /**
   * Confirm password reset
   */
  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    try {
      const response = await fetch(`${this.apiBase}/auth/password-reset/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token, new_password: newPassword })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Password reset failed')
      }
    } catch (error) {
      console.error('Password reset error:', error)
      throw error
    }
  }

  /**
   * Validate token
   */
  async validateToken(): Promise<boolean> {
    try {
      const token = this.tokenManager.getAccessToken()
      if (!token) {
        return false
      }

      const response = await fetch(`${this.apiBase}/auth/validate`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      return response.ok
    } catch (error) {
      console.error('Token validation error:', error)
      return false
    }
  }
}

// Export singleton instance
export const authService = new AuthService()
