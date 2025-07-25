import React from 'react';

/**
 * Header component with ChatGPT-style minimal design
 * - Clean typography for app title
 * - Subtle branding without overwhelming the interface
 * - Responsive design with proper spacing
 */
const Header: React.FC = () => {
  return (
    <header className="mb-8">
      <div className="text-center">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2">
          APUSH Grader
        </h1>
        <p className="text-gray-600 text-lg">
          AI-powered AP US History essay grading
        </p>
      </div>
    </header>
  );
};

export default Header;