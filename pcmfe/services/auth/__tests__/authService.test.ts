/**
 * Auth Service Tests
 * Tests for user authentication, login, logout, and token refresh
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { AuthService } from '../authService'

describe('AuthService', () => {
  let authService: AuthService
  let fetchMock: any

  beforeEach(() => {
    authService = new AuthService()
    fetchMock = vi.fn()
    global.fetch = fetchMock

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
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_456',
        expires_in: 3600,
        token_type: 'Bearer',
        user: {
          id: 'user123',
          email: 'user@example.com',
          name: 'Test User',
          roles: ['user'],
          permissions: ['read'],
          tenant_id: 'tenant123'
        }
      }

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await authService.login({
        email: 'user@example.com',
        password: 'password123'
      })

      expect(result).toEqual(mockResponse)
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/v1/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      )
    })

    it('should throw error on login failure', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid credentials' })
      })

      await expect(
        authService.login({
          email: 'user@example.com',
          password: 'wrongpassword'
        })
      ).rejects.toThrow('Invalid credentials')
    })
  })

  describe('logout', () => {
    it('should logout successfully', async () => {
      // First login
      const mockLoginResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_456',
        expires_in: 3600,
        token_type: 'Bearer',
        user: {
          id: 'user123',
          email: 'user@example.com',
          name: 'Test User',
          roles: ['user'],
          permissions: ['read'],
          tenant_id: 'tenant123'
        }
      }

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLoginResponse
      })

      await authService.login({
        email: 'user@example.com',
        password: 'password123'
      })

      // Then logout
      fetchMock.mockResolvedValueOnce({
        ok: true
      })

      await authService.logout()

      expect(authService.isAuthenticated()).toBe(false)
    })
  })

  describe('isAuthenticated', () => {
    it('should return false if not logged in', () => {
      expect(authService.isAuthenticated()).toBe(false)
    })

    it('should return true if logged in', async () => {
      const mockResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_456',
        expires_in: 3600,
        token_type: 'Bearer',
        user: {
          id: 'user123',
          email: 'user@example.com',
          name: 'Test User',
          roles: ['user'],
          permissions: ['read'],
          tenant_id: 'tenant123'
        }
      }

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      await authService.login({
        email: 'user@example.com',
        password: 'password123'
      })

      expect(authService.isAuthenticated()).toBe(true)
    })
  })

  describe('getCurrentUser', () => {
    it('should return null if not authenticated', () => {
      expect(authService.getCurrentUser()).toBeNull()
    })

    it('should return user info if authenticated', async () => {
      const mockResponse = {
        access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZXMiOlsidXNlciJdLCJwZXJtaXNzaW9ucyI6WyJyZWFkIl0sInRlbmFudF9pZCI6InRlbmFudDEyMyJ9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ',
        refresh_token: 'refresh_token_456',
        expires_in: 3600,
        token_type: 'Bearer',
        user: {
          id: 'user123',
          email: 'user@example.com',
          name: 'Test User',
          roles: ['user'],
          permissions: ['read'],
          tenant_id: 'tenant123'
        }
      }

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      await authService.login({
        email: 'user@example.com',
        password: 'password123'
      })

      const user = authService.getCurrentUser()
      expect(user).not.toBeNull()
      expect(user?.sub).toBe('user123')
    })
  })

  describe('requestPasswordReset', () => {
    it('should request password reset successfully', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true
      })

      await authService.requestPasswordReset('user@example.com')

      expect(fetchMock).toHaveBeenCalledWith(
        '/api/v1/auth/password-reset/request',
        expect.objectContaining({
          method: 'POST'
        })
      )
    })

    it('should throw error on password reset request failure', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'User not found' })
      })

      await expect(
        authService.requestPasswordReset('nonexistent@example.com')
      ).rejects.toThrow('User not found')
    })
  })

  describe('validateToken', () => {
    it('should return false if not authenticated', async () => {
      const result = await authService.validateToken()
      expect(result).toBe(false)
    })

    it('should return true if token is valid', async () => {
      // First login
      const mockLoginResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_456',
        expires_in: 3600,
        token_type: 'Bearer',
        user: {
          id: 'user123',
          email: 'user@example.com',
          name: 'Test User',
          roles: ['user'],
          permissions: ['read'],
          tenant_id: 'tenant123'
        }
      }

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLoginResponse
      })

      await authService.login({
        email: 'user@example.com',
        password: 'password123'
      })

      // Then validate
      fetchMock.mockResolvedValueOnce({
        ok: true
      })

      const result = await authService.validateToken()
      expect(result).toBe(true)
    })
  })
})
