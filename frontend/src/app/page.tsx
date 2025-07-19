"use client";

import ProductDataEnrichment from "@/components/product-data-enrichment";
import { useState } from "react";
import { Product } from "schema-dts";

export default function Home() {
  const [url, setUrl] = useState<string>("");
  const [result, setResult] = useState<Product | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const analyzeProducts = async () => {
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
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing products:", error);
      setResult(undefined);
    } finally {
      setLoading(false);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
  };

  const isValidUrl = (string: string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Product Analyzer
          </h1>
          <p className="text-xl text-gray-600">
            Enter a product URL to scrape and analyze with AI-powered recommendations
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product URL
              </label>
              <input
                type="url"
                value={url}
                onChange={handleUrlChange}
                placeholder="https://example.com/product-page"
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
              {url.trim() && !isValidUrl(url.trim()) && (
                <p className="mt-1 text-sm text-red-600">Please enter a valid URL</p>
              )}
            </div>
            <button
              onClick={analyzeProducts}
              disabled={loading || !url.trim() || !isValidUrl(url.trim())}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Scraping & Analyzing..." : "Scrape & Analyze"}
            </button>
          </div>

        {result && (
          <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Analysis Results</h2>
            <ProductDataEnrichment data={result} />
          </div>
        )}
        </div>

        <div className="text-center text-gray-500">
          <p>Powered by AI-driven product analysis using ChatGPT and web scraping</p>
        </div>
      </div>
    </div>
  );
}
