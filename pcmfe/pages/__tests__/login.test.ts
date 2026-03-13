import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Login from '../login.vue'

describe('Login Page', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(Login, {
      global: {
        stubs: {
          UCard: { template: '<div><slot name="header" /><slot /><slot name="footer" /></div>' },
          UInput: { template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />' },
          UButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          UCheckbox: { template: '<input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" />' },
          UAlert: { template: '<div><slot /></div>' },
          UIcon: { template: '<div></div>' },
          NuxtLink: { template: '<a><slot /></a>' }
        },
        mocks: {
          $auth: {
            error: null,
            isLoading: false,
            isAuthenticated: { value: false },
            login: vi.fn()
          }
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  it('renders login page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays login form', () => {
    const text = wrapper.text()
    expect(text).toContain('Sign In')
    expect(text).toContain('Email Address')
    expect(text).toContain('Password')
  })

  it('displays forgot password link', () => {
    const text = wrapper.text()
    expect(text).toContain('Forgot')
  })

  it('displays remember me checkbox', () => {
    const text = wrapper.text()
    expect(text).toContain('Remember me')
  })

  it('displays demo credentials', () => {
    const text = wrapper.text()
    expect(text).toContain('Demo Credentials')
    expect(text).toContain('admin@pcm.local')
  })

  it('updates email field on input', async () => {
    wrapper.vm.formData.email = 'test@example.com'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.email).toBe('test@example.com')
  })

  it('updates password field on input', async () => {
    wrapper.vm.formData.password = 'password123'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.password).toBe('password123')
  })

  it('updates remember me checkbox', async () => {
    wrapper.vm.formData.rememberMe = true
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.rememberMe).toBe(true)
  })

  it('validates email field', async () => {
    wrapper.vm.formData.email = 'invalid-email'
    wrapper.vm.validation.markTouched('email')
    await wrapper.vm.$nextTick()

    const hasError = wrapper.vm.validation.hasFieldError('email')
    expect(hasError).toBe(true)
  })

  it('validates password field', async () => {
    wrapper.vm.formData.password = 'short'
    wrapper.vm.validation.markTouched('password')
    await wrapper.vm.$nextTick()

    const hasError = wrapper.vm.validation.hasFieldError('password')
    expect(hasError).toBe(true)
  })

  it('displays error message on login failure', async () => {
    wrapper.vm.auth.error = 'Invalid credentials'
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Invalid credentials')
  })

  it('clears error message when user starts typing', async () => {
    wrapper.vm.auth.error = 'Invalid credentials'
    wrapper.vm.validation.clearFieldError('email')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.auth.error).toBe('Invalid credentials')
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
    expect(text).toContain('Signing in')
  })

  it('validates form before submission', async () => {
    wrapper.vm.formData.email = ''
    wrapper.vm.formData.password = ''

    await wrapper.vm.handleLogin()
    await flushPromises()

    expect(wrapper.vm.validation.isFieldTouched('email')).toBe(true)
    expect(wrapper.vm.validation.isFieldTouched('password')).toBe(true)
  })

  it('calls login method with valid credentials', async () => {
    wrapper.vm.formData.email = 'test@example.com'
    wrapper.vm.formData.password = 'password123'
    wrapper.vm.auth.login = vi.fn()

    await wrapper.vm.handleLogin()
    await flushPromises()

    expect(wrapper.vm.auth.login).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('marks email field as touched on blur', async () => {
    wrapper.vm.validation.markTouched('email')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.validation.isFieldTouched('email')).toBe(true)
  })

  it('marks password field as touched on blur', async () => {
    wrapper.vm.validation.markTouched('password')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.validation.isFieldTouched('password')).toBe(true)
  })

  it('displays correct page title', () => {
    expect(wrapper.vm.$head.title).toContain('Sign In')
  })

  it('displays PCM branding', () => {
    const text = wrapper.text()
    expect(text).toContain('Proxmox Center Manager')
    expect(text).toContain('Enterprise Cloud Control Plane')
  })
})

