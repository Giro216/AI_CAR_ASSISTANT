import { useState } from 'react';
import { useNavigate } from 'react-router';
import { User, MapPin, Calendar, Users, Loader2, Sparkles } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';

export function ProfileSetupPage() {
  const { saveProfile, isLoading, userEmail, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (!isAuthenticated) {
    navigate('/');
    return null;
  }

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [city, setCity] = useState('');
  const [age, setAge] = useState('');
  const [childrenCount, setChildrenCount] = useState('0');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!firstName.trim() || !lastName.trim()) {
      setError('Заполните обязательные поля (Имя и Фамилия)');
      return;
    }

    let ageNum: number | null = null;
    if (age.trim()) {
      const parsed = parseInt(age, 10);
      if (isNaN(parsed) || parsed < 18 || parsed > 100) {
        setError('Укажите корректный возраст (18–100) или оставьте поле пустым');
        return;
      }
      ageNum = parsed;
    }

    try {
      await saveProfile({
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        city: city.trim() || null,
        age: ageNum,
        childrenCount: childrenCount ? parseInt(childrenCount, 10) : 0,
      });
      navigate('/profile');
    } catch (err: any) {
      setError(err.message || 'Ошибка сохранения');
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        {/* Welcome header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl text-gray-900 mb-2">Добро пожаловать!</h1>
          <p className="text-gray-500 max-w-sm mx-auto">
            Расскажите о себе — это поможет нам подобрать автомобиль именно для вас
          </p>
          {userEmail && (
            <span className="inline-block mt-2 text-sm text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
              {userEmail}
            </span>
          )}
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* First name */}
              <div>
                <label className="block text-sm text-gray-700 mb-1.5">
                  Имя <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={firstName}
                    onChange={e => setFirstName(e.target.value)}
                    placeholder="Иван"
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Last name */}
              <div>
                <label className="block text-sm text-gray-700 mb-1.5">
                  Фамилия <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={lastName}
                    onChange={e => setLastName(e.target.value)}
                    placeholder="Петров"
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* City */}
            <div>
              <label className="block text-sm text-gray-700 mb-1.5">Город</label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={city}
                  onChange={e => setCity(e.target.value)}
                  placeholder="Москва"
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Age */}
              <div>
                <label className="block text-sm text-gray-700 mb-1.5">Возраст</label>
                <div className="relative">
                  <Calendar className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="number"
                    min={18}
                    max={100}
                    value={age}
                    onChange={e => setAge(e.target.value)}
                    placeholder="35"
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Children */}
              <div>
                <label className="block text-sm text-gray-700 mb-1.5">
                  Количество детей
                </label>
                <div className="relative">
                  <Users className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <select
                    value={childrenCount}
                    onChange={e => setChildrenCount(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
                  >
                    {[0, 1, 2, 3, 4, 5].map(n => (
                      <option key={n} value={n}>{n === 0 ? 'Нет детей' : `${n} ${n === 1 ? 'ребёнок' : n < 5 ? 'ребёнка' : 'детей'}`}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm bg-red-50 border border-red-100 px-4 py-3 rounded-xl">
                {error}
              </div>
            )}

            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-60 transition-all flex items-center justify-center gap-2"
              >
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                Сохранить и перейти в профиль
              </button>
            </div>
          </form>

          <p className="mt-4 text-center text-xs text-gray-400">
            Поля со звёздочкой обязательны для заполнения
          </p>
        </div>
      </div>
    </div>
  );
}
