import { Search, User, Menu } from 'lucide-react';

interface HeaderProps {
  onCatalogClick: () => void;
  onProfileClick: () => void;
}

export function Header({ onCatalogClick, onProfileClick }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl text-blue-600 cursor-pointer">AutoSelect</h1>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-gray-700 hover:text-blue-600 transition-colors">
              Главная
            </a>
            <button
              onClick={onCatalogClick}
              className="text-gray-700 hover:text-blue-600 transition-colors"
            >
              Каталог
            </button>
            <a href="#" className="text-gray-700 hover:text-blue-600 transition-colors">
              О нас
            </a>
            <a href="#" className="text-gray-700 hover:text-blue-600 transition-colors">
              Контакты
            </a>
          </nav>

          {/* Search and Profile */}
          <div className="flex items-center space-x-4">
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <Search className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={onProfileClick}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <User className="w-5 h-5 text-gray-600" />
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