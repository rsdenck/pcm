/**
 * Token Manager Tests
 * Tests for JWT token storage, retrieval, refresh, and validation
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { TokenManager } from '../tokenManager'

describe('TokenManager', () => {
  let tokenManager: TokenManager

  beforeEach(() => {
    tokenManager = new TokenManager()
    // Mock sessionStorage
    const store: Record<string, string> = {}
    global.sessionStorage = {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value
      },
      removeItem: (key: string) => {
        delete store[key]
      },
      clear: () => {
        Object.keys(store).forEach(key => delete store[key])
      },
      length: 0,
      key: () => null
    } as any
  })

  afterEach(() => {
    tokenManager.clearTokens()
  })

  describe('setTokens', () => {
    it('should store tokens correctly', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: 3600,
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)

      expect(tokenManager.getAccessToken()).toBe('access_token_123')
      expect(tokenManager.getRefreshToken()).toBe('refresh_token_456')
    })

    it('should calculate expiration time correctly', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: 3600,
        tokenType: 'Bearer'
      }

      const beforeTime = Date.now()
      tokenManager.setTokens(tokens)
      const afterTime = Date.now()

      expect(tokenManager.isTokenExpired()).toBe(false)
    })
  })

  describe('getAccessToken', () => {
    it('should return null if no token is set', () => {
      expect(tokenManager.getAccessToken()).toBeNull()
    })

    it('should return token if valid', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: 3600,
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)
      expect(tokenManager.getAccessToken()).toBe('access_token_123')
    })

    it('should return null if token is expired', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: -1, // Already expired
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)
      expect(tokenManager.getAccessToken()).toBeNull()
    })
  })

  describe('isTokenExpired', () => {
    it('should return true if no token is set', () => {
      expect(tokenManager.isTokenExpired()).toBe(true)
    })

    it('should return false if token is valid', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: 3600,
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)
      expect(tokenManager.isTokenExpired()).toBe(false)
    })

    it('should return true if token is expired', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: -1,
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)
      expect(tokenManager.isTokenExpired()).toBe(true)
    })
  })

  describe('shouldRefreshToken', () => {
    it('should return false if no token is set', () => {
      expect(tokenManager.shouldRefreshToken()).toBe(false)
    })

    it('should return false if token is not near expiration', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: 3600,
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)
      expect(tokenManager.shouldRefreshToken()).toBe(false)
    })

    it('should return true if token is near expiration', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: 200, // Less than 5 minutes
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)
      expect(tokenManager.shouldRefreshToken()).toBe(true)
    })
  })

  describe('decodeToken', () => {
    it('should decode valid JWT token', () => {
      // Valid JWT with payload: { sub: 'user123', email: 'user@example.com' }
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIn0.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ'

      const decoded = tokenManager.decodeToken(token)
      expect(decoded).not.toBeNull()
      expect(decoded?.sub).toBe('user123')
      expect(decoded?.email).toBe('user@example.com')
    })

    it('should return null for invalid token', () => {
      const decoded = tokenManager.decodeToken('invalid.token')
      expect(decoded).toBeNull()
    })

    it('should return null for malformed token', () => {
      const decoded = tokenManager.decodeToken('not-a-jwt')
      expect(decoded).toBeNull()
    })
  })

  describe('clearTokens', () => {
    it('should clear all tokens', () => {
      const tokens = {
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_456',
        expiresIn: 3600,
        tokenType: 'Bearer'
      }

      tokenManager.setTokens(tokens)
      tokenManager.clearTokens()

      expect(tokenManager.getAccessToken()).toBeNull()
      expect(tokenManager.getRefreshToken()).toBeNull()
      expect(tokenManager.isTokenExpired()).toBe(true)
    })
  })
})
