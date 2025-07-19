"use client"

import type React from "react"

import { useState } from "react"
import { ChevronRight, ChevronDown, Check, X, Edit3 } from "lucide-react"
import { DiffType, type DiffResult, getDiffTypeForPath, getOriginalValueForPath } from "../../utils/json-diff"
import { ValidationState, type FieldValidation, type ValidationAction } from "../../types/validation"
import EditableValue from "./editable-value"
import { Product } from "schema-dts"
import type { JsonValue } from "../../types/json";

interface JsonTreeViewProps {
  data: Product
  level?: number
  parentKey?: string
  diffResult?: DiffResult
  currentPath?: string[]
  validationStates?: FieldValidation
  onValidation?: (action: ValidationAction) => void
  editingFieldPath?: string | null
  onStartEditing?: (fieldPath: string, currentValue: JsonValue) => void
  onStopEditing?: () => void
  onUpdateValue?: (fieldPath: string, newValue: JsonValue) => void
}

interface JsonNodeProps {
  nodeKey: string
  value: JsonValue
  level: number
  isLast?: boolean
  diffResult?: DiffResult
  currentPath: string[]
  validationStates?: FieldValidation
  onValidation?: (action: ValidationAction) => void
  editingFieldPath?: string | null
  onStartEditing?: (fieldPath: string, currentValue: JsonValue) => void
  onStopEditing?: () => void
  onUpdateValue?: (fieldPath: string, newValue: JsonValue) => void
}

