import React, { useEffect, useRef } from 'react';

interface ChatTextAreaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  minRows?: number;
  maxRows?: number;
  className?: string;
  id?: string;
  ariaDescribedBy?: string;
}

const ChatTextArea: React.FC<ChatTextAreaProps> = ({
  value,
  onChange,
  placeholder = 'Enter your essay text here...',
  disabled = false,
  error,
  minRows = 4,
  maxRows = 20,
  className = '',
  id,
  ariaDescribedBy
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize functionality
  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to calculate actual scrollHeight
    textarea.style.height = 'auto';
    
    // Calculate the number of rows based on content
    const lineHeight = parseInt(getComputedStyle(textarea).lineHeight);
    const currentRows = Math.ceil(textarea.scrollHeight / lineHeight);
    
    // Constrain between min and max rows
    const constrainedRows = Math.max(minRows, Math.min(maxRows, currentRows));
    
    // Set the height based on constrained rows
    textarea.style.height = `${constrainedRows * lineHeight}px`;
  };

  // Adjust height on value change
  useEffect(() => {
    adjustHeight();
  }, [value]);

  // Adjust height on component mount
  useEffect(() => {
    adjustHeight();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const baseClasses = `
    w-full px-4 py-3 border rounded-lg shadow-sm resize-none
    text-sm leading-relaxed font-medium
    transition-all duration-200 ease-in-out transform
    focus:outline-none focus:ring-2 focus:ring-offset-1
    disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
    placeholder:text-gray-400
    hover:shadow-md focus:shadow-lg focus:scale-[1.01]
  `;

  const stateClasses = error
    ? 'border-red-300 focus:ring-red-500 focus:border-red-500 focus:shadow-red-100'
    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500 hover:border-gray-400 focus:shadow-blue-100';

  const combinedClasses = `${baseClasses} ${stateClasses} ${className}`;

  return (
    <div className="space-y-2">
      <textarea
        ref={textareaRef}
        id={id}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        className={combinedClasses}
        aria-describedby={ariaDescribedBy}
        rows={minRows}
        style={{
          minHeight: `${minRows * 1.5}rem`,
          maxHeight: `${maxRows * 1.5}rem`,
        }}
      />
      
      {error && (
        <div className="text-sm text-red-600 mt-1">
          {error}
        </div>
      )}
    </div>
  );
};

export default ChatTextArea;