import React, { useState } from 'react';
import { getConfig } from '../../services/config';

interface LoginScreenProps {
  onLogin: (sessionToken: string) => void;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const config = getConfig();
      const response = await fetch(`${config.baseUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        onLogin(data.session_token);
      } else {
        setError('Invalid password. Please try again.');
      }
    } catch (err) {
      setError('Unable to connect to the server. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-16 px-6">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex items-center justify-center gap-3 mb-16">
            <div className="w-7 h-7 bg-orange-500 rounded-full flex items-center justify-center">
              <span className="text-white text-base">✦</span>
            </div>
            <h1 className="text-4xl font-normal text-gray-800">
              APUSH Grader
            </h1>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div>
              <label htmlFor="password" className="block text-base font-medium text-gray-800 mb-4">
                Teacher Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full py-4 px-4 border border-gray-300 rounded-xl text-base focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-colors"
                required
                autoFocus
              />
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-red-600 text-base">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !password}
              className="w-full py-4 px-8 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 text-white text-base font-medium rounded-xl transition-colors duration-200"
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        </div>

        <div className="text-center">
          <p className="text-gray-500 text-sm">
            Secure access for authorized APUSH teachers
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;