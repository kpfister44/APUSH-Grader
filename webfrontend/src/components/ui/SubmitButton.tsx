import React, { useState, useEffect } from 'react';

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
  const [currentMessage, setCurrentMessage] = useState(0);
  
  // Progressive loading messages
  const loadingMessages = [
    'Analyzing essay...',
    'Processing with AI...',
    'Evaluating content...',
    'Generating feedback...',
    'Almost done...'
  ];
  
  // Cycle through loading messages every 3 seconds
  useEffect(() => {
    if (!isSubmitting) {
      setCurrentMessage(0);
      return;
    }
    
    const interval = setInterval(() => {
      setCurrentMessage(prev => (prev + 1) % loadingMessages.length);
    }, 3000);
    
    return () => clearInterval(interval);
  }, [isSubmitting, loadingMessages.length]);

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
      style={{
        cursor: isDisabled ? 'not-allowed' : 'pointer'
      }}
    >
      {isSubmitting ? (
        <div className="flex items-center justify-center gap-3">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span>{loadingMessages[currentMessage]}</span>
        </div>
      ) : (
        'Grade Essay'
      )}
    </button>
  );
};

export default SubmitButton;