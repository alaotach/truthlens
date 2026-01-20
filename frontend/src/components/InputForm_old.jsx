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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product Description
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste product description, title, specs, and price here..."
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              disabled={loading}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading || (inputType === 'url' ? !url.trim() : !text.trim())}
          className="w-full bg-primary text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Analyzing...' : 'Analyze Product'}
        </button>
      </form>

      {/* Example Products */}
      <div className="mt-6">
        <p className="text-sm font-medium text-gray-700 mb-3">
          {inputType === 'url' ? 'Try a demo URL:' : 'Try an example:'}
        </p>
        {inputType === 'url' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {exampleUrls.map((example, index) => (
              <button
                key={index}
                onClick={() => loadExampleUrl(example)}
                disabled={loading}
                className="text-left p-3 border border-gray-300 rounded-lg hover:border-primary hover:bg-blue-50 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="font-medium text-primary">{example.name}</span>
                <p className="text-xs text-gray-500 mt-1 truncate">{example.url}</p>
              </button>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {exampleProducts.map((example, index) => (
              <button
                key={index}
                onClick={() => loadExample(example)}
                disabled={loading}
                className="text-left p-3 border border-gray-300 rounded-lg hover:border-primary hover:bg-blue-50 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="font-medium text-primary">{example.name}</span>
              </button>
            ))}
          </div>
        )}
        {inputType === 'url' && (
          <p className="text-xs text-gray-500 mt-3">
            💡 Note: For live product URLs (Amazon, etc.), web scraping may be limited by anti-bot protections. 
            Use demo URLs above or paste product text for best results.
          </p>
        )}
      </div>
    </div>
  );
}
