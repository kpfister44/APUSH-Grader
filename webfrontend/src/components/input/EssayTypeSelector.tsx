import React from 'react';
import { EssayType, ESSAY_TYPES } from '../../types/api';

interface EssayTypeSelectorProps {
  selectedType: EssayType | null;
  onTypeChange: (type: EssayType) => void;
  disabled?: boolean;
}

const EssayTypeSelector: React.FC<EssayTypeSelectorProps> = ({
  selectedType,
  onTypeChange,
  disabled = false
}) => {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Essay Type
      </label>
      <div 
        className="flex flex-col sm:flex-row gap-3"
        role="group"
        aria-label="Select essay type"
      >
        {(Object.keys(ESSAY_TYPES) as EssayType[]).map((type) => {
          const typeInfo = ESSAY_TYPES[type];
          const isSelected = selectedType === type;
          
          return (
            <button
              key={type}
              type="button"
              onClick={() => onTypeChange(type)}
              disabled={disabled}
              className={`
                flex-1 px-4 py-3 rounded-lg border text-sm font-medium 
                transition-all duration-200 ease-out transform
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:scale-[1.02] active:scale-[0.98]
                ${isSelected
                  ? 'bg-blue-50 border-blue-200 text-blue-700 shadow-md scale-[1.01]'
                  : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:shadow-md'
                }
              `}
              aria-pressed={isSelected}
              aria-describedby={`${type}-description`}
            >
              <div className="text-center">
                <div className="font-semibold">{type}</div>
                <div className="text-xs mt-1 opacity-75">
                  {typeInfo.label}
                </div>
                <div className="text-xs mt-0.5 opacity-60">
                  {typeInfo.maxScore} points
                </div>
              </div>
            </button>
          );
        })}
      </div>
      
      {/* Description for screen readers */}
      {(Object.keys(ESSAY_TYPES) as EssayType[]).map((type) => (
        <div
          key={`${type}-description`}
          id={`${type}-description`}
          className="sr-only"
        >
          {ESSAY_TYPES[type].description}
        </div>
      ))}
    </div>
  );
};

export default EssayTypeSelector;