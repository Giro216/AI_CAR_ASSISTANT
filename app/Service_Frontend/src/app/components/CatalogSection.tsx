import { useState } from 'react';
import { Filter, X, Heart, ChevronDown, SlidersHorizontal } from 'lucide-react';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';

const catalogCars = [
  {
    id: 1,
    name: 'BMW 5 Series',
    price: 5200000,
    year: 2024,
    mileage: 0,
    engine: '2.0 л, 249 л.с.',
    transmission: 'Автомат',
    fuel: 'Бензин',
    bodyType: 'Седан',
    image: 'https://images.unsplash.com/photo-1707483413416-ca279c8b7a02?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBjYXIlMjBmcm9udHxlbnwxfHx8fDE3Njg1MDQ0MDV8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 2,
    name: 'Porsche 911',
    price: 9800000,
    year: 2024,
    mileage: 0,
    engine: '3.0 л, 385 л.с.',
    transmission: 'Автомат',
    fuel: 'Бензин',
    bodyType: 'Купе',
    image: 'https://images.unsplash.com/photo-1696581081901-f8e0f10713b2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzcG9ydHMlMjBjYXIlMjByZWR8ZW58MXx8fHwxNzY4NTQ4MzgxfDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 3,
    name: 'Mercedes-Benz GLE',
    price: 7500000,
    year: 2024,
    mileage: 0,
    engine: '2.0 л, 258 л.с.',
    transmission: 'Автомат',
    fuel: 'Бензин',
    bodyType: 'Внедорожник',
    image: 'https://images.unsplash.com/photo-1758411898280-2dc7c95e0ba7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdXYlMjBtb2Rlcm4lMjBjYXIlMjB3aGl0ZXxlbnwxfHx8fDE3Njg1NjU0NDdfDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 4,
    name: 'Audi A6',
    price: 4800000,
    year: 2023,
    mileage: 15000,
    engine: '2.0 л, 245 л.с.',
    transmission: 'Автомат',
    fuel: 'Бензин',
    bodyType: 'Седан',
    image: 'https://images.unsplash.com/photo-1757782630151-8012288407e1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZWRhbiUyMGNhciUyMHNpbHZlcnxlbnwxfHx8fDE3Njg1NjU3NDJ8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 5,
    name: 'Volkswagen Golf',
    price: 2500000,
    year: 2023,
    mileage: 20000,
    engine: '1.5 л, 150 л.с.',
    transmission: 'Механика',
    fuel: 'Бензин',
    bodyType: 'Хэтчбек',
    image: 'https://images.unsplash.com/photo-1729783458306-3615ee09ecd6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoYXRjaGJhY2slMjBjYXIlMjB3aGl0ZXxlbnwxfHx8fDE3Njg1NjU3NDJ8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 6,
    name: 'Tesla Model 3',
    price: 5500000,
    year: 2024,
    mileage: 5000,
    engine: 'Электро, 283 л.с.',
    transmission: 'Автомат',
    fuel: 'Электро',
    bodyType: 'Седан',
    image: 'https://images.unsplash.com/photo-1714557632393-64ed972394ed?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxlbGVjdHJpYyUyMGNhciUyMG1vZGVybnxlbnwxfHx8fDE3Njg1MTEyNTV8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
];

interface CatalogSectionProps {
  showFilters?: boolean;
  onToggleFavorite: (id: number) => void;
  favoriteIds: number[];
}

export function CatalogSection({ showFilters = true, onToggleFavorite, favoriteIds }: CatalogSectionProps) {
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [selectedBodyTypes, setSelectedBodyTypes] = useState<string[]>([]);
  const [selectedFuel, setSelectedFuel] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('popular');

  const bodyTypes = ['Седан', 'Внедорожник', 'Хэтчбек', 'Купе', 'Универсал'];
  const fuelTypes = ['Бензин', 'Дизель', 'Электро', 'Гибрид'];

  const toggleBodyType = (type: string) => {
    setSelectedBodyTypes(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const toggleFuelType = (type: string) => {
    setSelectedFuel(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };

  return (
    <section className="py-8 px-4 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl mb-2">Каталог автомобилей</h2>
            <p className="text-gray-600">Найдено {catalogCars.length} автомобилей</p>
          </div>
          
          {showFilters && (
            <button
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors lg:hidden"
            >
              <SlidersHorizontal className="w-5 h-5" />
              <span>Фильтры</span>
            </button>
          )}
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Sidebar */}
          {showFilters && (
            <div
              className={`${
                isFilterOpen ? 'block' : 'hidden'
              } lg:block lg:w-80 bg-white rounded-xl shadow-md p-6 h-fit sticky top-20`}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl flex items-center space-x-2">
                  <Filter className="w-5 h-5" />
                  <span>Фильтры</span>
                </h3>
                <button
                  onClick={() => setIsFilterOpen(false)}
                  className="lg:hidden p-1 hover:bg-gray-100 rounded"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Price Range */}
              <div className="mb-6 pb-6 border-b border-gray-200">
                <h4 className="mb-3">Цена</h4>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    placeholder="От"
                    value={priceRange.min}
                    onChange={(e) => setPriceRange({ ...priceRange, min: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-gray-500">—</span>
                  <input
                    type="text"
                    placeholder="До"
                    value={priceRange.max}
                    onChange={(e) => setPriceRange({ ...priceRange, max: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Body Type */}
              <div className="mb-6 pb-6 border-b border-gray-200">
                <h4 className="mb-3">Тип кузова</h4>
                <div className="space-y-2">
                  {bodyTypes.map((type) => (
                    <label key={type} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedBodyTypes.includes(type)}
                        onChange={() => toggleBodyType(type)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">{type}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Fuel Type */}
              <div className="mb-6 pb-6 border-b border-gray-200">
                <h4 className="mb-3">Тип топлива</h4>
                <div className="space-y-2">
                  {fuelTypes.map((type) => (
                    <label key={type} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedFuel.includes(type)}
                        onChange={() => toggleFuelType(type)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">{type}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Transmission */}
              <div className="mb-6">
                <h4 className="mb-3">Коробка передач</h4>
                <div className="space-y-2">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-gray-700">Автомат</span>
                  </label>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-gray-700">Механика</span>
                  </label>
                </div>
              </div>

              <button className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Применить фильтры
              </button>
            </div>
          )}

          {/* Cars Grid */}
          <div className="flex-1">
            {/* Sort */}
            <div className="flex items-center justify-between mb-6 bg-white rounded-lg p-4 shadow-sm">
              <span className="text-gray-600">Сортировка:</span>
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                >
                  <option value="popular">По популярности</option>
                  <option value="price-asc">Цена: по возрастанию</option>
                  <option value="price-desc">Цена: по убыванию</option>
                  <option value="year-desc">Год: новые</option>
                  <option value="year-asc">Год: старые</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {/* Cars Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {catalogCars.map((car) => (
                <div
                  key={car.id}
                  className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow group cursor-pointer"
                >
                  <div className="relative h-56 overflow-hidden">
                    <ImageWithFallback
                      src={car.image}
                      alt={car.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <button className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors" onClick={() => onToggleFavorite(car.id)}>
                      <Heart className={`w-5 h-5 ${favoriteIds.includes(car.id) ? 'text-red-500' : 'text-gray-600'}`} />
                    </button>
                    {car.mileage === 0 && (
                      <div className="absolute top-4 left-4 px-3 py-1 bg-green-500 text-white text-sm rounded-full">
                        Новый
                      </div>
                    )}
                  </div>

                  <div className="p-5">
                    <h3 className="text-xl mb-1">{car.name}</h3>
                    <p className="text-2xl text-blue-600 mb-4">{formatPrice(car.price)}</p>

                    <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mb-4">
                      <div className="flex flex-col">
                        <span className="text-gray-400">Год</span>
                        <span>{car.year}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-gray-400">Пробег</span>
                        <span>{car.mileage === 0 ? 'Новый' : `${car.mileage.toLocaleString()} км`}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-gray-400">Двигатель</span>
                        <span className="text-xs">{car.engine}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-gray-400">Коробка</span>
                        <span>{car.transmission}</span>
                      </div>
                    </div>

                    <button className="w-full py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Подробнее
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-center space-x-2 mt-8">
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Назад
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg">1</button>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                2
              </button>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                3
              </button>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Вперед
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}