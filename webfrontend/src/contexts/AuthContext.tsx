import React, { createContext, useContext, useState, useEffect } from 'react';
import { getConfig } from '../services/config';

interface AuthContextType {
  isAuthenticated: boolean;
  sessionToken: string | null;
  login: (token: string) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session token in sessionStorage
    const token = sessionStorage.getItem('session_token');
    if (token) {
      // Verify the token is still valid
      verifyToken(token);
    } else {
      setIsLoading(false);
    }
  }, []);

  const verifyToken = async (token: string) => {
    try {
      const config = getConfig();
      const response = await fetch(`${config.baseUrl}/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSessionToken(token);
      } else {
        // Token is invalid, remove it
        sessionStorage.removeItem('session_token');
        setSessionToken(null);
      }
    } catch (error) {
      // Connection error, remove token
      sessionStorage.removeItem('session_token');
      setSessionToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = (token: string) => {
    setSessionToken(token);
    sessionStorage.setItem('session_token', token);
  };

  const logout = async () => {
    const token = sessionToken;
    
    // Clear local state first
    setSessionToken(null);
    sessionStorage.removeItem('session_token');

    // Try to notify the server (fire and forget)
    if (token) {
      try {
        const config = getConfig();
        await fetch(`${config.baseUrl}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (error) {
        // Ignore logout errors - user is already logged out locally
      }
    }
  };

  const value: AuthContextType = {
    isAuthenticated: !!sessionToken,
    sessionToken,
    login,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};