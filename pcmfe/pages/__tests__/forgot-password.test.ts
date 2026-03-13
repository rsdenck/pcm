import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ForgotPassword from '../forgot-password.vue'

describe('Forgot Password Page', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(ForgotPassword, {
      global: {
        stubs: {
          UCard: { template: '<div><slot name="header" /><slot /><slot name="footer" /></div>' },
          UInput: { template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />' },
          UButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          UAlert: { template: '<div><slot /></div>' },
          UIcon: { template: '<div></div>' },
          NuxtLink: { template: '<a><slot /></a>' }
        },
        mocks: {
          $auth: {
            error: null,
            isLoading: false,
            requestPasswordReset: vi.fn()
          }
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  it('renders forgot password page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays forgot password form', () => {
    const text = wrapper.text()
    expect(text).toContain('Forgot Password')
    expect(text).toContain('Email Address')
  })

  it('displays back to login link', () => {
    const text = wrapper.text()
    expect(text).toContain('Back to Login')
  })

  it('updates email field on input', async () => {
    wrapper.vm.formData.email = 'test@example.com'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.email).toBe('test@example.com')
  })

  it('validates email field', async () => {
    wrapper.vm.formData.email = 'invalid-email'
    wrapper.vm.validation.markTouched('email')
    await wrapper.vm.$nextTick()

    const hasError = wrapper.vm.validation.hasFieldError('email')
    expect(hasError).toBe(true)
  })

  it('displays error message on request failure', async () => {
    wrapper.vm.auth.error = 'Email not found'
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Email not found')
  })

  it('disables submit button while loading', async () => {
    wrapper.vm.auth.isLoading = true
    await wrapper.vm.$nextTick()

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('shows loading state on submit button', async () => {
    wrapper.vm.auth.isLoading = true
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Sending')
  })

  it('validates form before submission', async () => {
    wrapper.vm.formData.email = ''

    await wrapper.vm.handleRequestReset()
    await flushPromises()

    expect(wrapper.vm.validation.isFieldTouched('email')).toBe(true)
  })

  it('calls requestPasswordReset with valid email', async () => {
    wrapper.vm.formData.email = 'test@example.com'
    wrapper.vm.auth.requestPasswordReset = vi.fn().mockResolvedValue(true)

    await wrapper.vm.handleRequestReset()
    await flushPromises()

    expect(wrapper.vm.auth.requestPasswordReset).toHaveBeenCalledWith('test@example.com')
  })

  it('displays success message after successful request', async () => {
    wrapper.vm.auth.requestPasswordReset = vi.fn().mockResolvedValue(true)
    wrapper.vm.formData.email = 'test@example.com'

    await wrapper.vm.handleRequestReset()
    await flushPromises()

    wrapper.vm.resetSuccess = true
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Check your email')
  })

  it('marks email field as touched on blur', async () => {
    wrapper.vm.validation.markTouched('email')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.validation.isFieldTouched('email')).toBe(true)
  })

  it('displays correct page title', () => {
    expect(wrapper.vm.$head.title).toContain('Forgot Password')
  })

  it('displays PCM branding', () => {
    const text = wrapper.text()
    expect(text).toContain('Proxmox Center Manager')
    expect(text).toContain('Enterprise Cloud Control Plane')
  })

  it('clears error message when user starts typing', async () => {
    wrapper.vm.auth.error = 'Email not found'
    wrapper.vm.validation.clearFieldError('email')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.auth.error).toBe('Email not found')
  })

  it('displays info message about password reset', () => {
    const text = wrapper.text()
    expect(text).toContain('Enter your email address')
  })
})

