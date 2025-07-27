import React from 'react';
import ChatTextArea from './ChatTextArea';

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
      placeholder: 'Enter your response for Part A...'
    },
    {
      key: 'part_b' as keyof SAQParts,
      label: 'Part B',
      placeholder: 'Enter your response for Part B...'
    },
    {
      key: 'part_c' as keyof SAQParts,
      label: 'Part C',
      placeholder: 'Enter your response for Part C...'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="text-sm text-gray-600 mb-6">
        Provide your responses for each part. You can fill out any or all parts as needed.
      </div>

      {parts.map((part) => (
        <div key={part.key} className="space-y-3">
          <label 
            htmlFor={`saq-${part.key}`}
            className="block text-sm font-medium text-gray-700"
          >
            {part.label}
          </label>
          
          <ChatTextArea
            id={`saq-${part.key}`}
            value={saqParts[part.key]}
            onChange={(value) => onPartChange(part.key, value)}
            placeholder={part.placeholder}
            disabled={disabled}
            error={validationErrors[part.key]}
            minRows={3}
            maxRows={12}
          />
        </div>
      ))}
    </div>
  );
};

export default SAQMultiPartInput;