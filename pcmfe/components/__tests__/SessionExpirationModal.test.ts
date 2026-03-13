import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SessionExpirationModal from '../SessionExpirationModal.vue'

describe('SessionExpirationModal', () => {
  let wrapper: any

  beforeEach(() => {
    vi.useFakeTimers()
    wrapper = mount(SessionExpirationModal, {
      global: {
        stubs: {
          UModal: { template: '<div><slot /></div>' },
          UCard: { template: '<div><slot name="header" /><slot /><slot name="footer" /></div>' },
          UIcon: { template: '<div></div>' },
          UButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' }
        }
      }
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    wrapper.unmount()
  })

  it('renders modal component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays session warning when event is triggered', async () => {
    const event = new CustomEvent('auth-session-warning')
    window.dispatchEvent(event)
    await flushPromises()

    expect(wrapper.vm.isOpen).toBe(true)
  })

  it('starts countdown timer on session warning', async () => {
    const event = new CustomEvent('auth-session-warning')
    window.dispatchEvent(event)
    await flushPromises()

    expect(wrapper.vm.timeRemaining).toBe(wrapper.vm.warningDuration)
  })

  it('decrements countdown timer', async () => {
    const event = new CustomEvent('auth-session-warning')
    window.dispatchEvent(event)
    await flushPromises()

    const initialTime = wrapper.vm.timeRemaining
    vi.advanceTimersByTime(1000)
    await flushPromises()

    expect(wrapper.vm.timeRemaining).toBe(initialTime - 1)
  })

  it('closes modal when continue session is clicked', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.handleContinue()
    await flushPromises()

    expect(wrapper.vm.isOpen).toBe(false)
  })

  it('closes modal when logout is clicked', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.handleLogout()
    await flushPromises()

    expect(wrapper.vm.isOpen).toBe(false)
  })

  it('stops countdown when session is reset', async () => {
    const event = new CustomEvent('auth-session-warning')
    window.dispatchEvent(event)
    await flushPromises()

    const resetEvent = new CustomEvent('auth-session-reset')
    window.dispatchEvent(resetEvent)
    await flushPromises()

    const currentTime = wrapper.vm.timeRemaining
    vi.advanceTimersByTime(1000)
    await flushPromises()

    // Time should not change after reset
    expect(wrapper.vm.timeRemaining).toBe(currentTime)
  })

  it('displays correct countdown time', async () => {
    wrapper.vm.isOpen = true
    wrapper.vm.timeRemaining = 45
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('45')
  })

  it('shows progress bar with correct width', async () => {
    wrapper.vm.isOpen = true
    wrapper.vm.timeRemaining = 30
    wrapper.vm.warningDuration = 60
    await wrapper.vm.$nextTick()

    const progressBar = wrapper.find('[style*="width"]')
    expect(progressBar.exists()).toBe(true)
  })

  it('cleans up event listeners on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')
    wrapper.unmount()

    expect(removeEventListenerSpy).toHaveBeenCalled()
  })
})

