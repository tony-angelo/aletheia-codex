import React from 'react';
import { ConfidenceBadgeProps } from '../types/review';

const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ 
  confidence, 
  size = 'md' 
}) => {
  const getConfidenceClass = (score: number) => {
    if (score >= 0.8) return 'confidence-high';
    if (score >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  const getSizeClass = (size: string) => {
    switch (size) {
      case 'sm': return 'text-xs';
      case 'lg': return 'text-sm';
      default: return 'text-xs';
    }
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  const confidenceClass = getConfidenceClass(confidence);
  const sizeClass = getSizeClass(size);
  const label = getConfidenceLabel(confidence);

  return (
    <span className={`${confidenceClass} ${sizeClass}`}>
      {label} ({Math.round(confidence * 100)}%)
    </span>
  );
};

export default ConfidenceBadge;