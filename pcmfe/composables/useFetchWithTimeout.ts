/**
 * Composable para requisições com timeout e abort controller
 * Previne loading infinito e requisições órfãs
 */

import { ref } from 'vue'

const DEFAULT_TIMEOUT = 30000 // 30 segundos

interface FetchOptions {
  timeout?: number
  method?: string
  body?: any
  headers?: Record<string, string>
  query?: Record<string, any>
}

export const useFetchWithTimeout = () => {
  const abortControllers = ref<Map<string, AbortController>>(new Map())

  /**
   * Executa fetch com timeout e abort controller
   */
  const fetchWithTimeout = async <T = any>(
    url: string,
    options: FetchOptions = {}
  ): Promise<T> => {
    const timeout = options.timeout || DEFAULT_TIMEOUT
    const controller = new AbortController()
    const requestId = `${url}-${Date.now()}`

    // Armazenar controller para limpeza posterior
    abortControllers.value.set(requestId, controller)

    try {
      // Criar timeout
      const timeoutId = setTimeout(() => {
        controller.abort()
      }, timeout)

      // Executar fetch
      const response = await $fetch<T>(url, {
        ...options,
        signal: controller.signal
      })

      clearTimeout(timeoutId)
      return response
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeout}ms`)
      }
      throw error
    } finally {
      // Limpar controller
      abortControllers.value.delete(requestId)
    }
  }

  /**
   * Cancelar todas as requisições pendentes
   */
  const cancelAll = () => {
    abortControllers.value.forEach(controller => {
      controller.abort()
    })
    abortControllers.value.clear()
  }

  /**
   * Cancelar requisição específica
   */
  const cancel = (requestId: string) => {
    const controller = abortControllers.value.get(requestId)
    if (controller) {
      controller.abort()
      abortControllers.value.delete(requestId)
    }
  }

  return {
    fetchWithTimeout,
    cancelAll,
    cancel
  }
}
