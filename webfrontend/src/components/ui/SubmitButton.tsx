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
        w-full py-4 px-8 rounded-xl font-medium text-base
        transition-all duration-200 ease-out
        focus:outline-none focus:ring-2 focus:ring-orange-400 focus:ring-offset-2
        ${isDisabled 
          ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
          : 'bg-orange-500 text-white hover:bg-orange-600 shadow-sm hover:shadow-md'
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
            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span>{loadingMessages[currentMessage]}</span>
        </div>
      ) : (
        <span className="flex items-center justify-center gap-2">
          <span>✦</span>
          <span>Grade Essay</span>
        </span>
      )}
    </button>
  );
};

export default SubmitButton;