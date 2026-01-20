import React from 'react';

export default function ScoreIndicator({ score, label, type = 'reality' }) {
  // Determine color based on score
  const getColor = () => {
    if (score >= 80) return 'text-success';
    if (score >= 60) return 'text-warning';
    return 'text-danger';
  };

  const getBgColor = () => {
    if (score >= 80) return 'bg-success';
    if (score >= 60) return 'bg-warning';
    return 'bg-danger';
  };

  const getDescription = () => {
    if (type === 'reality') {
      if (score >= 80) return 'Highly credible';
      if (score >= 60) return 'Some concerns';
      return 'Many red flags';
    } else {
      if (score >= 80) return 'Fair price';
      if (score >= 60) return 'Slightly high';
      return 'Overpriced';
    }
  };

  return (
    <div className="text-center">
      <div className="relative inline-flex items-center justify-center w-32 h-32">
        {/* Background circle */}
        <svg className="w-32 h-32 transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-200"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${2 * Math.PI * 56}`}
            strokeDashoffset={`${2 * Math.PI * 56 * (1 - score / 100)}`}
            className={getBgColor()}
            strokeLinecap="round"
          />
        </svg>
        {/* Score text */}
        <span className={`absolute text-3xl font-bold ${getColor()}`}>
          {score.toFixed(0)}
        </span>
      </div>
      <p className="mt-2 text-lg font-semibold text-gray-800">{label}</p>
      <p className={`text-sm font-medium ${getColor()}`}>{getDescription()}</p>
    </div>
  );
}
