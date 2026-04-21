import { X, Heart, Mail, Phone, Calendar, MapPin, Settings, LogOut } from 'lucide-react';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';

interface ProfileDialogProps {
  isOpen: boolean;
  onClose: () => void;
  favoriteCarIds: number[];
  onRemoveFavorite: (id: number) => void;
}

const allCars = [
  {
    id: 1,
    name: 'BMW 5 Series',
    price: 5200000,
    year: 2024,
    image: 'https://images.unsplash.com/photo-1707483413416-ca279c8b7a02?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBjYXIlMjBmcm9udHxlbnwxfHx8fDE3Njg1MDQ0MDV8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 2,
    name: 'Porsche 911',
    price: 9800000,
    year: 2024,
    image: 'https://images.unsplash.com/photo-1696581081901-f8e0f10713b2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzcG9ydHMlMjBjYXIlMjByZWR8ZW58MXx8fHwxNzY4NTQ4MzgxfDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 3,
    name: 'Mercedes-Benz GLE',
    price: 7500000,
    year: 2024,
    image: 'https://images.unsplash.com/photo-1758411898280-2dc7c95e0ba7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdXYlMjBtb2Rlcm4lMjBjYXJ8ZW58MXx8fHwxNzY4NTY1NDQ3fDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 4,
    name: 'Audi A6',
    price: 4800000,
    year: 2023,
    image: 'https://images.unsplash.com/photo-1757782630151-8012288407e1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZWRhbiUyMGNhciUyMHNpbHZlcnxlbnwxfHx8fDE3Njg1NjU3NDJ8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 5,
    name: 'Volkswagen Golf',
    price: 2500000,
    year: 2023,
    image: 'https://images.unsplash.com/photo-1729783458306-3615ee09ecd6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoYXRjaGJhY2slMjBjYXIlMjB3aGl0ZXxlbnwxfHx8fDE3Njg1NjU3NDJ8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 6,
    name: 'Tesla Model 3',
    price: 5500000,
    year: 2024,
    image: 'https://images.unsplash.com/photo-1714557632393-64ed972394ed?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxlbGVjdHJpYyUyMGNhciUyMG1vZGVybnxlbnwxfHx8fDE3Njg1MTEyNTV8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
];

export function ProfileDialog({ isOpen, onClose, favoriteCarIds, onRemoveFavorite }: ProfileDialogProps) {
  if (!isOpen) return null;

  const favoriteCars = allCars.filter(car => favoriteCarIds.includes(car.id));

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center text-3xl">
              👤
            </div>
            <div className="text-white">
              <h2 className="text-2xl mb-1">Иван Петров</h2>
              <p className="text-blue-100">Клиент с декабря 2023</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {/* Personal Info */}
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-xl mb-4 flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-600" />
              <span>Личная информация</span>
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="text-gray-800">ivan.petrov@example.com</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Phone className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Телефон</p>
                  <p className="text-gray-800">+7 (999) 123-45-67</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Дата рождения</p>
                  <p className="text-gray-800">15 мая 1985</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <MapPin className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">��ород</p>
                  <p className="text-gray-800">Москва</p>
                </div>
              </div>
            </div>

            <button className="mt-4 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
              Редактировать профиль
            </button>
          </div>

          {/* Favorite Cars */}
          <div className="p-6">
            <h3 className="text-xl mb-4 flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <Heart className="w-5 h-5 text-red-500" />
                <span>Избранные автомобили</span>
              </span>
              <span className="text-sm text-gray-500">({favoriteCars.length})</span>
            </h3>

            {favoriteCars.length === 0 ? (
              <div className="text-center py-12">
                <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg mb-2">Нет избранных автомобилей</p>
                <p className="text-gray-400 text-sm">
                  Добавьте автомобили в избранное, нажав на иконку сердца
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {favoriteCars.map((car) => (
                  <div
                    key={car.id}
                    className="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg transition-shadow group"
                  >
                    <div className="relative h-40 overflow-hidden">
                      <ImageWithFallback
                        src={car.image}
                        alt={car.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <button
                        onClick={() => onRemoveFavorite(car.id)}
                        className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                      >
                        <Heart className="w-5 h-5 text-red-500 fill-red-500" />
                      </button>
                    </div>

                    <div className="p-4">
                      <h4 className="mb-1">{car.name}</h4>
                      <p className="text-lg text-blue-600 mb-2">{formatPrice(car.price)}</p>
                      <p className="text-sm text-gray-500 mb-3">Год: {car.year}</p>
                      <button className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                        Подробнее
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="p-6 border-t border-gray-200 bg-gray-50">
            <div className="flex flex-col sm:flex-row gap-3">
              <button className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <Settings className="w-5 h-5 text-gray-600" />
                <span>Настройки</span>
              </button>
              <button className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-white border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                <LogOut className="w-5 h-5" />
                <span>Выйти</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
