"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState<string>("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const analyzeProducts = async (endpoint: string = "scrape-and-analyze") => {
    if (!url.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/${endpoint}`, {
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
      setResult([{ error: `Analysis failed: ${error}` }]);
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
            <div className="flex gap-3">
              <button
                onClick={() => analyzeProducts("scrape-main-product")}
                disabled={loading || !url.trim() || !isValidUrl(url.trim())}
                className="flex-1 px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Finding Main Product..." : "🎯 Main Product"}
              </button>
              <button
                onClick={() => analyzeProducts("scrape-and-analyze")}
                disabled={loading || !url.trim() || !isValidUrl(url.trim())}
                className="flex-1 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Scraping All..." : "📦 All Products"}
              </button>
            </div>
          </div>

          {result && (
            <div className="border-t pt-6">
              {/* Check if this is a main product result */}
              {result.main_product !== undefined ? renderMainProductResults(result) : renderScraperDevResults(result)}
            </div>
          )}
        </div>

        <div className="text-center text-gray-500">
          <p>Powered by AI-driven product analysis using ChatGPT and web scraping</p>
        </div>
      </div>
    </div>
  );

  // MAIN PRODUCT RESULTS RENDERER
  function renderMainProductResults(result: any) {
    const mainProduct = result.main_product;
    const analysis = result.analysis || {};
    const detectionSummary = result.detection_summary || {};

    return (
      <div>
        <h2 className="text-2xl font-semibold mb-4">🎯 Main Product Detection Results</h2>
        
        {/* Detection Summary */}
        <div className="bg-green-50 p-4 rounded-lg mb-6">
          <h3 className="font-semibold mb-2 text-green-800">📊 Detection Summary</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Main Product Found:</strong> 
              <span className={`ml-2 px-2 py-1 rounded text-xs ${
                detectionSummary.main_product_found 
                  ? 'bg-green-200 text-green-800' 
                  : 'bg-red-200 text-red-800'
              }`}>
                {detectionSummary.main_product_found ? 'YES' : 'NO'}
              </span>
            </div>
            <div><strong>Confidence:</strong> {detectionSummary.confidence_level || 'unknown'}</div>
            <div><strong>Total Products on Page:</strong> {detectionSummary.total_products_on_page || 0}</div>
            <div><strong>Algorithm:</strong> {detectionSummary.algorithm_used || 'unknown'}</div>
          </div>
        </div>

        {/* Main Product Details */}
        {mainProduct ? (
          <div className="bg-blue-50 p-6 rounded-lg mb-6">
            <h3 className="font-semibold mb-4 text-blue-800 text-xl">🏆 Main Product Identified</h3>
            
            <div className="space-y-4">
              {/* Product Name */}
              <div>
                <h4 className="text-lg font-medium text-gray-900">
                  {mainProduct.name || 'Unnamed Product'}
                </h4>
              </div>

              {/* Key Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><strong>SKU:</strong> {mainProduct.sku || 'N/A'}</div>
                <div><strong>Brand:</strong> {
                  typeof mainProduct.brand === 'object' 
                    ? mainProduct.brand?.name || 'N/A'
                    : mainProduct.brand || 'N/A'
                }</div>
                <div><strong>Type:</strong> {mainProduct['@type'] || 'N/A'}</div>
                <div><strong>Price:</strong> {
                  mainProduct.offers?.price 
                    ? `${mainProduct.offers.price} ${mainProduct.offers.priceCurrency || ''}` 
                    : 'N/A'
                }</div>
              </div>

              {/* Description */}
              {mainProduct.description && (
                <div>
                  <strong>Description:</strong>
                  <p className="mt-1 text-gray-700 text-sm">
                    {mainProduct.description.length > 200 
                      ? mainProduct.description.substring(0, 200) + '...' 
                      : mainProduct.description}
                  </p>
                </div>
              )}

              {/* Image */}
              {mainProduct.image && (
                <div>
                  <strong>Image:</strong>
                  <div className="mt-2">
                    <img 
                      src={Array.isArray(mainProduct.image) ? mainProduct.image[0] : mainProduct.image} 
                      alt={mainProduct.name || 'Product'} 
                      className="max-w-xs max-h-48 object-contain rounded border"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Raw Data Toggle */}
              <details className="mt-4">
                <summary className="cursor-pointer text-blue-600 hover:text-blue-800 font-medium">
                  View Complete Product Schema
                </summary>
                <pre className="mt-3 bg-gray-100 p-4 rounded text-xs overflow-auto max-h-60">
                  {JSON.stringify(mainProduct, null, 2)}
                </pre>
              </details>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-6">
            <h3 className="font-semibold text-yellow-800 mb-2">⚠️ No Main Product Detected</h3>
            <p className="text-yellow-700 text-sm">
              The algorithm couldn't identify a clear main product on this page. 
              This might be because:
            </p>
            <ul className="list-disc list-inside text-yellow-700 text-sm mt-2 space-y-1">
              <li>The page doesn't contain product schema markup</li>
              <li>Multiple products were found with similar importance</li>
              <li>The page is a category/listing page rather than a product page</li>
            </ul>
          </div>
        )}

        {/* All Products Found (if multiple) */}
        {result.all_products_found && result.all_products_found.length > 1 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-3">📦 All Products Found on Page ({result.all_products_found.length})</h3>
            <div className="space-y-3">
              {result.all_products_found.map((product: any, index: number) => (
                <div key={index} className={`p-3 rounded border-l-4 ${
                  product === mainProduct 
                    ? 'bg-green-50 border-green-500' 
                    : 'bg-gray-50 border-gray-300'
                }`}>
                  <div className="flex items-center gap-2">
                    {product === mainProduct && <span className="text-green-600 font-bold">🏆 MAIN</span>}
                    <span className="font-medium">{product.name || 'Unnamed Product'}</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    SKU: {product.sku || 'N/A'} | Type: {product['@type'] || 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {result.error && (
          <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
            <h3 className="font-semibold text-red-800 mb-2">❌ Error</h3>
            <div className="text-red-700">{result.error}</div>
          </div>
        )}
      </div>
    );
  }

  // TEMPORARY FUNCTION FOR SCRAPER DEVELOPMENT - DELETE WHEN DONE
  function renderScraperDevResults(result: any) {
    return (
      <div>
        <h2 className="text-2xl font-semibold mb-4">🔧 Scraper Development Results</h2>
        
        {/* Stats Summary */}
        {result.scraper_stats && (
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">📊 Scraper Statistics</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">{result.scraper_stats.products_found}</div>
                <div className="text-sm text-gray-600">Products</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{result.scraper_stats.total_schemas}</div>
                <div className="text-sm text-gray-600">Total Schemas</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">{result.scraper_stats.non_product_schemas}</div>
                <div className="text-sm text-gray-600">Non-Products</div>
              </div>
            </div>
          </div>
        )}

        {/* Products Found */}
        {result.scraped_products && result.scraped_products.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-3">📦 Products Found ({result.scraped_products.length})</h3>
            <div className="space-y-4">
              {result.scraped_products.map((product: any, index: number) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg">
                  <div className="font-medium text-lg mb-2">{product.name || 'Unnamed Product'}</div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div><strong>SKU:</strong> {product.sku || 'N/A'}</div>
                    <div><strong>Type:</strong> {product['@type'] || 'N/A'}</div>
                    <div><strong>Price:</strong> {product.offers?.price ? `${product.offers.price} ${product.offers.priceCurrency || ''}` : 'N/A'}</div>
                    <div><strong>Brand:</strong> {product.brand?.name || 'N/A'}</div>
                  </div>
                  <details className="mt-3">
                    <summary className="cursor-pointer text-blue-600 hover:text-blue-800">View Raw Data</summary>
                    <pre className="mt-2 bg-gray-100 p-3 rounded text-xs overflow-auto max-h-40">
                      {JSON.stringify(product, null, 2)}
                    </pre>
                  </details>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Crawler Summary */}
        {result.scraper_summary && (
          <div className="mb-6">
            <h3 className="font-semibold mb-3">🕷️ Crawler Summary</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><strong>Pages Visited:</strong> {result.scraper_summary.pages_visited || 0}</div>
                <div><strong>Links Processed:</strong> {result.scraper_summary.links_processed || 0}</div>
                <div><strong>Extraction Attempts:</strong> {result.scraper_summary.jsonld_extraction_attempts || 0}</div>
                <div><strong>Extraction Successes:</strong> {result.scraper_summary.jsonld_extraction_successes || 0}</div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {result.error && (
          <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
            <h3 className="font-semibold text-red-800 mb-2">❌ Error</h3>
            <div className="text-red-700">{result.error}</div>
          </div>
        )}
      </div>
    );
  }

}
