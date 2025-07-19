export enum DiffType {
  NEW = "new",
  MODIFIED = "modified",
  UNCHANGED = "unchanged",
}

export interface DiffResult {
  [key: string]: {
    type: DiffType
    value?: any
    originalValue?: any
    nested?: DiffResult
  }
}

export function compareJsonObjects(original: any, enriched: any, path = ""): DiffResult {
  const result: DiffResult = {}

  // Handle null/undefined cases
  if (original === null || original === undefined) {
    original = {}
  }
  if (enriched === null || enriched === undefined) {
    enriched = {}
  }

  // Get all unique keys from both objects
  const originalKeys = new Set(typeof original === "object" && !Array.isArray(original) ? Object.keys(original) : [])
  const enrichedKeys = new Set(typeof enriched === "object" && !Array.isArray(enriched) ? Object.keys(enriched) : [])
  const allKeys = new Set([...originalKeys, ...enrichedKeys])

  for (const key of allKeys) {
    const originalValue = original[key]
    const enrichedValue = enriched[key]
    const currentPath = path ? `${path}.${key}` : key

    // Key exists only in enriched (NEW)
    if (!originalKeys.has(key)) {
      result[key] = {
        type: DiffType.NEW,
        value: enrichedValue,
        originalValue: undefined,
      }
    }
    // Key exists in both
    else if (enrichedKeys.has(key)) {
      // Both are objects (not arrays) - recurse
      if (
        typeof originalValue === "object" &&
        typeof enrichedValue === "object" &&
        originalValue !== null &&
        enrichedValue !== null &&
        !Array.isArray(originalValue) &&
        !Array.isArray(enrichedValue)
      ) {
        const nestedDiff = compareJsonObjects(originalValue, enrichedValue, currentPath)
        const hasChanges = Object.values(nestedDiff).some((diff) => diff.type !== DiffType.UNCHANGED)

        result[key] = {
          type: hasChanges ? DiffType.MODIFIED : DiffType.UNCHANGED,
          value: enrichedValue,
          originalValue: originalValue,
          nested: nestedDiff,
        }
      }
      // Arrays or primitive values - deep compare
      else {
        const isEqual = JSON.stringify(originalValue) === JSON.stringify(enrichedValue)
        result[key] = {
          type: isEqual ? DiffType.UNCHANGED : DiffType.MODIFIED,
          value: enrichedValue,
          originalValue: originalValue,
        }
      }
    }
  }

  return result
}

export function getDiffTypeForPath(diffResult: DiffResult, path: string[]): DiffType {
  let current = diffResult

  for (let i = 0; i < path.length; i++) {
    const key = path[i]
    if (!current[key]) return DiffType.UNCHANGED

    if (i === path.length - 1) {
      return current[key].type
    }

    if (current[key].nested) {
      current = current[key].nested
    } else {
      return current[key].type
    }
  }

  return DiffType.UNCHANGED
}

export function getOriginalValueForPath(diffResult: DiffResult, path: string[]): any {
  let current = diffResult

  for (let i = 0; i < path.length; i++) {
    const key = path[i]
    if (!current[key]) return undefined

    if (i === path.length - 1) {
      return current[key].originalValue
    }

    if (current[key].nested) {
      current = current[key].nested
    } else {
      return current[key].originalValue
    }
  }

  return undefined
}
