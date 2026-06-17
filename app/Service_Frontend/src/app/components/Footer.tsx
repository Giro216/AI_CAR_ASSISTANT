import { Mail, MapPin, Github } from 'lucide-react';

export function Footer() {
  return (
    <footer id="footer" className="bg-[#030213] text-white pt-16 pb-12 border-t border-gray-800 scroll-mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          
          {/* Company Info */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-white">AutoSelect</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Профессиональный сервис по подбору автомобилей с использованием современных ИИ-технологий и глубокого анализа характеристик.
            </p>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="text-lg font-semibold mb-6 text-white tracking-wide">Контакты</h4>
            <ul className="space-y-4 text-gray-400 text-sm">
              <li className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-blue-400 shrink-0" />
                <span className="hover:text-white transition-colors">info@autoselect.ru</span>
              </li>
              <li className="flex items-center space-x-3">
                <MapPin className="w-5 h-5 text-blue-400 shrink-0" />
                <span>Новосибирск, ул. Кирова 41</span>
              </li>
            </ul>
          </div>

          {/* GitHub Placeholder */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white tracking-wide">Разработчик</h4>
            <p className="text-gray-400 text-sm leading-relaxed">
              Исходный код проекта и скрипты анализа данных доступны в репозитории на GitHub.
            </p>
            <div className="pt-2">
              <a
                href="https://github.com/Giro216/AI_CAR_ASSISTANT"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 px-5 py-3 bg-gray-800 hover:bg-blue-600 rounded-xl transition-colors text-sm text-white font-medium"
              >
                <Github className="w-5 h-5" />
                <span>GitHub Repository</span>
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-500 text-sm">
          <p>&copy; {new Date().getFullYear()} AutoSelect. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
}
