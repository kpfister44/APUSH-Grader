import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GradingPage from './pages/GradingPage';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<GradingPage />} />
      </Routes>
    </Router>
  );
};

export default App;