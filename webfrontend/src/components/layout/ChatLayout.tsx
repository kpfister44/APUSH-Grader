import React from 'react';

interface ChatLayoutProps {
  children: React.ReactNode;
}

/**
 * Main layout component inspired by ChatGPT's clean, centered design
 * - Centered layout with 768px max-width
 * - Responsive padding and spacing
 * - Clean background with subtle styling
 */
const ChatLayout: React.FC<ChatLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  );
};

export default ChatLayout;