import { Phone, Mail, MapPin, Facebook, Instagram, Twitter } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Company Info */}
          <div>
            <h3 className="text-xl mb-4 text-blue-400">AutoSelect</h3>
            <p className="text-gray-400 mb-4">
              Профессиональный сервис по подбору автомобилей с использованием AI-технологий
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="mb-4">Быстрые ссылки</h4>
            <ul className="space-y-2 text-gray-400">
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  О компании
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Каталог авто
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Услуги
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Отзывы
                </a>
              </li>
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="mb-4">Контакты</h4>
            <ul className="space-y-3 text-gray-400">
              <li className="flex items-center space-x-3">
                <Phone className="w-5 h-5 text-blue-400" />
                <span>+7 (495) 123-45-67</span>
              </li>
              <li className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-blue-400" />
                <span>info@autoselect.ru</span>
              </li>
              <li className="flex items-center space-x-3">
                <MapPin className="w-5 h-5 text-blue-400" />
                <span>Москва, ул. Примерная, 123</span>
              </li>
            </ul>
          </div>

          {/* Working Hours */}
          <div>
            <h4 className="mb-4">Режим работы</h4>
            <ul className="space-y-2 text-gray-400">
              <li>Пн-Пт: 9:00 - 20:00</li>
              <li>Сб: 10:00 - 18:00</li>
              <li>Вс: Выходной</li>
            </ul>
            <div className="flex space-x-4 mt-6">
              <a
                href="#"
                className="p-2 bg-gray-800 rounded-full hover:bg-blue-600 transition-colors"
              >
                <Facebook className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="p-2 bg-gray-800 rounded-full hover:bg-blue-600 transition-colors"
              >
                <Instagram className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="p-2 bg-gray-800 rounded-full hover:bg-blue-600 transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
          <p>&copy; 2026 AutoSelect. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
}
