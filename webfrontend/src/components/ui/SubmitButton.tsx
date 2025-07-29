import React from 'react';

interface SubmitButtonProps {
  isValid: boolean;
  isSubmitting: boolean;
  onClick: () => void;
  className?: string;
}

export const SubmitButton: React.FC<SubmitButtonProps> = ({
  isValid,
  isSubmitting,
  onClick,
  className = ''
}) => {
  const isDisabled = !isValid || isSubmitting;

  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      className={`
        w-full py-3 px-6 rounded-lg font-medium transition-all duration-200
        ${isDisabled 
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
          : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
        }
        ${className}
      `}
    >
      {isSubmitting ? (
        <div className="flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>Grading Essay...</span>
        </div>
      ) : (
        'Grade Essay'
      )}
    </button>
  );
};

export default SubmitButton;