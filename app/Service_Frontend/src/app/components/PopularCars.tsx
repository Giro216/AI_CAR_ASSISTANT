import { useEffect, useMemo, useState } from 'react';
import { Heart, ArrowRight } from 'lucide-react';
import { Link } from 'react-router';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';
import { getPopularCars, CarDto } from '@/app/api/cars';

interface PopularCarsProps {
  onToggleFavorite: (id: string) => void;
  favoriteIds: string[];
}

export function PopularCars({ onToggleFavorite, favoriteIds }: PopularCarsProps) {
  const [cars, setCars] = useState<CarDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    getPopularCars()
      .then((data) => {
        if (isMounted) {
          setCars(data ?? []);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Не удалось загрузить популярные автомобили');
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
  }, []);

  const placeholderImage =
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1080&q=80';

  const formatYear = (car: CarDto) => {
    if (car.start_year && car.end_year && car.start_year !== car.end_year) {
      return `${car.start_year}–${car.end_year}`;
    }
    return car.start_year ?? car.end_year ?? '—';
  };

  const cards = useMemo(() => cars.slice(0, 6), [cars]);

  return (
    <section className="py-16 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h2 className="text-3xl mb-2">Популярные автомобили</h2>
            <p className="text-gray-600">Самые востребованные модели этого месяца</p>
          </div>
          <Link
            to="/catalog"
            className="hidden md:flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors"
          >
            <span>Смотреть все</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {isLoading ? (
          <div className="text-gray-500">Загрузка популярных автомобилей…</div>
        ) : error ? (
          <div className="text-red-600">{error}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cards.map((car) => (
              <div
                key={car.id}
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow group"
              >
                <div className="relative h-56 overflow-hidden">
                  <ImageWithFallback
                    src={car.imageUrl ?? placeholderImage}
                    alt={`${car.brand ?? ''} ${car.model ?? ''}`.trim() || 'Автомобиль'}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <button
                    onClick={() => onToggleFavorite(car.id)}
                    className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                  >
                    <Heart
                      className={`w-5 h-5 ${
                        favoriteIds.includes(car.id)
                          ? 'text-red-500 fill-red-500'
                          : 'text-gray-600'
                      }`}
                    />
                  </button>
                </div>

                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-xl">
                      {car.brand ?? '—'} {car.model ?? ''}
                    </h3>
                  </div>

                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <div className="flex items-center justify-between">
                      <span>Год:</span>
                      <span>{formatYear(car)}</span>
                    </div>
                  </div>

                  <Link
                    to={`/catalog/${car.id}`}
                    className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center block"
                  >
                    Подробнее
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        <Link
          to="/catalog"
          className="md:hidden flex items-center justify-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors mx-auto mt-8"
        >
          <span>Смотреть все</span>
          <ArrowRight className="w-5 h-5" />
        </Link>
      </div>
    </section>
  );
}
