import { useState, useEffect, useRef } from 'react';
import { X, Mail, Lock, Loader2 } from 'lucide-react';
import { useNavigate, Link } from 'react-router';
import { useAuth } from '@/app/contexts/AuthContext';

interface LoginPopupProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LoginPopup({ isOpen, onClose }: LoginPopupProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const popupRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) {
      setEmail('');
      setPassword('');
      setError('');
    }
  }, [isOpen]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (popupRef.current && !popupRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Заполните все поля');
      return;
    }
    setError('');
    try {
      const { hasProfile } = await login(email, password);
      onClose();
      navigate(hasProfile ? '/profile' : '/profile-setup');
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div
      ref={popupRef}
      className="fixed top-[4.5rem] right-4 z-[60] w-80 bg-white rounded-2xl shadow-2xl border border-gray-100"
      style={{ animation: 'slideDown 0.18s ease-out' }}
    >
      <style>{`
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Header */}
      <div className="flex items-center justify-between px-5 pt-5 pb-3">
        <h3 className="text-lg text-gray-900">Вход в аккаунт</h3>
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      <form onSubmit={handleLogin} className="px-5 pb-5 space-y-3">
        {/* Email */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="example@mail.ru"
              className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Password */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">Пароль</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {error && (
          <p className="text-red-500 text-sm bg-red-50 px-3 py-2 rounded-lg">{error}</p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-60 transition-colors flex items-center justify-center gap-2 text-sm"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          Войти
        </button>

        <div className="border-t border-gray-100 pt-3 text-center">
          <p className="text-sm text-gray-500">
            Нет аккаунта?{' '}
            <Link
              to="/register"
              onClick={onClose}
              className="text-blue-600 hover:text-blue-700 transition-colors"
            >
              Зарегистрироваться
            </Link>
          </p>
        </div>
      </form>
    </div>
  );
}
