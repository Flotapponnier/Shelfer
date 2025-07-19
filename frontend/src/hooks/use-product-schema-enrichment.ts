import { useState, useCallback } from "react";
import { Product } from "schema-dts";

export type ProductSchemaEnrichmentResponse = {
  enrichedProductSchema: Product;
  originalProductSchema: Product;
};

export function useProductSchemaEnrichment() {
  const [url, setUrl] = useState<string>("");
  const [result, setResult] = useState<ProductSchemaEnrichmentResponse | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const isValidUrl = useCallback((string: string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  }, []);

  const enrichProductSchema = useCallback(async () => {
    if (!url.trim()) return;
    setLoading(true);
    try {
      const response = await fetch("/api/enrich-product-schema", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url.trim() }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ProductSchemaEnrichmentResponse = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing products:", error);
      setResult(undefined);
    } finally {
      setLoading(false);
    }
  }, [url]);

  return {
    url,
    setUrl,
    result,
    setResult,
    loading,
    enrichProductSchema,
    isValidUrl,
  };
} 