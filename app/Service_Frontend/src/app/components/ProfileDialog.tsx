// src/app/components/ProfileDialog.tsx
import { X, Heart, Mail, Calendar, MapPin, Settings, LogOut, Users, User } from 'lucide-react';
import { useNavigate } from 'react-router';
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

interface ProfileDialogProps {
  isOpen: boolean;
  onClose: () => void;
  favoriteCarIds: number[];
  onRemoveFavorite: (id: number) => void;
}

export function ProfileDialog({ isOpen, onClose, favoriteCarIds, onRemoveFavorite }: ProfileDialogProps) {
  const { profile, userEmail, logout } = useAuth();
  const navigate = useNavigate();

  if (!isOpen) return null;

  const favoriteCars = ALL_CARS.filter(car => favoriteCarIds.includes(car.id));

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };

  const handleLogout = () => {
    logout();
    onClose();
    navigate('/');
  };

  const handleEditProfile = () => {
    onClose();
    navigate('/profile-setup');
  };

  const getInitials = (firstName?: string, lastName?: string) => {
    const f = firstName?.[0] ?? '';
    const l = lastName?.[0] ?? '';
    return (f + l).toUpperCase() || '?';
  };

  const displayName = profile
    ? `${profile.firstName} ${profile.lastName}`
    : userEmail ?? 'Пользователь';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 animate-in fade-in duration-200">
      <div className="bg-card rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden border border-border">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="flex items-center space-x-4">
            {/* Аватар: используем наши новые константные утилиты bg-light-neutral и text-dark-neutral */}
            <div className="w-16 h-16 bg-light-neutral rounded-2xl flex items-center justify-center text-2xl font-semibold text-dark-neutral shadow-sm shrink-0">
              {profile ? getInitials(profile.firstName, profile.lastName) : <User className="w-8 h-8 text-dark-neutral" />}
            </div>
            
            <div className="text-white">
              <h2 className="text-2xl mb-1 text-white">{displayName}</h2>
              <p className="text-blue-100 text-sm">{userEmail}</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto bg-card">
          {/* Personal Info */}
          <div className="p-6 border-b border-border">
            <h3 className="text-xl mb-4 flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-600" />
              <span className="text-card-foreground font-semibold">Личная информация</span>
            </h3>
            
            {profile ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-3 p-3 bg-muted rounded-lg">
                  <Mail className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Email</p>
                    <p className="text-card-foreground font-medium">{userEmail}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-muted rounded-lg">
                  <MapPin className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Город</p>
                    <p className="text-card-foreground font-medium">{profile.city}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-muted rounded-lg">
                  <Calendar className="w-5 h-5 text-orange-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Возраст</p>
                    <p className="text-card-foreground font-medium">{profile.age} лет</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-muted rounded-lg">
                  <Users className="w-5 h-5 text-purple-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Дети</p>
                    <p className="text-card-foreground font-medium">
                      {profile.childrenCount === 0 ? 'Нет детей' : `${profile.childrenCount} детей`}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-yellow-50 border border-yellow-100 rounded-xl p-4 text-sm text-yellow-800">
                Профиль еще не заполнил. Заполните данные для получения рекомендаций.
              </div>
            )}

            {/* Кнопка: теперь отлично красится в text-card-foreground на любом фоне благодаря color: inherit */}
            <button 
              onClick={handleEditProfile}
              className="mt-4 px-4 py-2 border border-border text-card-foreground hover:bg-muted rounded-lg transition-colors text-sm font-medium"
            >
              Редактировать профиль
            </button>
          </div>

          {/* Favorite Cars */}
          <div className="p-6">
            <h3 className="text-xl mb-4 flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <Heart className="w-5 h-5 text-red-500" />
                <span className="text-card-foreground font-semibold">Избранные автомобили</span>
              </span>
              <span className="text-sm text-muted-foreground">({favoriteCars.length})</span>
            </h3>

            {favoriteCars.length === 0 ? (
              <div className="text-center py-12">
                <Heart className="w-16 h-16 text-muted-foreground/40 mx-auto mb-4" />
                <p className="text-muted-foreground text-lg mb-2">Нет избранных автомобилей</p>
                <p className="text-muted-foreground/60 text-sm">
                  Добавьте автомобили в избранное, нажав на иконку сердца
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {favoriteCars.map((car) => (
                  <div
                    key={car.id}
                    className="bg-card border border-border rounded-xl overflow-hidden hover:shadow-lg transition-shadow group"
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
                      <h4 className="mb-1 text-card-foreground font-semibold">{car.name}</h4>
                      <p className="text-lg text-blue-600 mb-2 font-medium">{formatPrice(car.price)}</p>
                      <p className="text-sm text-muted-foreground">Год: {car.year}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="p-6 border-t border-border bg-muted/30">
            <div className="flex flex-col sm:flex-row gap-3">
              <button 
                onClick={handleEditProfile}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-card border border-border rounded-lg hover:bg-muted transition-colors text-sm text-card-foreground"
              >
                <Settings className="w-5 h-5 text-muted-foreground" />
                <span>Настройки профиля</span>
              </button>
              <button 
                onClick={handleLogout}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-card border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm"
              >
                <LogOut className="w-5 h-5" />
                <span>Выйти из аккаунта</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}