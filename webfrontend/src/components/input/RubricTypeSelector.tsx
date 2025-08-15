import React from 'react';
import { RubricType, RUBRIC_TYPES } from '../../types/api';

interface RubricTypeSelectorProps {
  selectedType: RubricType;
  onTypeChange: (type: RubricType) => void;
  disabled?: boolean;
}

const RubricTypeSelector: React.FC<RubricTypeSelectorProps> = ({
  selectedType,
  onTypeChange,
  disabled = false
}) => {
  return (
    <div className="space-y-3">
      <label 
        htmlFor="rubric-type-select" 
        className="block text-sm font-medium text-gray-700"
      >
        Rubric Type
      </label>
      
      <div className="space-y-2">
        {(Object.keys(RUBRIC_TYPES) as RubricType[]).map((type) => {
          const rubricInfo = RUBRIC_TYPES[type];
          return (
            <label key={type} className="flex items-start space-x-3 cursor-pointer">
              <input
                type="radio"
                id={`rubric-${type}`}
                name="rubric-type"
                value={type}
                checked={selectedType === type}
                onChange={(e) => onTypeChange(e.target.value as RubricType)}
                disabled={disabled}
                className={`
                  mt-1 h-4 w-4 text-blue-600 border-gray-300
                  focus:ring-blue-500 focus:ring-2
                  disabled:cursor-not-allowed disabled:opacity-50
                `}
              />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">
                    {rubricInfo.label}
                  </span>
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                    {rubricInfo.maxScore} points
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {rubricInfo.description}
                </div>
              </div>
            </label>
          );
        })}
      </div>

      {/* Help text */}
      <div className="text-xs text-gray-500 bg-blue-50 p-3 rounded-lg border border-blue-200">
        <div className="font-medium text-blue-800 mb-1">Rubric Differences:</div>
        <div className="space-y-1">
          <div><strong>College Board:</strong> Traditional 3-point part-based scoring</div>
          <div><strong>EG:</strong> 10-point A/C/E criteria with strict requirements</div>
        </div>
      </div>
    </div>
  );
};

export default RubricTypeSelector;