import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Placeholder components for now
const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-2xl mx-auto text-center">
        <h1 className="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-6">
          APUSH Grader
        </h1>
        <p className="text-xl text-gray-700 mb-8 font-medium">
          ChatGPT-style web interface for grading AP US History essays.
        </p>
        <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
          <div className="flex items-center justify-center mb-4">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2 animate-pulse"></div>
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
          </div>
          <p className="text-lg text-green-600 font-semibold mb-2">
            ✅ React + TypeScript + Tailwind CSS setup complete!
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
              <p className="text-blue-800 font-semibold">React 18+</p>
              <p className="text-blue-600 text-sm">Modern Components</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
              <p className="text-purple-800 font-semibold">TypeScript</p>
              <p className="text-purple-600 text-sm">Type Safety</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
              <p className="text-green-800 font-semibold">Tailwind CSS</p>
              <p className="text-green-600 text-sm">Utility-First Styling</p>
            </div>
          </div>
          <button className="mt-6 px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-full hover:from-blue-600 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 shadow-lg">
            Ready for Issue #24! 🚀
          </button>
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