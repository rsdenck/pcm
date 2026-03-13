/**
 * useFormValidation Composable
 * Provides form validation and error handling
 */

import { ref, computed } from 'vue'

interface ValidationRule {
  validate: (value: any) => boolean
  message: string
}

interface FieldError {
  field: string
  message: string
}

export const useFormValidation = () => {
  const errors = ref<Map<string, string>>(new Map())
  const touched = ref<Set<string>>(new Set())

  /**
   * Email validation rule
   */
  const emailRule: ValidationRule = {
    validate: (value: string) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value)
    },
    message: 'Please enter a valid email address'
  }

  /**
   * Password validation rule (minimum 8 characters, at least one uppercase, one lowercase, one number)
   */
  const passwordRule: ValidationRule = {
    validate: (value: string) => {
      if (value.length < 8) return false
      if (!/[A-Z]/.test(value)) return false
      if (!/[a-z]/.test(value)) return false
      if (!/[0-9]/.test(value)) return false
      return true
    },
    message: 'Password must be at least 8 characters with uppercase, lowercase, and numbers'
  }

  /**
   * Required field validation rule
   */
  const requiredRule: ValidationRule = {
    validate: (value: any) => {
      if (typeof value === 'string') {
        return value.trim().length > 0
      }
      return value !== null && value !== undefined
    },
    message: 'This field is required'
  }

  /**
   * Minimum length validation rule
   */
  const minLengthRule = (length: number): ValidationRule => ({
    validate: (value: string) => value.length >= length,
    message: `Minimum length is ${length} characters`
  })

  /**
   * Maximum length validation rule
   */
  const maxLengthRule = (length: number): ValidationRule => ({
    validate: (value: string) => value.length <= length,
    message: `Maximum length is ${length} characters`
  })

  /**
   * Validate a single field
   */
  const validateField = (fieldName: string, value: any, rules: ValidationRule[]): boolean => {
    for (const rule of rules) {
      if (!rule.validate(value)) {
        errors.value.set(fieldName, rule.message)
        return false
      }
    }
    errors.value.delete(fieldName)
    return true
  }

  /**
   * Validate multiple fields
   */
  const validateFields = (fields: Record<string, { value: any; rules: ValidationRule[] }>): boolean => {
    let isValid = true
    errors.value.clear()

    for (const [fieldName, { value, rules }] of Object.entries(fields)) {
      if (!validateField(fieldName, value, rules)) {
        isValid = false
      }
    }

    return isValid
  }

  /**
   * Mark field as touched
   */
  const markTouched = (fieldName: string) => {
    touched.value.add(fieldName)
  }

  /**
   * Mark all fields as touched
   */
  const markAllTouched = () => {
    errors.value.forEach((_, fieldName) => {
      touched.value.add(fieldName)
    })
  }

  /**
   * Clear field error
   */
  const clearFieldError = (fieldName: string) => {
    errors.value.delete(fieldName)
  }

  /**
   * Clear all errors
   */
  const clearErrors = () => {
    errors.value.clear()
  }

  /**
   * Reset form state
   */
  const reset = () => {
    errors.value.clear()
    touched.value.clear()
  }

  /**
   * Get field error
   */
  const getFieldError = (fieldName: string): string | null => {
    return errors.value.get(fieldName) || null
  }

  /**
   * Check if field has error
   */
  const hasFieldError = (fieldName: string): boolean => {
    return errors.value.has(fieldName)
  }

  /**
   * Check if field is touched
   */
  const isFieldTouched = (fieldName: string): boolean => {
    return touched.value.has(fieldName)
  }

  /**
   * Check if form is valid
   */
  const isFormValid = computed(() => errors.value.size === 0)

  /**
   * Get all errors
   */
  const getAllErrors = computed(() => {
    const errorList: FieldError[] = []
    errors.value.forEach((message, field) => {
      errorList.push({ field, message })
    })
    return errorList
  })

  return {
    // State
    errors,
    touched,

    // Rules
    emailRule,
    passwordRule,
    requiredRule,
    minLengthRule,
    maxLengthRule,

    // Methods
    validateField,
    validateFields,
    markTouched,
    markAllTouched,
    clearFieldError,
    clearErrors,
    reset,
    getFieldError,
    hasFieldError,
    isFieldTouched,

    // Computed
    isFormValid,
    getAllErrors
  }
}
