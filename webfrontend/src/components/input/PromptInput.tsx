import React from 'react';
import { EssayType, SAQType } from '../../types/api';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  essayType: EssayType | null;
  saqType?: SAQType | null;
  disabled?: boolean;
  error?: string;
  className?: string;
  id?: string;
  ariaDescribedBy?: string;
}

const PromptInput: React.FC<PromptInputProps> = ({
  value,
  onChange,
  essayType,
  saqType,
  disabled = false,
  error,
  className = '',
  id,
  ariaDescribedBy
}) => {
  const getPlaceholder = (): string => {
    if (!essayType) {
      return 'Enter the essay prompt or question...';
    }

    switch (essayType) {
      case 'DBQ':
        return 'Enter the DBQ prompt and documents context...';
      
      case 'LEQ':
        return 'Enter the Long Essay Question prompt...';
      
      case 'SAQ':
        if (!saqType) {
          return 'Enter the SAQ prompt or question...';
        }
        
        switch (saqType) {
          case 'stimulus':
            return 'Enter the SAQ prompt with stimulus document information...';
          case 'non_stimulus':
            return 'Enter the SAQ content-based question...';
          case 'secondary_comparison':
            return 'Enter the SAQ prompt with historical interpretations to compare...';
          default:
            return 'Enter the SAQ prompt or question...';
        }
      
      default:
        return 'Enter the essay prompt or question...';
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const baseClasses = `
    w-full px-4 py-3 border rounded-lg shadow-sm
    text-sm leading-relaxed font-medium
    transition-all duration-200 ease-in-out
    focus:outline-none focus:ring-2 focus:ring-offset-1
    disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
    placeholder:text-gray-400
  `;

  const stateClasses = error
    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500 hover:border-gray-400';

  const combinedClasses = `${baseClasses} ${stateClasses} ${className}`;

  return (
    <div className="space-y-2">
      <input
        type="text"
        id={id}
        value={value}
        onChange={handleChange}
        placeholder={getPlaceholder()}
        disabled={disabled}
        className={combinedClasses}
        aria-describedby={ariaDescribedBy}
      />
      
      {error && (
        <div className="text-sm text-red-600 mt-1">
          {error}
        </div>
      )}
    </div>
  );
};

export default PromptInput;