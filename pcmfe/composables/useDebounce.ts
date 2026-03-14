/**
 * Composable para debounce de funções
 * Previne múltiplos cliques e requisições duplicadas
 */

import { ref } from 'vue'

export const useDebounce = () => {
  const debounceTimers = ref<Map<string, NodeJS.Timeout>>(new Map())

  /**
   * Executa função com debounce
   */
  const debounce = async <T = any>(
    fn: () => Promise<T> | T,
    delay: number = 500,
    key: string = 'default'
  ): Promise<T | null> => {
    // Limpar timer anterior
    const existingTimer = debounceTimers.value.get(key)
    if (existingTimer) {
      clearTimeout(existingTimer)
    }

    return new Promise((resolve) => {
      const timer = setTimeout(async () => {
        try {
          const result = await fn()
          resolve(result)
        } catch (error) {
          console.error('Debounced function error:', error)
          resolve(null)
        } finally {
          debounceTimers.value.delete(key)
        }
      }, delay)

      debounceTimers.value.set(key, timer)
    })
  }

  /**
   * Cancelar debounce
   */
  const cancel = (key: string = 'default') => {
    const timer = debounceTimers.value.get(key)
    if (timer) {
      clearTimeout(timer)
      debounceTimers.value.delete(key)
    }
  }

  /**
   * Cancelar todos os debounces
   */
  const cancelAll = () => {
    debounceTimers.value.forEach(timer => {
      clearTimeout(timer)
    })
    debounceTimers.value.clear()
  }

  return {
    debounce,
    cancel,
    cancelAll
  }
}
