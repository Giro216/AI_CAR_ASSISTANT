import { useOutletContext } from 'react-router';
import { AIChatSection } from '@/app/components/AIChatSection';
import { PopularCars } from '@/app/components/PopularCars';
import { Sparkles, Shield, Zap, Check } from 'lucide-react';

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
  setIsChatDialogOpen: (open: boolean) => void;
}

export function HomePage() {
  const { favoriteCarIds, handleToggleFavorite } = useOutletContext<OutletContext>();

  return (
    <div className="space-y-0">
      <AIChatSection />
      
      <div className="bg-gray-50 border-t border-b border-gray-100">
        <PopularCars
          onToggleFavorite={handleToggleFavorite}
          favoriteIds={favoriteCarIds}
        />
      </div>

      {/* Блок 3: О компании / О нас (Белый фон для контраста) */}
      <section id="about-us" className="py-16 px-4 bg-gradient-to-br scroll-mt-16">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <h2 className="text-3xl text-gray-900 font-bold tracking-tight">О проекте AutoSelect</h2>
          <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed text-base">
            AutoSelect — это инновационный веб-сервис интеллектуального подбора автомобилей на базе искусственного интеллекта. Наша система избавляет вас от необходимости изучать сотни технических таблиц, спецификаций и отзывов.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 text-left">
            <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100 space-y-3">
              <Sparkles className="w-6 h-6 text-blue-600" />
              <h4 className="font-semibold text-gray-900 text-lg">ИИ-Автоподбор</h4>
              <p className="text-gray-500 text-sm leading-relaxed">
                Просто опишите свои пожелания, бюджет или состав семьи на человеческом языке в свободной форме.
              </p>
            </div>
            <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100 space-y-3">
              <Shield className="w-6 h-6 text-green-600" />
              <h4 className="font-semibold text-gray-900 text-lg">Валидация по каталогу</h4>
              <p className="text-gray-500 text-sm leading-relaxed">
                Модель рекомендует только те машины, наличие которых подтверждено в нашей локальной базе данных.
              </p>
            </div>
            <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100 space-y-3">
              <Zap className="w-6 h-6 text-orange-600" />
              <h4 className="font-semibold text-gray-900 text-lg">Сверка цен</h4>
              <p className="text-gray-500 text-sm leading-relaxed">
                Ассистент мгновенно сверяет реальные цены на авторынке РФ, чтобы гарантированно уложиться в ваш бюджет.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Блок 4: Тарифные планы (Светло-серый фон) */}
      <section id="tariffs" className="py-16 px-4 bg-white border-t border-gray-100 scroll-mt-16">
        <div className="max-w-5xl mx-auto space-y-10">
          <div className="text-center">
            <h3 className="text-3xl text-gray-900 font-bold tracking-tight">Наши тарифные лимиты</h3>
            <p className="text-gray-500 text-sm mt-2">Выберите подходящий формат взаимодействия с ИИ-помощником</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Тариф Гость */}
            <div className="border border-gray-200 rounded-2xl p-6 bg-white flex flex-col justify-between shadow-sm">
              <div>
                <h4 className="text-xl text-gray-900 font-semibold mb-2">Гостевой режим</h4>
                <p className="text-gray-500 text-sm mb-4">Для быстрого ознакомления без регистрации</p>
                <div className="text-2xl font-bold text-gray-900 mb-6">Бесплатно</div>
                
                <ul className="space-y-3 text-sm text-gray-600 mb-8">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span>Максимум 3 диалога</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span>До 12 сообщений в одном чате</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span>Лаконичные быстрые ответы ИИ</span>
                  </li>
                  <li className="flex items-center gap-2 text-gray-400">
                    <XRed />
                    <span>История стирается при закрытии вкладки</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Тариф Авторизованный */}
            <div className="border-2 border-blue-600 rounded-2xl p-6 bg-white flex flex-col justify-between relative shadow-lg">
              <span className="absolute -top-3 right-6 bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-semibold">Рекомендуем</span>
              <div>
                <h4 className="text-xl text-gray-900 font-semibold mb-2">Авторизованный</h4>
                <p className="text-gray-500 text-sm mb-4">Для полноценного персонализированного подбора</p>
                <div className="text-2xl font-bold text-blue-600 mb-6">За регистрацию</div>
                
                <ul className="space-y-3 text-sm text-gray-600 mb-8">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span className="font-semibold text-gray-800">Безлимитное количество диалогов</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span>До 100 сообщений в одном чате</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span>Подробные, глубокие ответы ИИ</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span>Сохранение истории диалогов навсегда</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function XRed() {
  return (
    <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}