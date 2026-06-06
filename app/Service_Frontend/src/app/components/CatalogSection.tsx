// CatalogSection.tsx
import { useEffect, useMemo, useState } from 'react';
import { Filter, X, Heart, ChevronDown, SlidersHorizontal } from 'lucide-react';
import { Link, useSearchParams } from 'react-router';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';
import { CarDto, getCars, CatalogData, searchCars } from '@/app/api/cars';

interface CatalogSectionProps {
  showFilters?: boolean;
  onToggleFavorite: (id: string) => void;
  favoriteIds: string[];
}

const ITEMS_PER_PAGE = 12; // Match backend default limit
const SEARCH_LIMIT = 50;
const SEARCH_DEBOUNCE_MS = 500;

export function CatalogSection({ showFilters = true, onToggleFavorite, favoriteIds }: CatalogSectionProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') ?? '';
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [sortBy, setSortBy] = useState('popular');
  const [searchInput, setSearchInput] = useState(initialSearch);
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [brandFilter, setBrandFilter] = useState('');
  const [modelFilter, setModelFilter] = useState('');
  const [yearFromFilter, setYearFromFilter] = useState('');
  const [yearToFilter, setYearToFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const [cars, setCars] = useState<CarDto[]>([]);
  const [totalCars, setTotalCars] = useState(0);
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
    setCurrentPage(1); // Reset to first page when filters change
  };

  const apiSort = useMemo(() => {
    if (sortBy === 'year-desc') return 'year_desc';
    if (sortBy === 'year-asc') return 'year_asc';
    return undefined;
  }, [sortBy]);

  useEffect(() => {
    const nextSearch = searchParams.get('search') ?? '';
    setSearchInput(nextSearch);
    setSearchQuery(nextSearch);
  }, [searchParams]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      const trimmed = searchInput.trim();
      setSearchQuery(trimmed);

      const nextParams = new URLSearchParams(searchParams);
      if (trimmed) {
        nextParams.set('search', trimmed);
      } else {
        nextParams.delete('search');
      }

      if (nextParams.toString() !== searchParams.toString()) {
        setSearchParams(nextParams, { replace: true });
      }
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeoutId);
  }, [searchInput]);

  // Reset page when sort changes
  useEffect(() => {
    setCurrentPage(1);
  }, [sortBy]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [brandFilter, modelFilter, yearFromFilter, yearToFilter, searchQuery]);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    const isSearching = Boolean(searchQuery);

    const brandQuery = brandFilter.trim();
    const modelQuery = modelFilter.trim();

    const request = isSearching
      ? searchCars({ q: searchQuery, limit: SEARCH_LIMIT })
      : getCars({
          brand: brandQuery || undefined,
          model: modelQuery || undefined,
          sort: apiSort,
          limit: ITEMS_PER_PAGE,
          page: currentPage,
        });

    request
      .then((data: CatalogData) => {
        if (isMounted) {
          setCars(data.founded_cars ?? []);
          setTotalCars(data.cars_count);
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
  }, [apiSort, currentPage, brandFilter, modelFilter, searchQuery]); // Add currentPage as dependency

  // Since we're now paginating on the backend, we can simplify client-side filtering
  // Keep local filters for UI responsiveness, but they'll mainly be used as search criteria
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

    return filtered;
  }, [cars, brandFilter, modelFilter, yearFromFilter, yearToFilter]);

  const isSearchActive = Boolean(searchQuery);
  const hasYearFilter = Boolean(yearFromFilter.trim() || yearToFilter.trim());
  const totalItems = isSearchActive || hasYearFilter ? filteredCars.length : totalCars;

  // Calculate pagination
  const totalPages = Math.max(
    1,
    Math.ceil(totalItems / ITEMS_PER_PAGE)
  );

  const pagedCars = useMemo(() => {
    if (!isSearchActive) {
      return filteredCars;
    }
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredCars.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredCars, currentPage, isSearchActive]);
  
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 5; // Maximum visible page numbers
    
    if (totalPages <= maxVisible) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      let startPage = Math.max(2, currentPage - 1);
      let endPage = Math.min(totalPages - 1, currentPage + 1);
      
      // Adjust if near the beginning
      if (currentPage <= 3) {
        endPage = Math.min(4, totalPages - 1);
      }
      
      // Adjust if near the end
      if (currentPage >= totalPages - 2) {
        startPage = Math.max(totalPages - 3, 2);
      }
      
      // Add ellipsis before middle pages if needed
      if (startPage > 2) {
        pages.push('...');
      }
      
      // Add middle pages
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      // Add ellipsis after middle pages if needed
      if (endPage < totalPages - 1) {
        pages.push('...');
      }
      
      // Always show last page
      pages.push(totalPages);
    }
    
    return pages;
  };

  const handleSearchInputChange = (value: string) => {
    setSearchInput(value);
  };

  return (
    <section className="py-8 px-4 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl mb-2">Каталог автомобилей</h2>
            <p className="text-gray-600">Найдено {totalItems} автомобилей</p>
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
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6 bg-white rounded-lg p-4 shadow-sm">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => handleSearchInputChange(e.target.value)}
                placeholder="Поиск по названию"
                className="w-full sm:max-w-sm px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
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
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {pagedCars.map((car) => (
                    <div
                      key={car.brand_model_id}
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
                          onClick={() => onToggleFavorite(car.brand_model_id)}
                        >
                          <Heart className={`w-5 h-5 ${favoriteIds.includes(car.brand_model_id) ? 'text-red-500' : 'text-gray-600'}`} />
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
                          to={`/catalog/${car.brand_model_id}`}
                          className="w-full py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center block"
                        >
                          Подробнее
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center space-x-2 mt-8">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Назад
                    </button>
                    
                    {getPageNumbers().map((page, index) => (
                      typeof page === 'number' ? (
                        <button
                          key={index}
                          onClick={() => handlePageChange(page)}
                          className={`px-4 py-2 rounded-lg transition-colors ${
                            currentPage === page
                              ? 'bg-blue-600 text-white'
                              : 'border border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      ) : (
                        <span key={index} className="px-2 py-2 text-gray-500">
                          {page}
                        </span>
                      )
                    ))}
                    
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Вперед
                    </button>
                  </div>
                )}

                {/* Show current page info */}
                <div className="text-center mt-4 text-sm text-gray-500">
                  Страница {currentPage} из {totalPages}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
