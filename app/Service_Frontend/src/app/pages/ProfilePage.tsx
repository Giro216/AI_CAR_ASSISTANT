import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router';
import {
  Heart, Mail, MapPin, Calendar, Users, LogOut, Edit2, User, Car, ExternalLink,
} from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { apiGetFavorites, CarDto } from '@/app/api/cars';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';

function formatPrice(price: number) {
  return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
}

function getInitials(firstName?: string, lastName?: string) {
  const f = firstName?.[0] ?? '';
  const l = lastName?.[0] ?? '';
  return (f + l).toUpperCase() || '?';
}

export function ProfilePage() {
  const { profile, userEmail, token, favoriteCarIds, toggleFavorite, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [favoriteCars, setFavoriteCars] = useState<CarDto[]>([]);
  const [isFavoritesLoading, setIsFavoritesLoading] = useState(false);

  if (!isAuthenticated) {
    navigate('/');
    return null;
  }

  useEffect(() => {
    if (token) {
      setIsFavoritesLoading(true);
      apiGetFavorites(token)
        .then(setFavoriteCars)
        .catch(() => setFavoriteCars([]))
        .finally(() => setIsFavoritesLoading(false));
    }
  }, [token, favoriteCarIds]);

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
                className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-opacity-30 rounded-xl text-sm text-white transition-colors border border-white/30"
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
              <InfoCard icon={<MapPin className="w-5 h-5 text-green-500" />} label="Город" value={profile.city ? profile.city : 'Не указан'} />
              <InfoCard icon={<Calendar className="w-5 h-5 text-orange-500" />} label="Возраст" value={`${profile.age ? `${profile.age} лет` : 'Не указан'}`} />
              <InfoCard
                icon={<Users className="w-5 h-5 text-purple-500" />}
                label="Дети"
                value={
                  profile.childrenCount !== undefined && profile.childrenCount !== null
                    ? profile.childrenCount === 0
                      ? 'Нет детей'
                      : `${profile.childrenCount} ${profile.childrenCount === 1 ? 'ребёнок' : profile.childrenCount < 5 ? 'ребёнка' : 'детей'}`
                    : 'Не указано'
                }
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

          {isFavoritesLoading ? (
            <div className="text-center py-12 text-gray-500">Загрузка избранных авто...</div>
          ) : favoriteCars.length === 0 ? (
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
                  key={car.brand_model_id}
                  className="bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow group"
                >
                  <div className="relative h-44 overflow-hidden">
                    <ImageWithFallback
                      src={car.imageUrl || 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1080&q=80'}
                      alt={`${car.brand} ${car.model}`}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <button
                      onClick={() => toggleFavorite(car.brand_model_id)}
                      className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                    >
                      <Heart className="w-4 h-4 text-red-500 fill-red-500" />
                    </button>
                  </div>
                  <div className="p-4">
                    <h3 className="mb-1 text-gray-900">{car.brand} {car.model}</h3>
                    <div className="flex gap-2">
                      <Link
                        to={`/catalog/${car.brand_model_id}`}
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
