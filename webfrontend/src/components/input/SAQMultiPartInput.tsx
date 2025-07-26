import React from 'react';

interface SAQParts {
  part_a: string;
  part_b: string;
  part_c: string;
}

interface SAQMultiPartInputProps {
  saqParts: SAQParts;
  onPartChange: (part: keyof SAQParts, value: string) => void;
  disabled?: boolean;
  validationErrors?: Record<string, string>;
}

const SAQMultiPartInput: React.FC<SAQMultiPartInputProps> = ({
  saqParts,
  onPartChange,
  disabled = false,
  validationErrors = {}
}) => {
  const parts = [
    {
      key: 'part_a' as keyof SAQParts,
      label: 'Part A',
      placeholder: 'Enter your response for Part A...',
      description: 'First part of your SAQ response'
    },
    {
      key: 'part_b' as keyof SAQParts,
      label: 'Part B',
      placeholder: 'Enter your response for Part B...',
      description: 'Second part of your SAQ response'
    },
    {
      key: 'part_c' as keyof SAQParts,
      label: 'Part C',
      placeholder: 'Enter your response for Part C...',
      description: 'Third part of your SAQ response'
    }
  ];

  const getCharacterCount = (text: string) => text.length;
  const getWordCount = (text: string) => text.trim() ? text.trim().split(/\s+/).length : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
        <h3 className="text-lg font-medium text-gray-900">SAQ Response</h3>
      </div>
      
      <div className="text-sm text-gray-600 mb-6">
        Provide your responses for each part. You can fill out any or all parts as needed.
      </div>

      {parts.map((part, index) => {
        const value = saqParts[part.key];
        const hasError = validationErrors[part.key];
        const wordCount = getWordCount(value);
        const charCount = getCharacterCount(value);
        const hasContent = value.trim().length > 0;

        return (
          <div key={part.key} className="space-y-3">
            {/* Part Header - Simple and Clean */}
            <label 
              htmlFor={`saq-${part.key}`}
              className="block text-sm font-medium text-gray-700"
            >
              {part.label}
            </label>

            {/* Text Area - Full Width */}
            <textarea
              id={`saq-${part.key}`}
              value={value}
              onChange={(e) => onPartChange(part.key, e.target.value)}
              placeholder={part.placeholder}
              disabled={disabled}
              rows={4}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm resize-none
                text-sm leading-relaxed
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
                transition-colors duration-200
                ${hasError 
                  ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                  : ''
                }
              `}
              style={{ width: '100%', minWidth: '100%' }}
              aria-describedby={`${part.key}-stats`}
            />

            {/* Statistics and Error Message - Tighter Spacing */}
            <div className="space-y-1">
              {/* Error Message */}
              {hasError && (
                <div className="text-sm text-red-600">
                  {hasError}
                </div>
              )}

              {/* Statistics - Words Only */}
              <div 
                id={`${part.key}-stats`}
                className="text-xs text-gray-500"
              >
                <span>{wordCount} words</span>
              </div>
            </div>
          </div>
        );
      })}

      {/* Overall Statistics */}
      <div className="bg-gray-50 rounded-lg p-4 mt-6">
        <div className="text-sm font-medium text-gray-900 mb-2">Overall Progress</div>
        <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
          <div className="text-center">
            <div className="font-semibold text-lg">
              {parts.filter(part => saqParts[part.key].trim().length > 0).length}/3
            </div>
            <div>Parts Completed</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-lg">
              {parts.reduce((total, part) => total + getWordCount(saqParts[part.key]), 0)}
            </div>
            <div>Total Words</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SAQMultiPartInput;