import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiLogin, apiRegister, apiGetProfile, apiSaveProfile, UserProfile } from '@/app/api/user';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  userEmail: string | null;
  profile: UserProfile | null;
  isLoading: boolean;
  favoriteCarIds: number[];
  login: (email: string, password: string) => Promise<{ hasProfile: boolean }>;
  register: (email: string, password: string) => Promise<{ hasProfile: boolean }>;
  logout: () => void;
  saveProfile: (data: Omit<UserProfile, 'email'>) => Promise<void>;
  toggleFavorite: (id: number) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('as_token'));
  const [userEmail, setUserEmail] = useState<string | null>(() => localStorage.getItem('as_email'));
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [favoriteCarIds, setFavoriteCarIds] = useState<number[]>(() => {
    const email = localStorage.getItem('as_email');
    if (!email) return [];
    const stored = localStorage.getItem(`as_favorites_${email}`);
    return stored ? JSON.parse(stored) : [];
  });

  const isAuthenticated = !!token;

  useEffect(() => {
    if (token) {
      apiGetProfile(token)
        .then(setProfile)
        .catch(() => setProfile(null));
    }
  }, [token]);

  const persistFavorites = useCallback((ids: number[], email: string | null) => {
    if (email) localStorage.setItem(`as_favorites_${email}`, JSON.stringify(ids));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const { access_token } = await apiLogin(email, password);
      localStorage.setItem('as_token', access_token);
      localStorage.setItem('as_email', email);
      setToken(access_token);
      setUserEmail(email);

      const stored = localStorage.getItem(`as_favorites_${email}`);
      setFavoriteCarIds(stored ? JSON.parse(stored) : []);

      try {
        const prof = await apiGetProfile(access_token);
        setProfile(prof);
        return { hasProfile: true };
      } catch (e: any) {
        if (e.status === 404) return { hasProfile: false };
        throw e;
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const { access_token } = await apiRegister(email, password);
      localStorage.setItem('as_token', access_token);
      localStorage.setItem('as_email', email);
      setToken(access_token);
      setUserEmail(email);
      setFavoriteCarIds([]);
      return { hasProfile: false };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('as_token');
    localStorage.removeItem('as_email');
    setToken(null);
    setUserEmail(null);
    setProfile(null);
    setFavoriteCarIds([]);
  }, []);

  const saveProfile = useCallback(async (data: Omit<UserProfile, 'email'>) => {
    if (!token) throw new Error('Not authenticated');
    const saved = await apiSaveProfile(token, data);
    setProfile(saved);
  }, [token]);

  const toggleFavorite = useCallback((id: number) => {
    setFavoriteCarIds(prev => {
      const next = prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id];
      persistFavorites(next, userEmail);
      return next;
    });
  }, [userEmail, persistFavorites]);

  return (
    <AuthContext.Provider value={{
      isAuthenticated, token, userEmail, profile, isLoading,
      favoriteCarIds, login, register, logout, saveProfile, toggleFavorite,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
