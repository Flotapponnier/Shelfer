"use client"

import { useState, useCallback, useMemo } from "react"
import { compareJsonObjects } from "../../utils/json-diff"
import { Product } from "schema-dts"

export function useProductData(
  originalJsonLdSchema: Product,
  enrichedJsonLdSchema: Product
) {
  const [enrichedProduct, setEnrichedProduct] = useState<Product>(enrichedJsonLdSchema)

  const updateFieldValue = useCallback((fieldPath: string, newValue: unknown) => {
    setEnrichedProduct((prev: Product) => {
      const pathArray = fieldPath.split(".")
      const newData = JSON.parse(JSON.stringify(prev)) // Deep clone

      // Navigate to the parent object
      let current: Record<string, unknown> = newData
      for (let i = 0; i < pathArray.length - 1; i++) {
        if (!current[pathArray[i]]) {
          current[pathArray[i]] = {}
        }
        current = current[pathArray[i]] as Record<string, unknown>
      }

      // Set the final value
      const finalKey = pathArray[pathArray.length - 1]
      current[finalKey] = newValue

      return newData
    })
  }, [])

  const diffResult = useMemo(() => {
    return compareJsonObjects(originalJsonLdSchema, enrichedProduct)
  }, [originalJsonLdSchema, enrichedProduct])

  return {
    enrichedProduct,
    updateFieldValue,
    diffResult,
    setEnrichedProduct,
  }
}
