import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Placeholder components for now
const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md mx-auto text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          APUSH Grader
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          ChatGPT-style web interface for grading AP US History essays.
        </p>
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-sm text-gray-500">
            React + TypeScript + Tailwind CSS setup complete! 🎉
          </p>
        </div>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
      </Routes>
    </Router>
  );
};

export default App;