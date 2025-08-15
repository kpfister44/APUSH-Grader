import React, { useState, useCallback } from 'react';
import { GradingResponse } from '../../types/api';
import { ScoreVisualizer, PerformanceBadge } from './ScoreVisualizer';
import { PDFExport } from '../pdf';
import { useGrading } from '../../contexts/GradingContext';

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
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copying' | 'copied' | 'error'>('idle');
  const { state } = useGrading();
  
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
  
  const copyToClipboard = useCallback(async (text: string) => {
    setCopyStatus('copying');
    
    try {
      // Modern Clipboard API
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers or non-secure contexts
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      
      setCopyStatus('copied');
      
      // Reset status after 2 seconds
      setTimeout(() => setCopyStatus('idle'), 2000);
      
    } catch (err) {
      console.error('Failed to copy text: ', err);
      setCopyStatus('error');
      
      // Reset status after 2 seconds
      setTimeout(() => setCopyStatus('idle'), 2000);
    }
  }, []);
  
  const isExpanded = (sectionId: string) => expandedSections.has(sectionId);
  
  // Helper function to format breakdown section names
  const formatSectionName = (section: string): string => {
    const sectionMap: Record<string, string> = {
      'thesis': 'Thesis',
      'contextualization': 'Contextualization', 
      'evidence': 'Evidence',
      'analysis': 'Analysis',
      'part_a': 'Part A',
      'part_b': 'Part B',
      'part_c': 'Part C',
      'criterion_a': 'Criterion A (Complete Sentences)',
      'criterion_c': 'Criterion C (Evidence)',
      'criterion_e': 'Criterion E (Explanation)'
    };
    
    return sectionMap[section] || section.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden animate-in slide-in-from-bottom-4 fade-in duration-500 ease-out">
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
          <div className="flex flex-col gap-3">
            <button
              onClick={onNewEssay}
              className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-lg hover:bg-gray-700 hover:scale-105 active:scale-95 transition-all duration-200 ease-out transform"
            >
              Grade Another Essay
            </button>
            
            {/* PDF Export Button */}
            {state.form.essayType && (
              <PDFExport
                result={result}
                essayType={state.form.essayType}
                prompt={state.form.prompt}
                essayText={state.form.essayText}
                saqParts={state.form.saqParts}
                saqType={state.form.saqType}
                rubricType={state.form.rubricType}
              />
            )}
          </div>
        </div>
      </div>
      
      {/* Main content area */}
      <div className="p-6 space-y-4">
        {/* Overall feedback section */}
        {result.overall_feedback && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 animate-in fade-in slide-in-from-left-2 duration-300 delay-100 ease-out relative">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-blue-900 flex items-center gap-2">
                <span className="text-blue-600">💬</span>
                Overall Feedback
              </h4>
              <button
                onClick={() => copyToClipboard(result.overall_feedback)}
                disabled={copyStatus === 'copying'}
                className={`
                  px-2 py-1 text-xs font-medium rounded transition-all duration-200 ease-out
                  ${copyStatus === 'copied' 
                    ? 'bg-green-100 text-green-700 border border-green-200' 
                    : copyStatus === 'error'
                    ? 'bg-red-100 text-red-700 border border-red-200'
                    : 'bg-blue-100 text-blue-700 border border-blue-200 hover:bg-blue-200 hover:scale-105 active:scale-95'
                  }
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                title="Copy feedback to clipboard"
              >
                {copyStatus === 'copying' && '⏳'}
                {copyStatus === 'copied' && '✓ Copied!'}
                {copyStatus === 'error' && '✗ Error'}
                {copyStatus === 'idle' && 'Copy'}
              </button>
            </div>
            <p className="text-blue-800 text-sm leading-relaxed">
              {result.overall_feedback}
            </p>
          </div>
        )}
        
        {/* Rubric breakdown section */}
        <div className="space-y-3 animate-in fade-in slide-in-from-left-2 duration-300 delay-200 ease-out">
          <button
            onClick={() => toggleSection('breakdown')}
            className="w-full flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:shadow-sm transition-all duration-200 ease-out"
          >
            <div className="flex items-center gap-2">
              <span className="text-gray-600">📊</span>
              <h4 className="font-medium text-gray-900">Detailed Score Breakdown</h4>
            </div>
            <span className={`transform transition-transform duration-300 ease-out ${isExpanded('breakdown') ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
          
          {isExpanded('breakdown') && (
            <div className="border border-gray-200 rounded-lg p-4 space-y-3 animate-in fade-in slide-in-from-top-2 duration-300 ease-out">
              {Object.entries(result.breakdown).map(([section, details]) => (
                <div key={section} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900 mb-1">
                      {formatSectionName(section)}
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
          <div className="space-y-3 animate-in fade-in slide-in-from-left-2 duration-300 delay-300 ease-out">
            <button
              onClick={() => toggleSection('suggestions')}
              className="w-full flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:shadow-sm transition-all duration-200 ease-out"
            >
              <div className="flex items-center gap-2">
                <span className="text-gray-600">💡</span>
                <h4 className="font-medium text-gray-900">Improvement Suggestions</h4>
              </div>
              <span className={`transform transition-transform duration-300 ease-out ${isExpanded('suggestions') ? 'rotate-180' : ''}`}>
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
          <div className="space-y-3 animate-in fade-in slide-in-from-left-2 duration-300 delay-400 ease-out">
            <button
              onClick={() => toggleSection('warnings')}
              className="w-full flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg hover:bg-yellow-100 hover:shadow-sm transition-all duration-200 ease-out"
            >
              <div className="flex items-center gap-2">
                <span className="text-yellow-600">⚠️</span>
                <h4 className="font-medium text-yellow-900">Processing Warnings</h4>
              </div>
              <span className={`transform transition-transform duration-300 ease-out ${isExpanded('warnings') ? 'rotate-180' : ''}`}>
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
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 animate-in fade-in slide-in-from-left-2 duration-300 delay-500 ease-out">
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