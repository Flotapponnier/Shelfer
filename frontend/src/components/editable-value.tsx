"use client"

import { useState, useEffect, useRef, type KeyboardEvent } from "react"
import type { JsonValue } from "../../types/json"

interface EditableValueProps {
  value: JsonValue
  onSave: (newValue: JsonValue) => void
  onCancel: () => void
  className?: string
}

export default function EditableValue({ value, onSave, onCancel, className = "" }: EditableValueProps) {
  const [editValue, setEditValue] = useState(String(value))
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [])

  const handleSave = () => {
    let parsedValue: JsonValue = editValue

    // Try to parse the value to its original type
    if (typeof value === "number") {
      const numValue = Number(editValue)
      if (!isNaN(numValue)) {
        parsedValue = numValue
      }
    } else if (typeof value === "boolean") {
      parsedValue = editValue.toLowerCase() === "true"
    } else if (value === null && editValue.toLowerCase() === "null") {
      parsedValue = null
    }

    onSave(parsedValue)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleSave()
    } else if (e.key === "Escape") {
      e.preventDefault()
      onCancel()
    }
  }

  const handleBlur = () => {
    handleSave()
  }

  return (
    <input
      ref={inputRef}
      type="text"
      value={editValue}
      onChange={(e) => setEditValue(e.target.value)}
      onKeyDown={handleKeyDown}
      onBlur={handleBlur}
      className={`bg-white border border-blue-300 rounded px-1 py-0.5 text-sm font-mono min-w-0 ${className}`}
      style={{ width: `${Math.max(editValue.length * 8 + 16, 60)}px` }}
    />
  )
}
