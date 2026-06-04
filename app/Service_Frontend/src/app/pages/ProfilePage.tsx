import { useNavigate, Link } from 'react-router';
import {
  Heart, Mail, MapPin, Calendar, Users, LogOut, Edit2, User, Car, ExternalLink,
} from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';

const ALL_CARS = [
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

function formatPrice(price: number) {
  return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
}

function getInitials(firstName?: string, lastName?: string) {
  const f = firstName?.[0] ?? '';
  const l = lastName?.[0] ?? '';
  return (f + l).toUpperCase() || '?';
}

export function ProfilePage() {
  const { profile, userEmail, favoriteCarIds, toggleFavorite, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (!isAuthenticated) {
    navigate('/');
    return null;
  }

  const favoriteCars = ALL_CARS.filter(c => favoriteCarIds.includes(c.id));

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const displayName = profile
    ? `${profile.firstName} ${profile.lastName}`
    : userEmail ?? 'Пользователь';

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gray-50">
      {/* Hero banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="flex flex-col sm:flex-row items-center sm:items-end gap-6">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shrink-0 border-2 border-white/30">
              {profile ? (
                <span className="text-3xl text-white">
                  {getInitials(profile.firstName, profile.lastName)}
                </span>
              ) : (
                <User className="w-10 h-10 text-white" />
              )}
            </div>

            <div className="text-center sm:text-left flex-1">
              <h1 className="text-3xl mb-1 text-white">{displayName}</h1>
              <p className="text-blue-200 text-sm">{userEmail}</p>
              {profile?.city && (
                <div className="flex items-center justify-center sm:justify-start gap-1.5 mt-2 text-blue-100 text-sm">
                  <MapPin className="w-3.5 h-3.5" />
                  {profile.city}
                </div>
              )}
            </div>

            <div className="flex gap-3">
              <Link
                to="/profile-setup"
                className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl text-sm text-white transition-colors border border-white/30"
              >
                <Edit2 className="w-4 h-4" />
                Редактировать
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-500 bg-opacity-80 hover:bg-opacity-100 rounded-xl text-sm text-white transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Выйти
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Personal info cards */}
        {profile ? (
          <div>
            <h2 className="text-xl text-gray-800 mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-blue-600" />
              Личная информация
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <InfoCard icon={<Mail className="w-5 h-5 text-blue-500" />} label="Email" value={profile.email} />
              <InfoCard icon={<MapPin className="w-5 h-5 text-green-500" />} label="Город" value={profile.city} />
              <InfoCard icon={<Calendar className="w-5 h-5 text-orange-500" />} label="Возраст" value={`${profile.age} лет`} />
              <InfoCard
                icon={<Users className="w-5 h-5 text-purple-500" />}
                label="Дети"
                value={profile.childrenCount === 0 ? 'Нет детей' : `${profile.childrenCount} ${profile.childrenCount === 1 ? 'ребёнок' : profile.childrenCount < 5 ? 'ребёнка' : 'детей'}`}
              />
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6 flex items-start gap-4">
            <div className="w-10 h-10 bg-yellow-100 rounded-xl flex items-center justify-center shrink-0">
              <User className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-yellow-800 mb-2">Профиль не заполнен</p>
              <p className="text-yellow-600 text-sm mb-3">
                Заполните личные данные, чтобы получать персональные рекомендации по автомобилям.
              </p>
              <Link
                to="/profile-setup"
                className="inline-flex items-center gap-1.5 text-sm text-yellow-700 hover:text-yellow-800 transition-colors underline"
              >
                Заполнить профиль
              </Link>
            </div>
          </div>
        )}

        {/* Favorites */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl text-gray-800 flex items-center gap-2">
              <Heart className="w-5 h-5 text-red-500" />
              Избранные автомобили
              <span className="text-sm text-gray-400">({favoriteCars.length})</span>
            </h2>
            {favoriteCars.length > 0 && (
              <Link to="/catalog" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
                Каталог <ExternalLink className="w-3.5 h-3.5" />
              </Link>
            )}
          </div>

          {favoriteCars.length === 0 ? (
            <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
              <Car className="w-16 h-16 text-gray-200 mx-auto mb-4" />
              <p className="text-gray-500 mb-2">Нет избранных автомобилей</p>
              <p className="text-gray-400 text-sm mb-4">
                Добавляйте автомобили в избранное, нажимая на иконку сердца
              </p>
              <Link
                to="/catalog"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-700 transition-colors"
              >
                Перейти в каталог
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {favoriteCars.map(car => (
                <div
                  key={car.id}
                  className="bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow group"
                >
                  <div className="relative h-44 overflow-hidden">
                    <ImageWithFallback
                      src={car.image}
                      alt={car.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <button
                      onClick={() => toggleFavorite(car.id)}
                      className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                    >
                      <Heart className="w-4 h-4 text-red-500 fill-red-500" />
                    </button>
                  </div>
                  <div className="p-4">
                    <h3 className="mb-1 text-gray-900">{car.name}</h3>
                    <p className="text-blue-600 mb-3">{formatPrice(car.price)}</p>
                    <div className="flex gap-2">
                      <Link
                        to={`/catalog/${car.id}`}
                        className="flex-1 py-2 bg-blue-600 text-white text-center text-sm rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Подробнее
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-3 shadow-sm">
      <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center shrink-0">
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs text-gray-400 mb-0.5">{label}</p>
        <p className="text-gray-800 text-sm truncate">{value}</p>
      </div>
    </div>
  );
}
