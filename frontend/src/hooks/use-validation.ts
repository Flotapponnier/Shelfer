"use client"

import { useState, useCallback } from "react"
import { ValidationState, type FieldValidation, type ValidationAction } from "../../types/validation"

export function useValidation() {
  const [validationStates, setValidationStates] = useState<FieldValidation>({})

  const handleValidation = useCallback((action: ValidationAction) => {
    setValidationStates((prev) => ({
      ...prev,
      [action.fieldPath]: action.type === "APPROVE" ? ValidationState.APPROVED : ValidationState.DECLINED,
    }))
  }, [])

  const getValidationState = useCallback(
    (fieldPath: string): ValidationState => {
      return validationStates[fieldPath] || ValidationState.PENDING
    },
    [validationStates],
  )

  const resetValidation = useCallback(() => {
    setValidationStates({})
  }, [])

  return {
    validationStates,
    handleValidation,
    getValidationState,
    resetValidation,
  }
}
