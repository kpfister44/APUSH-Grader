import React from 'react';
import { SAQType, SAQ_TYPES } from '../../types/api';

interface SAQTypeSelectorProps {
  selectedType: SAQType | null;
  onTypeChange: (type: SAQType | null) => void;
  disabled?: boolean;
}

const SAQTypeSelector: React.FC<SAQTypeSelectorProps> = ({
  selectedType,
  onTypeChange,
  disabled = false
}) => {
  return (
    <div className="space-y-3">
      <label 
        htmlFor="saq-type-select" 
        className="block text-sm font-medium text-gray-700"
      >
        SAQ Type <span className="text-gray-500">(optional)</span>
      </label>
      
      <div className="relative">
        <select
          id="saq-type-select"
          value={selectedType || ''}
          onChange={(e) => onTypeChange(e.target.value as SAQType || null)}
          disabled={disabled}
          className={`
            block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm
            bg-white text-gray-900 text-sm
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
            transition-colors duration-200
          `}
          aria-describedby="saq-type-description"
        >
          <option value="">Select SAQ type (optional)</option>
          {(Object.keys(SAQ_TYPES) as SAQType[]).map((type) => {
            const typeInfo = SAQ_TYPES[type];
            return (
              <option key={type} value={type}>
                {typeInfo.label} - {typeInfo.description}
              </option>
            );
          })}
        </select>
        
        {/* Custom dropdown arrow */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <svg 
            className="w-4 h-4 text-gray-400" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M19 9l-7 7-7-7" 
            />
          </svg>
        </div>
      </div>

      {/* Help text */}
      <div id="saq-type-description" className="text-xs text-gray-500">
        Choose the specific type of SAQ for more accurate grading feedback.
      </div>
    </div>
  );
};

export default SAQTypeSelector;