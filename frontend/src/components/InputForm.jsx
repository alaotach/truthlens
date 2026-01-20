import React, { useState } from 'react';

export default function InputForm({ onAnalyze, loading }) {
  const [inputType, setInputType] = useState('text');
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputType === 'url' && url.trim()) {
      onAnalyze({ url: url.trim() });
    } else if (inputType === 'text' && text.trim()) {
      onAnalyze({ text: text.trim() });
    }
  };

  const exampleProducts = [
    {
      name: '10000mAh Fast Charger',
      text: '10000mAh power bank with AI-powered charging. Charges your phone in just 5 minutes! 100% efficiency. Only $99.99'
    },
    {
      name: 'Quantum Battery Pack',
      text: '20000mAh quantum battery pack. Medical-grade power bank. Charges in 2 minutes. 150W output. Military-grade durability. Price: $149.99'
    },
    {
      name: 'Realistic Power Bank',
      text: 'Portable 5000mAh power bank. Charges in 90 minutes. 18W fast charging support. Lightweight at 150g. $29.99'
    }
  ];

  const exampleUrls = [
    {
      name: 'Demo: Realistic Product',
      url: 'https://example.com/product/realistic-powerbank'
    },
    {
      name: 'Demo: Unrealistic Product',
      url: 'https://example.com/product/unrealistic-quantum-battery'
    }
  ];

  const loadExample = (example) => {
    setInputType('text');
    setText(example.text);
  };

  const loadExampleUrl = (example) => {
    setInputType('url');
    setUrl(example.url);
  };

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8 border border-gray-100 hover:shadow-3xl transition-shadow duration-300">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">📦</span>
        <h2 className="text-3xl font-bold text-gray-800">Analyze a Product</h2>
      </div>
      
      {/* Recommendation Banner */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-500 p-4 mb-6 rounded-lg">
        <div className="flex items-start gap-2">
          <span className="text-2xl">💡</span>
          <div>
            <p className="font-semibold text-gray-800 mb-1">Recommended: Use Text Input</p>
            <p className="text-sm text-gray-700">
              For best results, copy product details (title, price, features) from the website and paste below. 
              URL scraping may not work due to bot protection on many e-commerce sites.
            </p>
          </div>
        </div>
      </div>
      
      {/* Input Type Selector */}
      <div className="flex gap-3 mb-6 bg-gray-100 p-2 rounded-xl">
        <button
          onClick={() => setInputType('text')}
          className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
            inputType === 'text'
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg transform scale-105'
              : 'bg-white text-gray-700 hover:bg-gray-50 hover:shadow-md'
          }`}
        >
          📝 Product Description
        </button>
        <button
          onClick={() => setInputType('url')}
          className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
            inputType === 'url'
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg transform scale-105'
              : 'bg-white text-gray-700 hover:bg-gray-50 hover:shadow-md'
          }`}
        >
          🔗 Product URL
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {inputType === 'url' ? (
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="mr-2">🌐</span> Product URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/product/..."
              className="w-full px-5 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 text-lg"
              required
            />
          </div>
        ) : (
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="mr-2">✏️</span> Product Description
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste product details here... (include claims, features, price, specs)"
              rows="6"
              className="w-full px-5 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 text-lg"
              required
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02] disabled:transform-none flex items-center justify-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing...
            </>
          ) : (
            <>🚀 Analyze Product</>
          )}
        </button>

        {inputType === 'text' && (
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
            <p className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="mr-2">💡</span> Try Quick Examples:
            </p>
            <div className="flex gap-3 flex-wrap">
              {exampleProducts.map((example, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => loadExample(example)}
                  className="px-4 py-2 text-sm bg-white text-gray-700 rounded-lg hover:bg-blue-600 hover:text-white hover:shadow-md transition-all duration-200 border border-gray-200 font-medium"
                >
                  {example.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {inputType === 'url' && (
          <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-xl border border-green-100">
            <p className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="mr-2">🔗</span> Try Demo URLs:
            </p>
            <div className="flex gap-3 flex-wrap">
              {exampleUrls.map((example, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => loadExampleUrl(example)}
                  className="px-4 py-2 text-sm bg-white text-gray-700 rounded-lg hover:bg-green-600 hover:text-white hover:shadow-md transition-all duration-200 border border-gray-200 font-medium"
                >
                  {example.name}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-3">
              💡 <strong>Note:</strong> Most e-commerce sites block URL scraping. For reliable results, copy the product text:
              <br/>• Select product title, price, and features from the website
              <br/>• Paste into the text input above
            </p>
          </div>
        )}
      </form>
    </div>
  );
}
