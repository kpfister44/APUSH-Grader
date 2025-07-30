import React, { useState } from 'react';
import { GradingResponse } from '../../types/api';
import { ScoreVisualizer, PerformanceBadge } from './ScoreVisualizer';

interface ResultsDisplayProps {
  result: GradingResponse;
  onNewEssay: () => void;
}

/**
 * Enhanced results display component with score visualization and expandable sections
 */
export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  result,
  onNewEssay
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  
  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };
  
  const isExpanded = (sectionId: string) => expandedSections.has(sectionId);
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header with score visualization */}
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <ScoreVisualizer
              score={result.score}
              maxScore={result.max_score}
              percentage={result.percentage}
              letterGrade={`${result.score}/${result.max_score}`}
              performanceLevel={result.performance_level}
              animated={true}
              size="large"
            />
            <div className="flex flex-col justify-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Essay Grading Complete
              </h3>
              <PerformanceBadge
                letterGrade={result.letter_grade}
                performanceLevel={result.performance_level}
                score={result.score}
                maxScore={result.max_score}
                size="medium"
              />
            </div>
          </div>
          <button
            onClick={onNewEssay}
            className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors"
          >
            Grade Another Essay
          </button>
        </div>
      </div>
      
      {/* Main content area */}
      <div className="p-6 space-y-4">
        {/* Overall feedback section */}
        {result.overall_feedback && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
              <span className="text-blue-600">💬</span>
              Overall Feedback
            </h4>
            <p className="text-blue-800 text-sm leading-relaxed">
              {result.overall_feedback}
            </p>
          </div>
        )}
        
        {/* Rubric breakdown section */}
        <div className="space-y-3">
          <button
            onClick={() => toggleSection('breakdown')}
            className="w-full flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-gray-600">📊</span>
              <h4 className="font-medium text-gray-900">Detailed Score Breakdown</h4>
            </div>
            <span className={`transform transition-transform ${isExpanded('breakdown') ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
          
          {isExpanded('breakdown') && (
            <div className="border border-gray-200 rounded-lg p-4 space-y-3">
              {Object.entries(result.breakdown).map(([section, details]) => (
                <div key={section} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900 capitalize mb-1">
                      {section.replace(/_/g, ' ')}
                    </h5>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {details.feedback}
                    </p>
                  </div>
                  <div className="ml-4">
                    <ScoreVisualizer
                      score={details.score}
                      maxScore={details.max_score}
                      percentage={(details.score / details.max_score) * 100}
                      letterGrade={`${details.score}/${details.max_score}`}
                      performanceLevel="" // Not used anymore, colors based on score
                      animated={true}
                      size="small"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Suggestions section */}
        {result.suggestions && result.suggestions.length > 0 && (
          <div className="space-y-3">
            <button
              onClick={() => toggleSection('suggestions')}
              className="w-full flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-gray-600">💡</span>
                <h4 className="font-medium text-gray-900">Improvement Suggestions</h4>
              </div>
              <span className={`transform transition-transform ${isExpanded('suggestions') ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>
            
            {isExpanded('suggestions') && (
              <div className="border border-gray-200 rounded-lg p-4">
                <ul className="space-y-2">
                  {result.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start gap-3 text-sm">
                      <span className="text-amber-500 mt-0.5">•</span>
                      <span className="text-gray-700 leading-relaxed">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {/* Warnings section */}
        {result.warnings && result.warnings.length > 0 && (
          <div className="space-y-3">
            <button
              onClick={() => toggleSection('warnings')}
              className="w-full flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg hover:bg-yellow-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-yellow-600">⚠️</span>
                <h4 className="font-medium text-yellow-900">Processing Warnings</h4>
              </div>
              <span className={`transform transition-transform ${isExpanded('warnings') ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>
            
            {isExpanded('warnings') && (
              <div className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                <ul className="space-y-2">
                  {result.warnings.map((warning, index) => (
                    <li key={index} className="flex items-start gap-3 text-sm">
                      <span className="text-yellow-600 mt-0.5">⚠</span>
                      <span className="text-yellow-800 leading-relaxed">{warning}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {/* Essay statistics */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
            <span className="text-gray-600">📈</span>
            Essay Statistics
          </h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Word Count:</span>
              <span className="ml-2 font-medium text-gray-900">{result.word_count}</span>
            </div>
            <div>
              <span className="text-gray-600">Paragraphs:</span>
              <span className="ml-2 font-medium text-gray-900">{result.paragraph_count}</span>
            </div>
            {result.processing_time_ms && (
              <div className="col-span-2">
                <span className="text-gray-600">Processing Time:</span>
                <span className="ml-2 font-medium text-gray-900">
                  {(result.processing_time_ms / 1000).toFixed(1)}s
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};