import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ResultCard from './components/ResultCard';
import { analyzeProduct } from './services/api';

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (productInput) => {
    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const result = await analyzeProduct(productInput);
      setAnalysis(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white shadow-2xl relative overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="max-w-6xl mx-auto px-4 py-12 relative z-10">
          <div className="flex items-center justify-center gap-4 mb-3">
            <div className="bg-white/20 backdrop-blur-sm rounded-full p-3">
              <div className="text-5xl">🔍</div>
            </div>
            <h1 className="text-5xl font-extrabold tracking-tight">TruthLens</h1>
          </div>
          <p className="text-blue-100 text-lg text-center max-w-2xl mx-auto">
            AI-Powered Product Reality & Fair Price Checker — Verify claims, analyze pricing, make smarter purchases
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        <InputForm onAnalyze={handleAnalyze} loading={loading} />

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-2xl shadow-2xl p-12 text-center border border-gray-100">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600 mb-4"></div>
            <p className="text-xl text-gray-800 font-bold">Analyzing product claims...</p>
            <p className="text-sm text-gray-500 mt-2">⚡ Verifying physics, checking prices, scoring credibility</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 rounded-xl shadow-lg p-6 mb-8 animate-shake">
            <div className="flex items-start gap-3">
              <span className="text-3xl">⚠️</span>
              <div>
                <h3 className="text-lg font-bold text-red-800 mb-1">Analysis Failed</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {analysis && !loading && (
          <ResultCard analysis={analysis} />
        )}

        {/* Info Section */}
        {!analysis && !loading && !error && (
          <div className="grid md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-3">⚗️</div>
              <h3 className="text-lg font-bold text-gray-800 mb-2">Physics-Based Verification</h3>
              <p className="text-gray-600 text-sm">Every claim is verified against real scientific constraints and engineering limits</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-3">💰</div>
              <h3 className="text-lg font-bold text-gray-800 mb-2">Fair Price Analysis</h3>
              <p className="text-gray-600 text-sm">Compare listed price against market benchmarks and feature-based fair value</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 border border-green-100 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-3">📊</div>
              <h3 className="text-lg font-bold text-gray-800 mb-2">Reality Score</h3>
              <p className="text-gray-600 text-sm">Get an overall credibility score based on feasibility and pricing analysis</p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-gray-800 to-gray-900 text-white mt-20">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center">
          <p className="text-gray-400">Built with FastAPI & React • Physics-based claim verification</p>
          <p className="text-gray-500 text-sm mt-2">© 2026 TruthLens — Making informed purchases easier</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
