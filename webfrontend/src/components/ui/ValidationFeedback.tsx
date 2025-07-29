import React from 'react';

interface ValidationFeedbackProps {
  error?: string;
  className?: string;
}

export const ValidationFeedback: React.FC<ValidationFeedbackProps> = ({ 
  error, 
  className = '' 
}) => {
  if (!error) return null;

  return (
    <div className={`flex items-center gap-2 text-red-600 text-sm mt-1 ${className}`}>
      <span className="text-red-500">⚠</span>
      <span>{error}</span>
    </div>
  );
};

export default ValidationFeedback;