function JsonNode({
  nodeKey,
  value,
  level,
  isLast = false,
  diffResult,
  currentPath,
  validationStates,
  onValidation,
  editingFieldPath,
  onStartEditing,
  onStopEditing,
  onUpdateValue,
}: JsonNodeProps) {
  const [isExpanded, setIsExpanded] = useState(level < 2)

  const nodePath = [...currentPath, nodeKey]
  const fieldPath = nodePath.join(".")
  const diffType = diffResult ? getDiffTypeForPath(diffResult, nodePath) : DiffType.UNCHANGED
  const originalValue = diffResult ? getOriginalValueForPath(diffResult, nodePath) : undefined
  const validationState = validationStates?.[fieldPath] || ValidationState.PENDING
  const isCurrentlyEditing = editingFieldPath === fieldPath

  const getValueType = (val: JsonValue): string => {
    if (val === null) return "null"
    if (Array.isArray(val)) return "array"
    return typeof val
  }

  const getValueColor = (type: string): string => {
    switch (type) {
      case "string":
        return "text-green-600"
      case "number":
        return "text-blue-600"
      case "boolean":
        return "text-purple-600"
      case "null":
        return "text-gray-500"
      case "array":
        return "text-orange-600"
      case "object":
        return "text-indigo-600"
      default:
        return "text-gray-800"
    }
  }

  const getDiffBackgroundClass = (
    diffType: DiffType,
    validationState: ValidationState,
    isValueOnly = false,
  ): string => {
    // If approved or declined, remove highlighting
    if (validationState !== ValidationState.PENDING) {
      return "bg-white"
    }

    switch (diffType) {
      case DiffType.NEW:
        return isValueOnly ? "bg-green-100" : "bg-green-50 border-l-4 border-green-400"
      case DiffType.MODIFIED:
        return isValueOnly ? "bg-yellow-100" : "bg-yellow-50 border-l-4 border-yellow-400"
      case DiffType.UNCHANGED:
      default:
        return "bg-white"
    }
  }

  const formatValue = (val: JsonValue): string => {
    if (val === null) return "null"
    if (typeof val === "string") return `"${val}"`
    if (typeof val === "boolean") return val.toString()
    if (typeof val === "number") return val.toString()
    return ""
  }

  const isExpandable = (val: JsonValue): boolean => {
    return val !== null && (typeof val === "object" || Array.isArray(val))
  }

  const isEditable = (val: JsonValue): boolean => {
    return !isExpandable(val) && onStartEditing !== undefined
  }

  const getObjectPreview = (val: JsonValue): string => {
    if (Array.isArray(val)) {
      return `Array(${val.length})`
    }
    if (typeof val === "object" && val !== null) {
      const keys = Object.keys(val)
      return `Object(${keys.length})`
    }
    return ""
  }

  const handleToggle = () => {
    if (isExpandable(value)) {
      setIsExpanded(!isExpanded)
    }
  }

  const handleValueClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (isEditable(value) && !isCurrentlyEditing) {
      onStartEditing?.(fieldPath, value)
    }
  }

  const handleEditSave = (newValue: JsonValue) => {
    onUpdateValue?.(fieldPath, newValue)
    onStopEditing?.()
  }

  const handleEditCancel = () => {
    onStopEditing?.()
  }

  const handleApprove = (e: React.MouseEvent) => {
    e.stopPropagation()
    onValidation?.({
      type: "APPROVE",
      fieldPath,
      originalValue,
    })
  }

  const handleDecline = (e: React.MouseEvent) => {
    e.stopPropagation()
    onValidation?.({
      type: "DECLINE",
      fieldPath,
      originalValue,
    })
  }

  const shouldShowValidationControls = (): boolean => {
    return (
      validationState === ValidationState.PENDING &&
      (diffType === DiffType.NEW || diffType === DiffType.MODIFIED) &&
      !isExpandable(value) &&
      !isCurrentlyEditing
    )
  }

  const getDisplayValue = () => {
    // If declined, show original value or hide if it was a new field
    if (validationState === ValidationState.DECLINED) {
      if (diffType === DiffType.NEW) {
        return null // Don't render new fields that were declined
      }
      return originalValue
    }
    return value
  }

  const displayValue = getDisplayValue()

  // Don't render declined new fields
  if (validationState === ValidationState.DECLINED && diffType === DiffType.NEW) {
    return null
  }

  const getNestedDiffResult = (): DiffResult | undefined => {
    if (!diffResult) return undefined

    let current = diffResult
    for (const key of nodePath) {
      if (current[key]?.nested) {
        current = current[key].nested!
      } else {
        return undefined
      }
    }
    return current
  }

  return (
    <div className="font-mono text-sm">
      <div
        className={`flex items-center py-1 hover:bg-gray-50 rounded px-2 transition-colors group ${
          isExpandable(displayValue) ? "cursor-pointer" : "cursor-default"
        } ${getDiffBackgroundClass(diffType, validationState)} ${
          validationState !== ValidationState.PENDING ? "opacity-75" : ""
        }`}
        onClick={handleToggle}
        style={{ paddingLeft: `${level * 20}px` }}
      >
        {/* Expand/Collapse Icon */}
        <div className="w-4 h-4 mr-2 flex items-center justify-center">
          {isExpandable(displayValue) ? (
            isExpanded ? (
              <ChevronDown className="w-3 h-3 text-gray-600" />
            ) : (
              <ChevronRight className="w-3 h-3 text-gray-600" />
            )
          ) : (
            <div className="w-3 h-3" />
          )}
        </div>

        {/* Diff indicator */}
        {diffResult && validationState === ValidationState.PENDING && (
          <div className="w-2 h-2 mr-2 rounded-full flex-shrink-0">
            {diffType === DiffType.NEW && <div className="w-full h-full bg-green-500 rounded-full"></div>}
            {diffType === DiffType.MODIFIED && <div className="w-full h-full bg-yellow-500 rounded-full"></div>}
          </div>
        )}

        {/* Validation state indicator */}
        {validationState !== ValidationState.PENDING && (
          <div className="w-2 h-2 mr-2 rounded-full flex-shrink-0">
            {validationState === ValidationState.APPROVED && (
              <div className="w-full h-full bg-blue-500 rounded-full"></div>
            )}
            {validationState === ValidationState.DECLINED && (
              <div className="w-full h-full bg-gray-400 rounded-full"></div>
            )}
          </div>
        )}

        {/* Key */}
        <span className="text-blue-800 font-medium mr-2">{nodeKey}:</span>

        {/* Value */}
        <div className="flex-1 flex items-center justify-between">
          <div className="flex items-center">
            {!isExpandable(displayValue) ? (
              <div className="flex items-center">
                {isCurrentlyEditing ? (
                  <EditableValue
                    value={displayValue}
                    onSave={handleEditSave}
                    onCancel={handleEditCancel}
                    className={getValueColor(getValueType(displayValue))}
                  />
                ) : (
                  <span
                    className={`${getValueColor(getValueType(displayValue))} ${
                      diffType === DiffType.MODIFIED && validationState === ValidationState.PENDING
                        ? getDiffBackgroundClass(diffType, validationState, true) + " px-1 rounded"
                        : ""
                    } ${isEditable(displayValue) ? "cursor-pointer hover:bg-gray-100 px-1 rounded" : ""}`}
                    onClick={handleValueClick}
                    title={isEditable(displayValue) ? "Click to edit" : ""}
                  >
                    {formatValue(displayValue)}
                  </span>
                )}
                {isEditable(displayValue) && !isCurrentlyEditing && (
                  <Edit3 className="w-3 h-3 text-gray-400 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
              </div>
            ) : (
              <span className="text-gray-600">
                {isExpanded
                  ? Array.isArray(displayValue)
                    ? "["
                    : "{"
                  : `${getObjectPreview(displayValue)} ${Array.isArray(displayValue) ? "[...]" : "{...}"}`}
              </span>
            )}

            {/* Status badges */}
            {validationState === ValidationState.PENDING && diffType === DiffType.NEW && (
              <span className="ml-2 px-2 py-1 text-xs bg-green-200 text-green-800 rounded-full font-medium">NEW</span>
            )}
            {validationState === ValidationState.APPROVED && (
              <span className="ml-2 px-2 py-1 text-xs bg-blue-200 text-blue-800 rounded-full font-medium">
                APPROVED
              </span>
            )}
            {validationState === ValidationState.DECLINED && (
              <span className="ml-2 px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded-full font-medium">
                DECLINED
              </span>
            )}
          </div>

          {/* Validation Controls */}
          {shouldShowValidationControls() && (
            <div className="flex items-center gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={handleApprove}
                className="p-1 hover:bg-green-100 rounded-full transition-colors"
                title="Approve this change"
              >
                <Check className="w-3 h-3 text-green-600" />
              </button>
              <button
                onClick={handleDecline}
                className="p-1 hover:bg-red-100 rounded-full transition-colors"
                title="Decline this change"
              >
                <X className="w-3 h-3 text-red-600" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Nested Content */}
      {isExpandable(displayValue) && isExpanded && (
        <div>
          {Array.isArray(displayValue)
            ? displayValue.map((item, index) => (
                <JsonNode
                  key={index}
                  nodeKey={`[${index}]`}
                  value={item}
                  level={level + 1}
                  isLast={index === displayValue.length - 1}
                  diffResult={diffResult}
                  currentPath={nodePath}
                  validationStates={validationStates}
                  onValidation={onValidation}
                  editingFieldPath={editingFieldPath}
                  onStartEditing={onStartEditing}
                  onStopEditing={onStopEditing}
                  onUpdateValue={onUpdateValue}
                />
              ))
            : Object.entries(displayValue).map(([key, val], index, array) => (
                <JsonNode
                  key={key}
                  nodeKey={key}
                  value={val as JsonValue}
                  level={level + 1}
                  isLast={index === array.length - 1}
                  diffResult={getNestedDiffResult()}
                  currentPath={nodePath}
                  validationStates={validationStates}
                  onValidation={onValidation}
                  editingFieldPath={editingFieldPath}
                  onStartEditing={onStartEditing}
                  onStopEditing={onStopEditing}
                  onUpdateValue={onUpdateValue}
                />
              ))}
          <div className="text-gray-600 font-mono text-sm" style={{ paddingLeft: `${level * 20 + 24}px` }}>
            {Array.isArray(displayValue) ? "]" : "}"}
          </div>
        </div>
      )}
    </div>
  )
}

export default function JsonTreeView({
  data,
  level = 0,
  parentKey,
  diffResult,
  currentPath = [],
  validationStates,
  onValidation,
  editingFieldPath,
  onStartEditing,
  onStopEditing,
  onUpdateValue,
}: JsonTreeViewProps) {
  if (data === null || data === undefined) {
    return <div className="text-gray-500 font-mono text-sm p-4">No data available</div>
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 max-h-96 overflow-y-auto">
      <div className="space-y-1">
        {typeof data === "object" && !Array.isArray(data) ? (
          Object.entries(data).map(([key, value], index, array) => (
            <JsonNode
              key={key}
              nodeKey={key}
              value={value}
              level={level}
              isLast={index === array.length - 1}
              diffResult={diffResult}
              currentPath={currentPath}
              validationStates={validationStates}
              onValidation={onValidation}
              editingFieldPath={editingFieldPath}
              onStartEditing={onStartEditing}
              onStopEditing={onStopEditing}
              onUpdateValue={onUpdateValue}
            />
          ))
        ) : (
          <JsonNode
            nodeKey={parentKey || "root"}
            value={data}
            level={level}
            diffResult={diffResult}
            currentPath={currentPath}
            validationStates={validationStates}
            onValidation={onValidation}
            editingFieldPath={editingFieldPath}
            onStartEditing={onStartEditing}
            onStopEditing={onStopEditing}
            onUpdateValue={onUpdateValue}
          />
        )}
      </div>
    </div>
  )
}
