import { useEffect, useRef, useState } from 'react';
import { Search, User, Menu, MessageCircle, UserCheck } from 'lucide-react';
import { Link, useNavigate } from 'react-router';

interface HeaderProps {
  onProfileClick: () => void;
  isAuthenticated: boolean;
}

export function Header({ onProfileClick, isAuthenticated }: HeaderProps) {
  const navigate = useNavigate();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const searchContainerRef = useRef<HTMLDivElement | null>(null);

  const submitSearch = () => {
    const trimmed = searchValue.trim();
    const target = trimmed ? `/catalog?search=${encodeURIComponent(trimmed)}` : '/catalog';
    navigate(target);
  };

  const handleSearchClick = () => {
    if (!isSearchOpen) {
      setIsSearchOpen(true);
      window.setTimeout(() => searchInputRef.current?.focus(), 0);
      return;
    }
    submitSearch();
  };

  useEffect(() => {
    if (!isSearchOpen) {
      return;
    }

    const handleOutsideClick = (event: MouseEvent) => {
      if (!searchContainerRef.current) {
        return;
      }
      if (!searchContainerRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false);
      }
    };

    document.addEventListener('mousedown', handleOutsideClick);
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isSearchOpen]);

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-blue-600 cursor-pointer">AutoSelect</Link>
          </div>

          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
              Главная
            </Link>
            <Link to="/catalog" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
              Каталог
            </Link>
            <Link to="/chat" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
              Чат
            </Link>
            <a href="/#about-us" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
              О нас
            </a>
            <a href="/#footer" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
              Контакты
            </a>
          </nav>

          {/* Search and Profile */}
          <div className="flex items-center space-x-4">
            <div ref={searchContainerRef} className="flex items-center gap-2">
              {isSearchOpen && (
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchValue}
                  onChange={(event) => setSearchValue(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      submitSearch();
                    }
                  }}
                  placeholder="Поиск по названию"
                  className="w-44 sm:w-56 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              )}
              <button
                onClick={handleSearchClick}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                aria-label="Поиск по названию"
              >
                <Search className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            <Link
              to="/chat"
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              aria-label="Открыть чат"
            >
              <MessageCircle className="w-5 h-5 text-gray-600" />
            </Link>
            <button
              onClick={onProfileClick}
              className={`p-2 rounded-full transition-colors relative ${
                isAuthenticated
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'hover:bg-gray-100 text-gray-600'
              }`}
              title={isAuthenticated ? 'Мой профиль' : 'Войти'}
            >
              {isAuthenticated ? (
                <UserCheck className="w-5 h-5" />
              ) : (
                <User className="w-5 h-5" />
              )}
            </button>
            <button className="md:hidden p-2 hover:bg-gray-100 rounded-full transition-colors">
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}