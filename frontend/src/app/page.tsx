"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState<string>("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const analyzeProducts = async () => {
    if (!url.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/scrape-and-analyze", {
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
            <button
              onClick={analyzeProducts}
              disabled={loading || !url.trim() || !isValidUrl(url.trim())}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Scraping & Analyzing..." : "Scrape & Analyze"}
            </button>
          </div>

          {result && (
            <div className="border-t pt-6">
              <h2 className="text-2xl font-semibold mb-4">Product Analysis Results</h2>
              <div className="space-y-6">
                {result.map((product: any, index: number) => (
                  <div key={index} className="bg-gray-50 p-6 rounded-lg">
                    {product.error ? (
                      <div className="text-red-600 font-medium">{product.error}</div>
                    ) : (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          <div className="text-center">
                            <div className="text-3xl font-bold text-blue-600 mb-2">
                              {product.overall_score || 0}/100
                            </div>
                            <div className="text-gray-600">Overall Score</div>
                          </div>
                          
                          <div className="space-y-2">
                            <h4 className="font-semibold text-green-700">Strengths</h4>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {product.strengths?.map((strength: string, i: number) => (
                                <li key={i} className="flex items-start">
                                  <span className="text-green-500 mr-2">✓</span>
                                  {strength}
                                </li>
                              ))}
                            </ul>
                          </div>
                          
                          <div className="space-y-2">
                            <h4 className="font-semibold text-red-700">Weaknesses</h4>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {product.weaknesses?.map((weakness: string, i: number) => (
                                <li key={i} className="flex items-start">
                                  <span className="text-red-500 mr-2">✗</span>
                                  {weakness}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                        
                        {product.improvements && product.improvements.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-semibold mb-3">Recommended Improvements</h4>
                            <div className="space-y-3">
                              {product.improvements.map((improvement: any, i: number) => (
                                <div key={i} className="bg-white p-4 rounded border-l-4 border-yellow-400">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="font-medium">{improvement.category}</span>
                                    <span className={`px-2 py-1 text-xs rounded ${
                                      improvement.priority === 'high' ? 'bg-red-100 text-red-700' :
                                      improvement.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                      'bg-green-100 text-green-700'
                                    }`}>
                                      {improvement.priority} priority
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-600 mb-2">
                                    <strong>Current:</strong> {improvement.current}
                                  </p>
                                  <p className="text-sm text-gray-600 mb-2">
                                    <strong>Suggested:</strong> {improvement.suggested}
                                  </p>
                                  <p className="text-sm text-blue-600">
                                    <strong>Impact:</strong> {improvement.impact}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {product.seo_recommendations && product.seo_recommendations.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-semibold mb-2">SEO Recommendations</h4>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {product.seo_recommendations.map((rec: string, i: number) => (
                                <li key={i} className="flex items-start">
                                  <span className="text-blue-500 mr-2">•</span>
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>
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
