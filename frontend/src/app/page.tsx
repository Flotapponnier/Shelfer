"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeSEO = async () => {
    if (!url) return;
    
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing SEO:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI SEO Analyzer
          </h1>
          <p className="text-xl text-gray-600">
            Get instant SEO scores and recommendations for any website
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
          <div className="flex gap-4 mb-6">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter website URL (e.g., https://example.com)"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <button
              onClick={analyzeSEO}
              disabled={loading || !url}
              className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Analyzing..." : "Analyze SEO"}
            </button>
          </div>

          {result && (
            <div className="border-t pt-6">
              <h2 className="text-2xl font-semibold mb-4">SEO Analysis Results</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {result.score}/100
                    </div>
                    <div className="text-gray-600">SEO Score</div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Title:</span>
                    <span className="font-medium">{result.title || "Not found"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">H1 Tags:</span>
                    <span className="font-medium">{result.h1_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Missing Alt Tags:</span>
                    <span className="font-medium">{result.image_alt_missing}</span>
                  </div>
                </div>
              </div>
              
              {result.meta_description && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Meta Description:</h3>
                  <p className="text-gray-600 bg-gray-50 p-3 rounded">
                    {result.meta_description}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="text-center text-gray-500">
          <p>Powered by AI-driven SEO analysis</p>
        </div>
      </div>
    </div>
  );
}
