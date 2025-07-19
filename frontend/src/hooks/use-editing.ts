"use client"

import { useState, useCallback } from "react"
import { JsonValue } from "../../types/json"

export interface EditingState {
  fieldPath: string | null
  value: JsonValue
}

export function useEditing() {
  const [editingState, setEditingState] = useState<EditingState>({
    fieldPath: null,
    value: null,
  })

  const startEditing = useCallback((fieldPath: string, currentValue: JsonValue) => {
    setEditingState({
      fieldPath,
      value: currentValue,
    })
  }, [])

  const updateEditingValue = useCallback((value: JsonValue) => {
    setEditingState((prev) => ({
      ...prev,
      value,
    }))
  }, [])

  const stopEditing = useCallback(() => {
    setEditingState({
      fieldPath: null,
      value: null,
    })
  }, [])

  const isEditing = useCallback(
    (fieldPath: string): boolean => {
      return editingState.fieldPath === fieldPath
    },
    [editingState.fieldPath],
  )

  return {
    editingState,
    startEditing,
    updateEditingValue,
    stopEditing,
    isEditing,
  }
}
