/**
 * Token Manager Service
 * Handles JWT token storage, retrieval, refresh, and validation
 * Implements secure token management with automatic refresh
 */

interface TokenPair {
  accessToken: string
  refreshToken: string
  expiresIn: number
  tokenType: string
}

interface DecodedToken {
  sub: string
  email: string
  roles: string[]
  permissions: string[]
  tenant_id: string
  exp: number
  iat: number
}

const TOKEN_STORAGE_KEY = 'pcm_auth_tokens'
const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000 // 5 minutes before expiration

export class TokenManager {
  private accessToken: string | null = null
  private refreshToken: string | null = null
  private tokenExpiresAt: number | null = null
  private refreshTimeout: NodeJS.Timeout | null = null

  constructor() {
    this.loadTokensFromStorage()
  }

  /**
   * Store tokens securely
   */
  setTokens(tokens: TokenPair): void {
    this.accessToken = tokens.accessToken
    this.refreshToken = tokens.refreshToken
    this.tokenExpiresAt = Date.now() + tokens.expiresIn * 1000

    // Store in secure storage (HttpOnly cookie would be ideal, but using localStorage for now)
    if (typeof window !== 'undefined') {
      try {
        sessionStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify({
          accessToken: this.accessToken,
          refreshToken: this.refreshToken,
          expiresAt: this.tokenExpiresAt
        }))
      } catch (error) {
        console.error('Failed to store tokens:', error)
      }
    }

    // Schedule automatic token refresh
    this.scheduleTokenRefresh()
  }

  /**
   * Get current access token
   */
  getAccessToken(): string | null {
    if (this.isTokenExpired()) {
      return null
    }
    return this.accessToken
  }

  /**
   * Get refresh token
   */
  getRefreshToken(): string | null {
    return this.refreshToken
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(): boolean {
    if (!this.tokenExpiresAt) {
      return true
    }
    return Date.now() >= this.tokenExpiresAt
  }

  /**
   * Check if token should be refreshed (within threshold)
   */
  shouldRefreshToken(): boolean {
    if (!this.tokenExpiresAt) {
      return false
    }
    return Date.now() >= this.tokenExpiresAt - TOKEN_REFRESH_THRESHOLD
  }

  /**
   * Decode JWT token (without verification - for client-side use only)
   */
  decodeToken(token: string): DecodedToken | null {
    try {
      const parts = token.split('.')
      if (parts.length !== 3) {
        return null
      }

      const decoded = JSON.parse(
        atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'))
      )
      return decoded as DecodedToken
    } catch (error) {
      console.error('Failed to decode token:', error)
      return null
    }
  }

  /**
   * Get decoded token information
   */
  getTokenInfo(): DecodedToken | null {
    if (!this.accessToken) {
      return null
    }
    return this.decodeToken(this.accessToken)
  }

  /**
   * Clear all tokens
   */
  clearTokens(): void {
    this.accessToken = null
    this.refreshToken = null
    this.tokenExpiresAt = null

    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout)
      this.refreshTimeout = null
    }

    if (typeof window !== 'undefined') {
      try {
        sessionStorage.removeItem(TOKEN_STORAGE_KEY)
      } catch (error) {
        console.error('Failed to clear tokens:', error)
      }
    }
  }

  /**
   * Load tokens from storage
   */
  private loadTokensFromStorage(): void {
    if (typeof window === 'undefined') {
      return
    }

    try {
      const stored = sessionStorage.getItem(TOKEN_STORAGE_KEY)
      if (stored) {
        const { accessToken, refreshToken, expiresAt } = JSON.parse(stored)
        this.accessToken = accessToken
        this.refreshToken = refreshToken
        this.tokenExpiresAt = expiresAt

        // Schedule refresh if token is still valid
        if (!this.isTokenExpired()) {
          this.scheduleTokenRefresh()
        }
      }
    } catch (error) {
      console.error('Failed to load tokens from storage:', error)
      this.clearTokens()
    }
  }

  /**
   * Schedule automatic token refresh
   */
  private scheduleTokenRefresh(): void {
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout)
    }

    if (!this.tokenExpiresAt) {
      return
    }

    const timeUntilRefresh = this.tokenExpiresAt - TOKEN_REFRESH_THRESHOLD - Date.now()
    if (timeUntilRefresh > 0) {
      this.refreshTimeout = setTimeout(() => {
        // Emit event for refresh - will be handled by auth service
        window.dispatchEvent(new CustomEvent('token-refresh-needed'))
      }, timeUntilRefresh)
    }
  }
}

// Export singleton instance
export const tokenManager = new TokenManager()
