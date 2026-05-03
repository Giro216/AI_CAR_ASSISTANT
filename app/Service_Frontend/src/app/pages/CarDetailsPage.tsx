import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useOutletContext } from 'react-router';
import { ArrowLeft, Heart, Calendar, Gauge } from 'lucide-react';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';
import { CarDto, getCars } from '@/app/api/cars';

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
}

export function CarDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { favoriteCarIds, handleToggleFavorite } = useOutletContext<OutletContext>();
  const [car, setCar] = useState<CarDto | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    getCars()
      .then((data) => {
        if (!isMounted) return;
        const found = (data ?? []).find(item => item.id === id) ?? null;
        setCar(found);
      })
      .catch((err) => {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : 'Не удалось загрузить автомобиль');
      })
      .finally(() => {
        if (!isMounted) return;
        setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [id]);

  const placeholderImage =
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1080&q=80';

  const displayName = useMemo(() => {
    if (!car) return '';
    return `${car.brand ?? ''} ${car.model ?? ''}`.trim() || 'Автомобиль';
  }, [car]);

  const displayYear = useMemo(() => {
    if (!car) return '—';
    if (car.start_year && car.end_year && car.start_year !== car.end_year) {
      return `${car.start_year}–${car.end_year}`;
    }
    return car.start_year ?? car.end_year ?? '—';
  }, [car]);

  const isFavorite = car ? favoriteCarIds.includes(car.id) : false;

  if (isLoading) {
    return (
      <div className="py-16 px-4 text-center text-gray-500">Загрузка автомобиля…</div>
    );
  }

  if (error) {
    return (
      <div className="py-16 px-4 text-center text-red-600">{error}</div>
    );
  }

  if (!car) {
    return (
      <div className="py-16 px-4 text-center">
        <h2 className="text-2xl mb-4">Автомобиль не найден</h2>
        <button
          onClick={() => navigate('/catalog')}
          className="text-blue-600 hover:text-blue-700"
        >
          Вернуться к каталогу
        </button>
      </div>
    );
  }

  return (
    <div className="py-8 px-4 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Назад</span>
        </button>

        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="relative">
            <ImageWithFallback
              src={car.imageUrl ?? placeholderImage}
              alt={displayName}
              className="w-full h-96 object-cover"
            />
            <button
              onClick={() => handleToggleFavorite(car.id)}
              className="absolute top-6 right-6 p-3 bg-white rounded-full shadow-lg hover:bg-red-50 transition-colors"
            >
              <Heart
                className={`w-6 h-6 ${
                  isFavorite ? 'text-red-500 fill-red-500' : 'text-gray-600'
                }`}
              />
            </button>
          </div>

          <div className="p-8">
            <h1 className="text-4xl mb-6">{displayName}</h1>

            <div className="bg-gray-50 rounded-xl p-6 mb-8">
              <div className="grid grid-cols-2 md:grid-cols-2 gap-6">
                <div className="flex items-center space-x-3">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-500">Год выпуска</p>
                    <p className="font-medium">{displayYear}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Gauge className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-500">ID</p>
                    <p className="font-medium text-sm">{car.id}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
