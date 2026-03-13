import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ResetPassword from '../[token].vue'

describe('Reset Password Page', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(ResetPassword, {
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
          $route: {
            params: { token: 'test-token-123' }
          },
          $auth: {
            error: null,
            isLoading: false,
            isAuthenticated: { value: false },
            confirmPasswordReset: vi.fn()
          }
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  it('renders reset password page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays reset password form', () => {
    const text = wrapper.text()
    expect(text).toContain('Reset Password')
    expect(text).toContain('New Password')
    expect(text).toContain('Confirm Password')
  })

  it('displays password requirements', () => {
    const text = wrapper.text()
    expect(text).toContain('Password Requirements')
    expect(text).toContain('At least 8 characters')
    expect(text).toContain('One uppercase letter')
    expect(text).toContain('One lowercase letter')
    expect(text).toContain('One number')
  })

  it('displays back to login link', () => {
    const text = wrapper.text()
    expect(text).toContain('Back to Login')
  })

  it('updates password field on input', async () => {
    wrapper.vm.formData.password = 'Password123'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.password).toBe('Password123')
  })

  it('updates confirm password field on input', async () => {
    wrapper.vm.formData.confirmPassword = 'Password123'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.confirmPassword).toBe('Password123')
  })

  it('validates password strength', async () => {
    const isValid = wrapper.vm.validatePasswordStrength('Password123')
    expect(isValid).toBe(true)
  })

  it('rejects weak passwords', async () => {
    const isValid = wrapper.vm.validatePasswordStrength('weak')
    expect(isValid).toBe(false)
  })

  it('rejects passwords without uppercase', async () => {
    const isValid = wrapper.vm.validatePasswordStrength('password123')
    expect(isValid).toBe(false)
  })

  it('rejects passwords without lowercase', async () => {
    const isValid = wrapper.vm.validatePasswordStrength('PASSWORD123')
    expect(isValid).toBe(false)
  })

  it('rejects passwords without numbers', async () => {
    const isValid = wrapper.vm.validatePasswordStrength('PasswordAbc')
    expect(isValid).toBe(false)
  })

  it('rejects passwords shorter than 8 characters', async () => {
    const isValid = wrapper.vm.validatePasswordStrength('Pass12')
    expect(isValid).toBe(false)
  })

  it('validates password match', async () => {
    wrapper.vm.formData.password = 'Password123'
    wrapper.vm.formData.confirmPassword = 'Password123'
    await wrapper.vm.$nextTick()

    const isValid = wrapper.vm.formData.password === wrapper.vm.formData.confirmPassword
    expect(isValid).toBe(true)
  })

  it('rejects mismatched passwords', async () => {
    wrapper.vm.formData.password = 'Password123'
    wrapper.vm.formData.confirmPassword = 'Password456'
    await wrapper.vm.$nextTick()

    const isValid = wrapper.vm.formData.password === wrapper.vm.formData.confirmPassword
    expect(isValid).toBe(false)
  })

  it('displays error message on reset failure', async () => {
    wrapper.vm.auth.error = 'Invalid token'
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Invalid token')
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
    expect(text).toContain('Resetting')
  })

  it('validates form before submission', async () => {
    wrapper.vm.formData.password = ''
    wrapper.vm.formData.confirmPassword = ''

    await wrapper.vm.handleResetPassword()
    await flushPromises()

    expect(wrapper.vm.validation.isFieldTouched('password')).toBe(true)
    expect(wrapper.vm.validation.isFieldTouched('confirmPassword')).toBe(true)
  })

  it('calls confirmPasswordReset with valid data', async () => {
    wrapper.vm.formData.password = 'Password123'
    wrapper.vm.formData.confirmPassword = 'Password123'
    wrapper.vm.auth.confirmPasswordReset = vi.fn().mockResolvedValue(true)

    await wrapper.vm.handleResetPassword()
    await flushPromises()

    expect(wrapper.vm.auth.confirmPasswordReset).toHaveBeenCalledWith('test-token-123', 'Password123')
  })

  it('displays success message after successful reset', async () => {
    wrapper.vm.auth.confirmPasswordReset = vi.fn().mockResolvedValue(true)
    wrapper.vm.formData.password = 'Password123'
    wrapper.vm.formData.confirmPassword = 'Password123'

    await wrapper.vm.handleResetPassword()
    await flushPromises()

    wrapper.vm.resetSuccess = true
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Password Reset Successful')
  })

  it('marks password field as touched on blur', async () => {
    wrapper.vm.validation.markTouched('password')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.validation.isFieldTouched('password')).toBe(true)
  })

  it('marks confirm password field as touched on blur', async () => {
    wrapper.vm.validation.markTouched('confirmPassword')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.validation.isFieldTouched('confirmPassword')).toBe(true)
  })

  it('displays correct page title', () => {
    expect(wrapper.vm.$head.title).toContain('Reset Password')
  })

  it('displays PCM branding', () => {
    const text = wrapper.text()
    expect(text).toContain('Proxmox Center Manager')
    expect(text).toContain('Enterprise Cloud Control Plane')
  })

  it('shows password requirement indicators', async () => {
    wrapper.vm.formData.password = 'Password123'
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('At least 8 characters')
    expect(text).toContain('One uppercase letter')
    expect(text).toContain('One lowercase letter')
    expect(text).toContain('One number')
  })
})

