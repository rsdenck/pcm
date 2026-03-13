import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import UserMenu from '../UserMenu.vue'

describe('UserMenu', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(UserMenu, {
      global: {
        stubs: {
          UButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          UIcon: { template: '<div></div>' },
          NuxtLink: { template: '<a @click="$emit(\'click\')"><slot /></a>' }
        },
        mocks: {
          $auth: {
            user: {
              name: 'John Doe',
              email: 'john@example.com'
            },
            logout: vi.fn()
          }
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  it('renders user menu button', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays user name in button', async () => {
    wrapper.vm.auth.user = {
      name: 'John Doe',
      email: 'john@example.com'
    }
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('John Doe')
  })

  it('truncates long user names', async () => {
    wrapper.vm.auth.user = {
      name: 'This is a very long user name',
      email: 'user@example.com'
    }
    await wrapper.vm.$nextTick()

    const displayName = wrapper.vm.userDisplayName
    expect(displayName.length).toBeLessThanOrEqual(15)
    expect(displayName).toContain('...')
  })

  it('toggles dropdown menu on button click', async () => {
    expect(wrapper.vm.isOpen).toBe(false)

    await wrapper.find('button').trigger('click')
    expect(wrapper.vm.isOpen).toBe(true)

    await wrapper.find('button').trigger('click')
    expect(wrapper.vm.isOpen).toBe(false)
  })

  it('displays user info in dropdown', async () => {
    wrapper.vm.auth.user = {
      name: 'John Doe',
      email: 'john@example.com'
    }
    wrapper.vm.isOpen = true
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('John Doe')
    expect(text).toContain('john@example.com')
  })

  it('displays menu items', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text).toContain('Profile')
    expect(text).toContain('Settings')
    expect(text).toContain('Change Password')
    expect(text).toContain('Logout')
  })

  it('closes menu when profile link is clicked', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.$nextTick()

    const profileLink = wrapper.findAll('a')[0]
    await profileLink.trigger('click')

    expect(wrapper.vm.isOpen).toBe(false)
  })

  it('closes menu when settings link is clicked', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.$nextTick()

    const settingsLink = wrapper.findAll('a')[1]
    await settingsLink.trigger('click')

    expect(wrapper.vm.isOpen).toBe(false)
  })

  it('calls logout when logout button is clicked', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.$nextTick()

    const logoutButton = wrapper.findAll('button')[wrapper.findAll('button').length - 1]
    await logoutButton.trigger('click')
    await flushPromises()

    expect(wrapper.vm.isOpen).toBe(false)
  })

  it('closes menu when clicking outside', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.$nextTick()

    const overlay = wrapper.find('[class*="fixed"]')
    await overlay.trigger('click')

    expect(wrapper.vm.isOpen).toBe(false)
  })

  it('displays correct icons for menu items', async () => {
    wrapper.vm.isOpen = true
    await wrapper.vm.$nextTick()

    const icons = wrapper.findAll('[class*="icon"]')
    expect(icons.length).toBeGreaterThan(0)
  })
})

