import { useEffect, useMemo, useState } from 'react';
import { Filter, X, Heart, ChevronDown, SlidersHorizontal } from 'lucide-react';
import { Link } from 'react-router';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';
import { CarDto, getCars } from '@/app/api/cars';

interface CatalogSectionProps {
  showFilters?: boolean;
  onToggleFavorite: (id: string) => void;
  favoriteIds: string[];
}

export function CatalogSection({ showFilters = true, onToggleFavorite, favoriteIds }: CatalogSectionProps) {
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [sortBy, setSortBy] = useState('popular');
  const [brandFilter, setBrandFilter] = useState('');
  const [modelFilter, setModelFilter] = useState('');
  const [yearFromFilter, setYearFromFilter] = useState('');
  const [yearToFilter, setYearToFilter] = useState('');

  const [cars, setCars] = useState<CarDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const formatYear = (car: CarDto) => {
    if (car.start_year && car.end_year && car.start_year !== car.end_year) {
      return `${car.start_year}–${car.end_year}`;
    }
    return car.start_year ?? car.end_year ?? '—';
  };

  const placeholderImage =
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1080&q=80';

  const resetFilters = () => {
    setBrandFilter('');
    setModelFilter('');
    setYearFromFilter('');
    setYearToFilter('');
  };

  const apiSort = useMemo(() => {
    if (sortBy === 'year-desc') return 'year_desc';
    if (sortBy === 'year-asc') return 'year_asc';
    return undefined;
  }, [sortBy]);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    getCars({ sort: apiSort })
      .then((data) => {
        if (isMounted) {
          setCars(data ?? []);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Не удалось загрузить каталог');
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [apiSort]);

  const filteredCars = useMemo(() => {
    const yearFrom = Number(yearFromFilter) || null;
    const yearTo = Number(yearToFilter) || null;

    const filtered = cars.filter((car) => {
      const carBrand = (car.brand ?? '').toLowerCase();
      const carModel = (car.model ?? '').toLowerCase();

      if (brandFilter.trim() && !carBrand.includes(brandFilter.trim().toLowerCase())) {
        return false;
      }

      if (modelFilter.trim() && !carModel.includes(modelFilter.trim().toLowerCase())) {
        return false;
      }

      const carStartYear = car.start_year ?? car.end_year ?? null;
      const carEndYear = car.end_year ?? car.start_year ?? null;

      if (yearFrom !== null && carEndYear !== null && carEndYear < yearFrom) {
        return false;
      }

      if (yearTo !== null && carStartYear !== null && carStartYear > yearTo) {
        return false;
      }

      return true;
    });

    if (sortBy === 'year-desc') {
      return [...filtered].sort((a, b) => (b.start_year ?? b.end_year ?? 0) - (a.start_year ?? a.end_year ?? 0));
    }

    if (sortBy === 'year-asc') {
      return [...filtered].sort((a, b) => (a.start_year ?? a.end_year ?? 0) - (b.start_year ?? b.end_year ?? 0));
    }

    return filtered;
  }, [cars, brandFilter, modelFilter, yearFromFilter, yearToFilter, sortBy]);

  return (
    <section className="py-8 px-4 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl mb-2">Каталог автомобилей</h2>
            <p className="text-gray-600">Найдено {filteredCars.length} автомобилей</p>
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

              <div className="space-y-4 mb-6">
                <div>
                  <h4 className="mb-2 text-sm text-gray-600">Бренд</h4>
                  <input
                    type="text"
                    value={brandFilter}
                    onChange={(e) => setBrandFilter(e.target.value)}
                    placeholder="Например, Audi"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <h4 className="mb-2 text-sm text-gray-600">Модель</h4>
                  <input
                    type="text"
                    value={modelFilter}
                    onChange={(e) => setModelFilter(e.target.value)}
                    placeholder="Например, A4"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <h4 className="mb-2 text-sm text-gray-600">Год выпуска</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      value={yearFromFilter}
                      onChange={(e) => setYearFromFilter(e.target.value)}
                      placeholder="От"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      value={yearToFilter}
                      onChange={(e) => setYearToFilter(e.target.value)}
                      placeholder="До"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={resetFilters}
                  className="flex-1 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Сбросить
                </button>
                <button
                  type="button"
                  onClick={() => setIsFilterOpen(false)}
                  className="flex-1 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Применить
                </button>
              </div>
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
                  <option value="year-asc">Год: старые</option>
                  <option value="year-desc">Год: новые</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {isLoading ? (
              <div className="text-gray-500">Загрузка каталога…</div>
            ) : error ? (
              <div className="text-red-600">{error}</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredCars.map((car) => (
                  <div
                    key={car.id}
                    className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow group cursor-pointer"
                  >
                    <div className="relative h-56 overflow-hidden">
                      <ImageWithFallback
                        src={car.imageUrl ?? placeholderImage}
                        alt={`${car.brand ?? ''} ${car.model ?? ''}`.trim() || 'Автомобиль'}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <button
                        className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                        onClick={() => onToggleFavorite(car.id)}
                      >
                        <Heart className={`w-5 h-5 ${favoriteIds.includes(car.id) ? 'text-red-500' : 'text-gray-600'}`} />
                      </button>
                    </div>

                    <div className="p-5">
                      <h3 className="text-xl mb-1">{car.brand ?? '—'} {car.model ?? ''}</h3>
                      <div className="grid grid-cols-1 gap-2 text-sm text-gray-600 mb-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Год</span>
                          <span>{formatYear(car)}</span>
                        </div>
                      </div>

                      <Link
                        to={`/catalog/${car.id}`}
                        className="w-full py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center block"
                      >
                        Подробнее
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}

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
