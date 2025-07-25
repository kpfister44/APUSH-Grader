import React from 'react';

interface MainContentProps {
  children: React.ReactNode;
}

/**
 * Main content area component inspired by ChatGPT's conversation interface
 * - Clean white background with subtle shadows
 * - Proper spacing and padding using 8px grid system
 * - Responsive design for all screen sizes
 */
const MainContent: React.FC<MainContentProps> = ({ children }) => {
  return (
    <main className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 sm:p-8">
        {children}
      </div>
    </main>
  );
};

export default MainContent;