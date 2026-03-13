/**
 * Session Manager Service
 * Handles user session tracking, inactivity detection, and timeout management
 */

interface SessionConfig {
  inactivityTimeout: number // milliseconds
  warningTimeout: number // milliseconds before logout
  checkInterval: number // milliseconds between checks
}

const DEFAULT_CONFIG: SessionConfig = {
  inactivityTimeout: 30 * 60 * 1000, // 30 minutes
  warningTimeout: 5 * 60 * 1000, // 5 minutes before logout
  checkInterval: 1 * 60 * 1000 // Check every minute
}

export class SessionManager {
  private config: SessionConfig
  private lastActivityTime: number = Date.now()
  private inactivityTimer: NodeJS.Timeout | null = null
  private warningTimer: NodeJS.Timeout | null = null
  private checkInterval: NodeJS.Timeout | null = null
  private isWarningShown: boolean = false
  private listeners: Map<string, Function[]> = new Map()

  constructor(config: Partial<SessionConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
    this.setupActivityListeners()
  }

  /**
   * Start session monitoring
   */
  start(): void {
    this.resetInactivityTimer()
    this.startCheckInterval()
  }

  /**
   * Stop session monitoring
   */
  stop(): void {
    this.clearTimers()
  }

  /**
   * Record user activity
   */
  recordActivity(): void {
    this.lastActivityTime = Date.now()
    this.isWarningShown = false
    this.resetInactivityTimer()
  }

  /**
   * Get time until session timeout
   */
  getTimeUntilTimeout(): number {
    const timeElapsed = Date.now() - this.lastActivityTime
    const timeRemaining = this.config.inactivityTimeout - timeElapsed
    return Math.max(0, timeRemaining)
  }

  /**
   * Get time until warning
   */
  getTimeUntilWarning(): number {
    const timeUntilTimeout = this.getTimeUntilTimeout()
    const timeUntilWarning = timeUntilTimeout - this.config.warningTimeout
    return Math.max(0, timeUntilWarning)
  }

  /**
   * Check if session is about to expire
   */
  isAboutToExpire(): boolean {
    return this.getTimeUntilTimeout() <= this.config.warningTimeout
  }

  /**
   * Check if session has expired
   */
  hasExpired(): boolean {
    return this.getTimeUntilTimeout() <= 0
  }

  /**
   * Extend session
   */
  extendSession(): void {
    this.recordActivity()
    this.emit('session-extended')
  }

  /**
   * Setup activity listeners
   */
  private setupActivityListeners(): void {
    if (typeof window === 'undefined') {
      return
    }

    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click']
    const handler = () => this.recordActivity()

    activityEvents.forEach(event => {
      window.addEventListener(event, handler, true)
    })
  }

  /**
   * Reset inactivity timer
   */
  private resetInactivityTimer(): void {
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer)
    }

    if (this.warningTimer) {
      clearTimeout(this.warningTimer)
    }

    // Set warning timer
    this.warningTimer = setTimeout(() => {
      if (!this.isWarningShown) {
        this.isWarningShown = true
        this.emit('session-warning')
      }
    }, this.config.inactivityTimeout - this.config.warningTimeout)

    // Set logout timer
    this.inactivityTimer = setTimeout(() => {
      this.emit('session-expired')
    }, this.config.inactivityTimeout)
  }

  /**
   * Start periodic check interval
   */
  private startCheckInterval(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
    }

    this.checkInterval = setInterval(() => {
      if (this.hasExpired()) {
        this.emit('session-expired')
      } else if (this.isAboutToExpire() && !this.isWarningShown) {
        this.isWarningShown = true
        this.emit('session-warning')
      }
    }, this.config.checkInterval)
  }

  /**
   * Clear all timers
   */
  private clearTimers(): void {
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer)
      this.inactivityTimer = null
    }

    if (this.warningTimer) {
      clearTimeout(this.warningTimer)
      this.warningTimer = null
    }

    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }
  }

  /**
   * Register event listener
   */
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(callback)
  }

  /**
   * Unregister event listener
   */
  off(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      return
    }
    const callbacks = this.listeners.get(event)!
    const index = callbacks.indexOf(callback)
    if (index > -1) {
      callbacks.splice(index, 1)
    }
  }

  /**
   * Emit event
   */
  private emit(event: string, data?: any): void {
    if (!this.listeners.has(event)) {
      return
    }
    this.listeners.get(event)!.forEach(callback => callback(data))
  }
}

// Export singleton instance
export const sessionManager = new SessionManager()
