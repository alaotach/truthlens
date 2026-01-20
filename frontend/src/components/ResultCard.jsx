import React from 'react';
import ScoreIndicator from './ScoreIndicator';

export default function ResultCard({ analysis }) {
  const getVerdictInfo = (verdict) => {
    const verdicts = {
      good_value: { text: '✅ Good Value', color: 'bg-success text-white', icon: '✅' },
      acceptable: { text: '⚠️ Acceptable', color: 'bg-yellow-500 text-white', icon: '⚠️' },
      overpriced: { text: '💰 Overpriced', color: 'bg-warning text-white', icon: '💰' },
      misleading_claims: { text: '⚠️ Misleading Claims', color: 'bg-orange-500 text-white', icon: '⚠️' },
      not_recommended: { text: '❌ Not Recommended', color: 'bg-danger text-white', icon: '❌' }
    };
    return verdicts[verdict] || verdicts.acceptable;
  };

  const getStatusBadge = (status) => {
    const badges = {
      feasible: { text: '✅ Feasible', color: 'bg-green-100 text-green-800' },
      exaggerated: { text: '⚠️ Exaggerated', color: 'bg-yellow-100 text-yellow-800' },
      impossible: { text: '❌ Impossible', color: 'bg-red-100 text-red-800' }
    };
    return badges[status] || badges.feasible;
  };

  const verdictInfo = getVerdictInfo(analysis.overall_verdict);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Product Title */}
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        {analysis.product_title}
      </h2>

      {/* Overall Verdict */}
      <div className={`${verdictInfo.color} rounded-lg p-4 mb-6`}>
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold">{verdictInfo.text}</span>
        </div>
      </div>

      {/* Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <ScoreIndicator 
          score={analysis.reality_score} 
          label="Reality Score"
          type="reality"
        />
        <ScoreIndicator 
          score={analysis.pricing_score} 
          label="Pricing Score"
          type="pricing"
        />
      </div>

      {/* Summary */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-3 text-gray-800">Summary</h3>
        <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
      </div>

      {/* Red Flags */}
      {analysis.red_flags && analysis.red_flags.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-3 text-gray-800">Red Flags</h3>
          <div className="space-y-2">
            {analysis.red_flags.map((flag, index) => (
              <div key={index} className="flex items-start gap-2 text-gray-700">
                <span className="mt-1">{flag}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Price Analysis */}
      {analysis.price_analysis && (
        <div className="mb-6 bg-blue-50 rounded-lg p-4">
          <h3 className="text-xl font-semibold mb-3 text-gray-800">Price Analysis</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Listed Price</p>
              <p className="text-lg font-bold text-gray-800">
                ${analysis.price_analysis.listed_price.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Fair Price Range</p>
              <p className="text-lg font-bold text-gray-800">
                ${analysis.price_analysis.fair_price_min.toFixed(2)} - ${analysis.price_analysis.fair_price_max.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Market Average</p>
              <p className="text-lg font-bold text-gray-800">
                ${analysis.price_analysis.market_average.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Price Difference</p>
              <p className={`text-lg font-bold ${
                analysis.price_analysis.overpricing_percentage > 25 ? 'text-danger' :
                analysis.price_analysis.overpricing_percentage > 10 ? 'text-warning' :
                'text-success'
              }`}>
                {analysis.price_analysis.overpricing_percentage > 0 ? '+' : ''}
                {analysis.price_analysis.overpricing_percentage.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Claim Verifications */}
      {analysis.verifications && analysis.verifications.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-3 text-gray-800">
            Claim Analysis ({analysis.verifications.length} claims)
          </h3>
          <div className="space-y-3">
            {analysis.verifications.map((verification, index) => {
              const badge = getStatusBadge(verification.status);
              return (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-sm text-gray-700 flex-1 mr-3">
                      "{verification.claim}"
                    </p>
                    <span className={`${badge.color} px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap`}>
                      {badge.text}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    <strong>Analysis:</strong> {verification.reasoning}
                  </p>
                  {verification.technical_details && (
                    <p className="text-xs text-gray-500 mt-2 italic">
                      {verification.technical_details}
                    </p>
                  )}
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          verification.confidence > 0.8 ? 'bg-success' :
                          verification.confidence > 0.6 ? 'bg-warning' :
                          'bg-danger'
                        }`}
                        style={{ width: `${verification.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">
                      {(verification.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div>
          <h3 className="text-xl font-semibold mb-3 text-gray-800">Recommendations</h3>
          <div className="space-y-2">
            {analysis.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start gap-2 text-gray-700">
                <span className="mt-1">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
