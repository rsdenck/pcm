/**
 * Session Manager Tests
 * Tests for session tracking, inactivity detection, and timeout management
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { SessionManager } from '../sessionManager'

describe('SessionManager', () => {
  let sessionManager: SessionManager

  beforeEach(() => {
    vi.useFakeTimers()
    sessionManager = new SessionManager({
      inactivityTimeout: 30 * 60 * 1000, // 30 minutes
      warningTimeout: 5 * 60 * 1000, // 5 minutes
      checkInterval: 1 * 60 * 1000 // 1 minute
    })
  })

  afterEach(() => {
    sessionManager.stop()
    vi.useRealTimers()
  })

  describe('recordActivity', () => {
    it('should update last activity time', () => {
      sessionManager.start()
      const initialTime = sessionManager.getTimeUntilTimeout()

      vi.advanceTimersByTime(5 * 60 * 1000) // 5 minutes
      sessionManager.recordActivity()

      const newTime = sessionManager.getTimeUntilTimeout()
      expect(newTime).toBeGreaterThan(initialTime)
    })

    it('should reset warning flag', () => {
      sessionManager.start()
      vi.advanceTimersByTime(26 * 60 * 1000) // 26 minutes (near timeout)

      sessionManager.recordActivity()
      expect(sessionManager.isAboutToExpire()).toBe(false)
    })
  })

  describe('getTimeUntilTimeout', () => {
    it('should return correct time remaining', () => {
      sessionManager.start()
      const timeRemaining = sessionManager.getTimeUntilTimeout()

      expect(timeRemaining).toBeLessThanOrEqual(30 * 60 * 1000)
      expect(timeRemaining).toBeGreaterThan(29 * 60 * 1000)
    })

    it('should decrease over time', () => {
      sessionManager.start()
      const initialTime = sessionManager.getTimeUntilTimeout()

      vi.advanceTimersByTime(5 * 60 * 1000) // 5 minutes
      const newTime = sessionManager.getTimeUntilTimeout()

      expect(newTime).toBeLessThan(initialTime)
    })

    it('should return 0 when expired', () => {
      sessionManager.start()
      vi.advanceTimersByTime(31 * 60 * 1000) // 31 minutes (past timeout)

      expect(sessionManager.getTimeUntilTimeout()).toBe(0)
    })
  })

  describe('isAboutToExpire', () => {
    it('should return false initially', () => {
      sessionManager.start()
      expect(sessionManager.isAboutToExpire()).toBe(false)
    })

    it('should return true when near expiration', () => {
      sessionManager.start()
      vi.advanceTimersByTime(26 * 60 * 1000) // 26 minutes (within 5 minute warning)

      expect(sessionManager.isAboutToExpire()).toBe(true)
    })

    it('should return false after activity', () => {
      sessionManager.start()
      vi.advanceTimersByTime(26 * 60 * 1000) // 26 minutes

      sessionManager.recordActivity()
      expect(sessionManager.isAboutToExpire()).toBe(false)
    })
  })

  describe('hasExpired', () => {
    it('should return false initially', () => {
      sessionManager.start()
      expect(sessionManager.hasExpired()).toBe(false)
    })

    it('should return true when expired', () => {
      sessionManager.start()
      vi.advanceTimersByTime(31 * 60 * 1000) // 31 minutes

      expect(sessionManager.hasExpired()).toBe(true)
    })

    it('should return false after activity', () => {
      sessionManager.start()
      vi.advanceTimersByTime(31 * 60 * 1000) // 31 minutes

      sessionManager.recordActivity()
      expect(sessionManager.hasExpired()).toBe(false)
    })
  })

  describe('extendSession', () => {
    it('should extend session and emit event', () => {
      sessionManager.start()
      const listener = vi.fn()
      sessionManager.on('session-extended', listener)

      vi.advanceTimersByTime(26 * 60 * 1000) // 26 minutes
      sessionManager.extendSession()

      expect(listener).toHaveBeenCalled()
      expect(sessionManager.isAboutToExpire()).toBe(false)
    })
  })

  describe('event listeners', () => {
    it('should emit session-warning event', () => {
      const listener = vi.fn()
      sessionManager.on('session-warning', listener)
      sessionManager.start()

      vi.advanceTimersByTime(26 * 60 * 1000) // 26 minutes (within warning threshold)

      expect(listener).toHaveBeenCalled()
    })

    it('should emit session-expired event', () => {
      const listener = vi.fn()
      sessionManager.on('session-expired', listener)
      sessionManager.start()

      vi.advanceTimersByTime(31 * 60 * 1000) // 31 minutes

      expect(listener).toHaveBeenCalled()
    })

    it('should allow removing listeners', () => {
      const listener = vi.fn()
      sessionManager.on('session-warning', listener)
      sessionManager.off('session-warning', listener)
      sessionManager.start()

      vi.advanceTimersByTime(26 * 60 * 1000)

      expect(listener).not.toHaveBeenCalled()
    })
  })

  describe('stop', () => {
    it('should stop session monitoring', () => {
      sessionManager.start()
      sessionManager.stop()

      const listener = vi.fn()
      sessionManager.on('session-expired', listener)

      vi.advanceTimersByTime(31 * 60 * 1000)

      expect(listener).not.toHaveBeenCalled()
    })
  })
})
