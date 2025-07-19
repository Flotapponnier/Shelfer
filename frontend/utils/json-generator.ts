import { DiffType, type DiffResult } from "./json-diff"
import { ValidationState, type FieldValidation } from "../types/validation"

export function generateFinalJson(
  originalData: unknown,
  enrichedData: unknown,
  diffResult: DiffResult,
  validationStates: FieldValidation,
): unknown {
  return processObject(originalData, enrichedData, diffResult, validationStates, [])
}

function processObject(
  originalData: unknown,
  enrichedData: unknown,
  diffResult: DiffResult,
  validationStates: FieldValidation,
  currentPath: string[],
): unknown {
  if (enrichedData === null || enrichedData === undefined) {
    return enrichedData;
  }

  if (typeof enrichedData !== "object" || Array.isArray(enrichedData)) {
    return enrichedData;
  }

  const result: Record<string, unknown> = {};

  // Process each key in the enriched data
  for (const [key, enrichedValue] of Object.entries(enrichedData)) {
    const fieldPath = [...currentPath, key].join(".")
    const validationState = validationStates[fieldPath] || ValidationState.PENDING
    const diffInfo = diffResult[key]

    if (!diffInfo) {
      // Field doesn't exist in diff result, include as-is
      result[key] = enrichedValue
      continue
    }

    const { type: diffType, originalValue, nested } = diffInfo

    switch (diffType) {
      case DiffType.NEW:
        // New field: include only if approved or pending
        if (validationState === ValidationState.APPROVED || validationState === ValidationState.PENDING) {
          if (nested && typeof enrichedValue === "object" && !Array.isArray(enrichedValue)) {
            result[key] = processObject({}, enrichedValue, nested, validationStates, [...currentPath, key])
          } else {
            result[key] = enrichedValue
          }
        }
        // If declined, don't include the field
        break

      case DiffType.MODIFIED:
        if (validationState === ValidationState.DECLINED) {
          // Declined: revert to original value
          result[key] = originalValue
        } else {
          // Approved or pending: use enriched value
          if (nested && typeof enrichedValue === "object" && !Array.isArray(enrichedValue)) {
            result[key] = processObject(originalValue || {}, enrichedValue, nested, validationStates, [
              ...currentPath,
              key,
            ])
          } else {
            result[key] = enrichedValue
          }
        }
        break

      case DiffType.UNCHANGED:
      default:
        // Unchanged: include the enriched value (which should be the same as original)
        if (nested && typeof enrichedValue === "object" && !Array.isArray(enrichedValue)) {
          result[key] = processObject(originalValue || {}, enrichedValue, nested, validationStates, [
            ...currentPath,
            key,
          ])
        } else {
          result[key] = enrichedValue
        }
        break
    }
  }

  return result
}

export function getAllPendingFields(
  diffResult: DiffResult,
  validationStates: FieldValidation,
  path: string[] = [],
): string[] {
  const pendingFields: string[] = []

  const isPrimitive = (val: any) => val === null || typeof val !== "object";

  for (const [key, diffInfo] of Object.entries(diffResult)) {
    if (key === "@type") continue; // Never count @type as pending
    const currentPath = [...path, key]
    const fieldPath = currentPath.join(".")
    const validationState = validationStates[fieldPath] || ValidationState.PENDING

    if (isPrimitive(diffInfo.value)) {
      if (
        validationState === ValidationState.PENDING &&
        (diffInfo.type === DiffType.NEW || diffInfo.type === DiffType.MODIFIED)
      ) {
        pendingFields.push(fieldPath)
      }
    }

    // Recursively check nested objects or arrays
    if (diffInfo.nested) {
      if (Array.isArray(diffInfo.value)) {
        for (const arrayKey of Object.keys(diffInfo.nested)) {
          const nestedPath = [...currentPath, arrayKey]
          const nestedDiff = diffInfo.nested[arrayKey]
          if (nestedDiff && typeof nestedDiff === 'object' && !Array.isArray(nestedDiff) && !('type' in nestedDiff)) {
            const nestedPending = getAllPendingFields(nestedDiff as DiffResult, validationStates, nestedPath)
            pendingFields.push(...nestedPending)
          }
        }
      } else {
        const nestedPending = getAllPendingFields(diffInfo.nested as DiffResult, validationStates, currentPath)
        pendingFields.push(...nestedPending)
      }
    }
  }

  return pendingFields
}
