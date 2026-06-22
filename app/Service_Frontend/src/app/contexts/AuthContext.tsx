import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiLogin, apiRegister, apiGetProfile, apiSaveProfile, UserProfile } from '@/app/api/user';
import { apiGetFavorites, apiAddFavorite, apiRemoveFavorite } from '@/app/api/cars';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  userEmail: string | null;
  profile: UserProfile | null;
  isLoading: boolean;
  generatingChatId: string | null;
  setGeneratingChatId: (id: string | null) => void;
  favoriteCarIds: string[];
  login: (email: string, password: string) => Promise<{ hasProfile: boolean }>;
  register: (email: string, password: string) => Promise<{ hasProfile: boolean }>;
  logout: () => void;
  saveProfile: (data: Omit<UserProfile, 'email'>) => Promise<void>;
  toggleFavorite: (id: string) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('as_token'));
  const [userEmail, setUserEmail] = useState<string | null>(() => localStorage.getItem('as_email'));
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [favoriteCarIds, setFavoriteCarIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [generatingChatId, setGeneratingChatId] = useState<string | null>(null);

  const isAuthenticated = !!token;

  const logout = useCallback(() => {
    localStorage.removeItem('as_token');
    localStorage.removeItem('as_email');
    setToken(null);
    setUserEmail(null);
    setProfile(null);
    setFavoriteCarIds([]);
  }, []);

  useEffect(() => {
    if (token) {
      apiGetProfile(token)
        .then(setProfile)
        .catch((err) => {
          if (err.status === 401) {
            logout();
          } else {
            setProfile(null);
          }
        });

      apiGetFavorites(token)
        .then((cars) => {
          setFavoriteCarIds(cars.map(car => String(car.id)));
        })
        .catch((err) => {
          if (err.status === 401) {
            logout();
          } else {
            setFavoriteCarIds([]);
          }
        });
    } else {
      setProfile(null);
      setFavoriteCarIds([]);
    }
  }, [token, logout]);

  const persistFavorites = useCallback((ids: string[], email: string | null) => {
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

  const saveProfile = useCallback(async (data: Omit<UserProfile, 'email'>) => {
    if (!token) throw new Error('Not authenticated');
    const saved = await apiSaveProfile(token, data);
    setProfile(saved);
  }, [token]);

  const toggleFavorite = useCallback(async (id: string) => {
    if (!token) return;

    const isFav = favoriteCarIds.includes(id);
    try {
      if (isFav) {
        await apiRemoveFavorite(id, token);
        setFavoriteCarIds(prev => prev.filter(x => x !== id));
      } else {
        await apiAddFavorite(id, token);
        setFavoriteCarIds(prev => [...prev, id]);
      }
    } catch (err) {
      console.error('Ошибка изменения избранного:', err);
    }
  }, [token, favoriteCarIds]);

  return (
    <AuthContext.Provider value={{
      isAuthenticated, token, userEmail, profile, isLoading, generatingChatId, setGeneratingChatId,
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
