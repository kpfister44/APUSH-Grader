import React from 'react';
import { ChatLayout, Header, MainContent } from '../components/layout';

/**
 * Main grading page component using ChatGPT-style layout
 * This will eventually contain the essay grading interface
 */
const GradingPage: React.FC = () => {
  return (
    <ChatLayout>
      <Header />
      <MainContent>
        <div className="text-center space-y-6">
          <h2 className="text-2xl font-semibold text-gray-900">
            Welcome to APUSH Grader
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Ready to start grading AP US History essays with AI assistance.
            The ChatGPT-style interface will be implemented in the next phases.
          </p>
          <div className="bg-gray-50 rounded-lg p-6 text-left">
            <h3 className="font-semibold text-gray-900 mb-3">
              Issue #24 Components Complete:
            </h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                ChatLayout with centered 768px max-width
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                Header component with app title
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                MainContent conversation area
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                React Router basic structure
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                ChatGPT-style typography & spacing
              </li>
            </ul>
          </div>
        </div>
      </MainContent>
    </ChatLayout>
  );
};

export default GradingPage;