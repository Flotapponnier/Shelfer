"use client";

import ProductDataEnrichment from "@/components/product-data-enrichment";
import { useProductSchemaEnrichment } from "@/hooks/use-product-schema-enrichment";

export default function Home() {
  const {
    url,
    setUrl,
    result,
    loading,
    enrichProductSchema,
    isValidUrl,
  } = useProductSchemaEnrichment();

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
              <div className="text-center mb-8 mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Product Data Enrichment
          </h1>
        </div>
      {!result && (
        <>



      <div className="w-full mx-auto">

      <div className="text-center mb-12 max-w-xl mx-auto">

          <p className="text-xl text-gray-600">
            Enter a URL of an e-commerce shop&apos;s product page to scrape and enrich it with AI-powered recommendations
          </p>
          </div>

        <div className="bg-white rounded-lg shadow-xl p-8 mb-8 max-w-xl mx-auto">
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
              onClick={enrichProductSchema}
              disabled={loading || !url.trim() || !isValidUrl(url.trim())}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Scraping & Analyzing..." : "Scrape & Analyze"}
            </button>
          </div>

       
        </div>

        <div className="text-center text-gray-500">
          <p>Powered by AI-driven product analysis using ChatGPT and web scraping</p>
        </div>
      </div>
    </>
  )}

{result && (
          <>
            <ProductDataEnrichment data={result} />
          </>
        )}
  </div>
  );
}
