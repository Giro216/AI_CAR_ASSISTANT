import { Heart, ArrowRight } from 'lucide-react';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';

const cars = [
  {
    id: 1,
    name: 'BMW 5 Series',
    price: '5 200 000 ₽',
    year: 2024,
    engine: '2.0 л, 249 л.с.',
    transmission: 'Автомат',
    image: 'https://images.unsplash.com/photo-1707483413416-ca279c8b7a02?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBjYXIlMjBmcm9udHxlbnwxfHx8fDE3Njg1MDQ0MDV8MA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 2,
    name: 'Porsche 911',
    price: '9 800 000 ₽',
    year: 2024,
    engine: '3.0 л, 385 л.с.',
    transmission: 'Автомат',
    image: 'https://images.unsplash.com/photo-1696581081901-f8e0f10713b2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzcG9ydHMlMjBjYXIlMjByZWR8ZW58MXx8fHwxNzY4NTQ4MzgxfDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
  {
    id: 3,
    name: 'Mercedes-Benz GLE',
    price: '7 500 000 ₽',
    year: 2024,
    engine: '2.0 л, 258 л.с.',
    transmission: 'Автомат',
    image: 'https://images.unsplash.com/photo-1758411898280-2dc7c95e0ba7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdXYlMjBtb2Rlcm4lMjBjYXJ8ZW58MXx8fHwxNzY4NTY1NDQ3fDA&ixlib=rb-4.1.0&q=80&w=1080',
  },
];

interface PopularCarsProps {
  onCatalogClick: () => void;
  onToggleFavorite: (id: number) => void;
  favoriteIds: number[];
}

export function PopularCars({ onCatalogClick, onToggleFavorite, favoriteIds }: PopularCarsProps) {
  return (
    <section className="py-16 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h2 className="text-3xl mb-2">Популярные автомобили</h2>
            <p className="text-gray-600">Самые востребованные модели этого месяца</p>
          </div>
          <button
            onClick={onCatalogClick}
            className="hidden md:flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors"
          >
            <span>Смотреть все</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cars.map((car) => (
            <div
              key={car.id}
              className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow group"
            >
              <div className="relative h-56 overflow-hidden">
                <ImageWithFallback
                  src={car.image}
                  alt={car.name}
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
                  <h3 className="text-xl">{car.name}</h3>
                  <span className="text-blue-600">{car.price}</span>
                </div>

                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <div className="flex items-center justify-between">
                    <span>Год:</span>
                    <span>{car.year}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Двигатель:</span>
                    <span>{car.engine}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Коробка:</span>
                    <span>{car.transmission}</span>
                  </div>
                </div>

                <button className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Подробнее
                </button>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={onCatalogClick}
          className="md:hidden flex items-center justify-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors mx-auto mt-8"
        >
          <span>Смотреть все</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </section>
  );
}