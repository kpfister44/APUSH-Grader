import React, { useEffect, useState } from 'react';

interface ScoreVisualizerProps {
  score: number;
  maxScore: number;
  percentage: number;
  letterGrade: string;
  performanceLevel: string;
  animated?: boolean;
  size?: 'small' | 'medium' | 'large';
}

/**
 * Determines the color scheme based on score ratio
 * 3/3 (100%) = Green, 2/3 (67%) = Yellow, 1/3 (33%) = Orange, 0/3 (0%) = Red
 */
const getPerformanceColors = (score: number, maxScore: number) => {
  const ratio = score / maxScore;
  
  if (ratio === 1.0) {
    // Perfect score - Green
    return {
      primary: 'text-green-600',
      secondary: 'text-green-500',
      bg: 'bg-green-50',
      border: 'border-green-200',
      stroke: '#10b981', // green-500
      fill: 'fill-green-100'
    };
  } else if (ratio >= 0.67) {
    // 2/3 or similar - Yellow
    return {
      primary: 'text-yellow-600',
      secondary: 'text-yellow-500',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      stroke: '#eab308', // yellow-500
      fill: 'fill-yellow-100'
    };
  } else if (ratio >= 0.33) {
    // 1/3 or similar - Orange
    return {
      primary: 'text-orange-600',
      secondary: 'text-orange-500',
      bg: 'bg-orange-50', 
      border: 'border-orange-200',
      stroke: '#f97316', // orange-500
      fill: 'fill-orange-100'
    };
  } else {
    // 0/3 or very low scores - Red
    return {
      primary: 'text-red-600',
      secondary: 'text-red-500',
      bg: 'bg-red-50',
      border: 'border-red-200', 
      stroke: '#ef4444', // red-500
      fill: 'fill-red-100'
    };
  }
};

/**
 * Gets size-specific dimensions
 */
const getSizeDimensions = (size: 'small' | 'medium' | 'large') => {
  switch (size) {
    case 'small':
      return {
        container: 'w-16 h-16',
        svg: 64,
        strokeWidth: 4,
        radius: 28,
        textSize: 'text-xs',
        fontSize: '10px'
      };
    case 'large':
      return {
        container: 'w-32 h-32',
        svg: 128,
        strokeWidth: 6,
        radius: 58,
        textSize: 'text-lg',
        fontSize: '14px'
      };
    default: // medium
      return {
        container: 'w-24 h-24',
        svg: 96,
        strokeWidth: 5,
        radius: 43,
        textSize: 'text-sm',
        fontSize: '12px'
      };
  }
};

/**
 * Circular progress indicator with color-coded performance levels
 */
export const ScoreVisualizer: React.FC<ScoreVisualizerProps> = ({
  score,
  maxScore,
  percentage,
  letterGrade,
  performanceLevel,
  animated = true,
  size = 'medium'
}) => {
  const [animatedPercentage, setAnimatedPercentage] = useState(animated ? 0 : percentage);
  const colors = getPerformanceColors(score, maxScore);
  const dimensions = getSizeDimensions(size);
  
  // Animation effect
  useEffect(() => {
    if (!animated) return;
    
    const duration = 1500; // 1.5 seconds
    const steps = 60;
    const increment = percentage / steps;
    let currentStep = 0;
    
    const timer = setInterval(() => {
      currentStep++;
      const newValue = Math.min(currentStep * increment, percentage);
      setAnimatedPercentage(newValue);
      
      if (currentStep >= steps || newValue >= percentage) {
        clearInterval(timer);
        setAnimatedPercentage(percentage);
      }
    }, duration / steps);
    
    return () => clearInterval(timer);
  }, [percentage, animated]);
  
  // Calculate circle properties
  const { svg, strokeWidth, radius } = dimensions;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (animatedPercentage / 100) * circumference;
  const center = svg / 2;
  
  return (
    <div className={`${dimensions.container} relative flex items-center justify-center`}>
      {/* Background circle and progress circle */}
      <svg
        width={svg}
        height={svg}
        className="transform -rotate-90"
        aria-hidden="true"
      >
        {/* Background circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke="#e5e7eb" // gray-200
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        
        {/* Progress circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke={colors.stroke}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{
            transition: animated ? 'stroke-dashoffset 0.1s ease-out' : 'none',
          }}
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className={`font-bold ${colors.primary} ${dimensions.textSize}`}>
          {score}/{maxScore}
        </div>
        <div className={`font-semibold ${colors.secondary}`} style={{ fontSize: dimensions.fontSize }}>
          {Math.round(animatedPercentage)}%
        </div>
      </div>
    </div>
  );
};

/**
 * Performance level badge component
 */
interface PerformanceBadgeProps {
  letterGrade: string;
  performanceLevel: string;
  score: number;
  maxScore: number;
  size?: 'small' | 'medium' | 'large';
}

export const PerformanceBadge: React.FC<PerformanceBadgeProps> = ({
  letterGrade,
  performanceLevel,
  score,
  maxScore,
  size = 'medium'
}) => {
  const colors = getPerformanceColors(score, maxScore);
  
  const sizeClasses = {
    small: 'px-2 py-1 text-xs',
    medium: 'px-3 py-1.5 text-sm',
    large: 'px-4 py-2 text-base'
  };
  
  return (
    <div className={`
      inline-flex items-center rounded-full font-medium
      ${colors.bg} ${colors.border} ${colors.primary} border
      ${sizeClasses[size]}
    `}>
      <span>{performanceLevel}</span>
    </div>
  );
};