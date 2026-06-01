import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useOutletContext } from 'react-router';
import { ArrowLeft, Heart, ChevronLeft, ChevronRight } from 'lucide-react';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';

interface CarConfig {
  id: number;
  doors: number;
  engineType: string;
  transmission: string;
  series: string;
  price: number;
  specs: {
    engine: string;
    power: string;
    drive: string;
    fuelType: string;
    consumption: string;
    acceleration: string;
    maxSpeed: string;
    dimensions: string;
    trunk: string;
    weight: string;
  };
}

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
}

const mockCarData = {
  name: 'BMW 5 Series',
  images: [
    'https://images.unsplash.com/photo-1707483413416-ca279c8b7a02?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBjYXIlMjBmcm9udHxlbnwxfHx8fDE3Njg1MDQ0MDV8MA&ixlib=rb-4.1.0&q=80&w=1080',
    'https://images.unsplash.com/photo-1555215695-3004980ad54e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwyfHxsdXh1cnklMjBjYXIlMjBpbnRlcmlvcnxlbnwxfHx8fDE3Njg1MDQ0MDV8MA&ixlib=rb-4.1.0&q=80&w=1080',
    'https://images.unsplash.com/photo-1627454820516-d0fbb44ba71c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwzfHxsdXh1cnklMjBjYXIlMjBzaWRlfGVufDF8fHx8MTc2ODUwNDQwNXww&ixlib=rb-4.1.0&q=80&w=1080',
  ],
  configurations: [
    {
      id: 1,
      doors: 4,
      engineType: '2.0 Бензин',
      transmission: 'Автомат',
      series: 'Series Active',
      price: 5200000,
      specs: {
        engine: '2.0 л, Бензин',
        power: '249 л.с.',
        drive: 'Задний',
        fuelType: 'АИ-95',
        consumption: '7.1 л/100км',
        acceleration: '6.2 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '530 л',
        weight: '1665 кг',
      },
    },
    {
      id: 2,
      doors: 4,
      engineType: '2.0 Бензин',
      transmission: 'Механика',
      series: 'Series Active',
      price: 4800000,
      specs: {
        engine: '2.0 л, Бензин',
        power: '249 л.с.',
        drive: 'Задний',
        fuelType: 'АИ-95',
        consumption: '6.8 л/100км',
        acceleration: '6.5 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '530 л',
        weight: '1620 кг',
      },
    },
    {
      id: 3,
      doors: 4,
      engineType: '3.0 Бензин',
      transmission: 'Автомат',
      series: 'Series M Sport',
      price: 6500000,
      specs: {
        engine: '3.0 л, Бензин',
        power: '340 л.с.',
        drive: 'Полный',
        fuelType: 'АИ-95',
        consumption: '8.3 л/100км',
        acceleration: '4.8 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '530 л',
        weight: '1740 кг',
      },
    },
    {
      id: 4,
      doors: 5,
      engineType: '2.0 Бензин',
      transmission: 'Автомат',
      series: 'Series Active',
      price: 5400000,
      specs: {
        engine: '2.0 л, Бензин',
        power: '249 л.с.',
        drive: 'Задний',
        fuelType: 'АИ-95',
        consumption: '7.2 л/100км',
        acceleration: '6.3 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '560 л',
        weight: '1680 кг',
      },
    },
    {
      id: 5,
      doors: 5,
      engineType: '3.0 Дизель',
      transmission: 'Автомат',
      series: 'Series M Sport',
      price: 6200000,
      specs: {
        engine: '3.0 л, Дизель',
        power: '286 л.с.',
        drive: 'Полный',
        fuelType: 'Дизель',
        consumption: '5.8 л/100км',
        acceleration: '5.5 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '560 л',
        weight: '1790 кг',
      },
    },
    {
      id: 6,
      doors: 5,
      engineType: '3.0 Дизель',
      transmission: 'Автомат',
      series: 'Series M Sport',
      price: 9000000,
      specs: {
        engine: '3.0 л, Дизель',
        power: '286 л.с.',
        drive: 'Полный',
        fuelType: 'Дизель',
        consumption: '5.8 л/100км',
        acceleration: '5.5 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '560 л',
        weight: '1790 кг',
      },
    },
    {
      id: 7,
      doors: 4,
      engineType: '2.5 Бензин',
      transmission: 'Автомат',
      series: 'Series Luxury',
      price: 5900000,
      specs: {
        engine: '2.5 л, Бензин',
        power: '258 л.с.',
        drive: 'Задний',
        fuelType: 'АИ-95',
        consumption: '7.6 л/100км',
        acceleration: '6.0 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '530 л',
        weight: '1705 кг',
      },
    },
    {
      id: 8,
      doors: 4,
      engineType: '2.5 Бензин',
      transmission: 'Автомат',
      series: 'Series Luxury',
      price: 6400000,
      specs: {
        engine: '2.5 л, Бензин',
        power: '258 л.с.',
        drive: 'Полный',
        fuelType: 'АИ-95',
        consumption: '8.1 л/100км',
        acceleration: '5.9 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '530 л',
        weight: '1780 кг',
      },
    },
    {
      id: 9,
      doors: 4,
      engineType: '3.0 Бензин',
      transmission: 'Автомат',
      series: 'Series M Sport',
      price: 7200000,
      specs: {
        engine: '3.0 л, Бензин',
        power: '340 л.с.',
        drive: 'Полный',
        fuelType: 'АИ-98',
        consumption: '9.1 л/100км',
        acceleration: '4.7 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '530 л',
        weight: '1845 кг',
      },
    },
    {
      id: 10,
      doors: 5,
      engineType: '2.0 Бензин',
      transmission: 'Механика',
      series: 'Series Active',
      price: 5100000,
      specs: {
        engine: '2.0 л, Бензин',
        power: '204 л.с.',
        drive: 'Задний',
        fuelType: 'АИ-95',
        consumption: '7.9 л/100км',
        acceleration: '7.2 сек (0-100 км/ч)',
        maxSpeed: '240 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '560 л',
        weight: '1685 кг',
      },
    },
    {
      id: 11,
      doors: 5,
      engineType: '2.0 Гибрид',
      transmission: 'Автомат',
      series: 'Series Eco',
      price: 6100000,
      specs: {
        engine: '2.0 л, Гибрид',
        power: '252 л.с.',
        drive: 'Полный',
        fuelType: 'АИ-95',
        consumption: '4.9 л/100км',
        acceleration: '6.4 сек (0-100 км/ч)',
        maxSpeed: '235 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '520 л',
        weight: '1860 кг',
      },
    },
    {
      id: 12,
      doors: 5,
      engineType: '3.0 Дизель',
      transmission: 'Автомат',
      series: 'Series M Sport',
      price: 8300000,
      specs: {
        engine: '3.0 л, Дизель',
        power: '320 л.с.',
        drive: 'Полный',
        fuelType: 'Дизель',
        consumption: '6.3 л/100км',
        acceleration: '5.2 сек (0-100 км/ч)',
        maxSpeed: '250 км/ч',
        dimensions: '4963×1868×1479 мм',
        trunk: '560 л',
        weight: '1900 кг',
      },
    },
  ],
};

export function CarConfiguratorPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { favoriteCarIds, handleToggleFavorite } = useOutletContext<OutletContext>();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [selectedVariantId, setSelectedVariantId] = useState<number | null>(null);
  const [selectedSeries, setSelectedSeries] = useState('');

  const availableDoors = [...new Set(mockCarData.configurations.map(c => c.doors))];
  const [selectedDoors, setSelectedDoors] = useState(availableDoors[0]);

  const configsForDoors = useMemo(
    () => mockCarData.configurations.filter(c => c.doors === selectedDoors),
    [selectedDoors]
  );

  const seriesOptions = useMemo(() => {
    const map = new Map<string, { name: string; image: string; configId: number }>();
    configsForDoors.forEach((config, index) => {
      if (!map.has(config.series)) {
        const image = mockCarData.images[index % mockCarData.images.length];
        map.set(config.series, { name: config.series, image, configId: config.id });
      }
    });
    return Array.from(map.values());
  }, [configsForDoors]);

  const configsForSeries = useMemo(() => {
    if (!selectedSeries) return configsForDoors;
    return configsForDoors.filter(c => c.series === selectedSeries);
  }, [configsForDoors, selectedSeries]);

  const engineOptions = useMemo(() => {
    const map = new Map<string, { key: string; label: string }>();
    configsForSeries.forEach((config) => {
      const volume = (config.specs.engine.split(',')[0] || config.specs.engine).trim();
      const fuel = (config.specs.engine.split(',')[1] || config.specs.fuelType || '').trim();
      const power = config.specs.power.trim();
      const key = `${volume}|${power}|${fuel}`;
      if (!map.has(key)) {
        const label = [volume, power, fuel].filter(Boolean).join(', ');
        map.set(key, { key, label });
      }
    });
    return Array.from(map.values());
  }, [configsForSeries]);

  const [selectedEngineKey, setSelectedEngineKey] = useState(
    engineOptions[0]?.key ?? ''
  );

  const configsForEngine = useMemo(() => {
    if (!selectedEngineKey) return configsForSeries;
    return configsForSeries.filter((config) => {
      const volume = (config.specs.engine.split(',')[0] || config.specs.engine).trim();
      const fuel = (config.specs.engine.split(',')[1] || config.specs.fuelType || '').trim();
      const power = config.specs.power.trim();
      return `${volume}|${power}|${fuel}` === selectedEngineKey;
    });
  }, [configsForSeries, selectedEngineKey]);

  const availableGearboxes = [...new Set(configsForEngine.map(c => c.transmission))];
  const [selectedGearbox, setSelectedGearbox] = useState(availableGearboxes[0] ?? '');

  const configsForGearbox = useMemo(() => {
    if (!selectedGearbox) return configsForEngine;
    return configsForEngine.filter(c => c.transmission === selectedGearbox);
  }, [configsForEngine, selectedGearbox]);

  const availableDrives = [...new Set(configsForGearbox.map(c => c.specs.drive))];
  const [selectedDrive, setSelectedDrive] = useState(availableDrives[0] ?? '');

  const matchingConfigs = useMemo(() => {
    return configsForSeries.filter((config) => {
      const volume = (config.specs.engine.split(',')[0] || config.specs.engine).trim();
      const fuel = (config.specs.engine.split(',')[1] || config.specs.fuelType || '').trim();
      const power = config.specs.power.trim();
      const engineKey = `${volume}|${power}|${fuel}`;
      const matchesEngine = selectedEngineKey ? engineKey === selectedEngineKey : true;
      const matchesGearbox = selectedGearbox ? config.transmission === selectedGearbox : true;
      const matchesDrive = selectedDrive ? config.specs.drive === selectedDrive : true;
      return matchesEngine && matchesGearbox && matchesDrive;
    });
  }, [configsForSeries, selectedEngineKey, selectedGearbox, selectedDrive]);

  useEffect(() => {
    setSelectedSeries(seriesOptions[0]?.name ?? '');
  }, [seriesOptions]);

  useEffect(() => {
    setSelectedEngineKey(engineOptions[0]?.key ?? '');
  }, [engineOptions]);

  useEffect(() => {
    setSelectedGearbox(availableGearboxes[0] ?? '');
  }, [availableGearboxes]);

  useEffect(() => {
    setSelectedDrive(availableDrives[0] ?? '');
  }, [availableDrives]);

  useEffect(() => {
    const firstId = matchingConfigs[0]?.id ?? null;
    setSelectedVariantId((prev) => (prev && matchingConfigs.some(c => c.id === prev) ? prev : firstId));
  }, [matchingConfigs]);

  const currentConfig = matchingConfigs.find(c => c.id === selectedVariantId)
    ?? matchingConfigs[0]
    ?? configsForSeries[0]
    ?? mockCarData.configurations[0];

  const handleDoorsChange = (doors: number) => {
    setSelectedDoors(doors);
  };

  const handleSeriesChange = (series: string) => {
    setSelectedSeries(series);
    setSelectedVariantId(null);
  };

  const handleEngineChange = (engineKey: string) => {
    setSelectedEngineKey(engineKey);
  };

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % mockCarData.images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + mockCarData.images.length) % mockCarData.images.length);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
  };

  const carId = id ?? '';
  const isFavorite = favoriteCarIds.includes(carId);

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
          <div className="relative h-[500px] bg-black">
            <ImageWithFallback
              src={mockCarData.images[currentImageIndex]}
              alt={mockCarData.name}
              className="w-full h-full object-cover"
            />

            <button
              onClick={prevImage}
              className="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-white/90 rounded-full shadow-lg hover:bg-white transition-colors"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>

            <button
              onClick={nextImage}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-white/90 rounded-full shadow-lg hover:bg-white transition-colors"
            >
              <ChevronRight className="w-6 h-6" />
            </button>

            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
              {mockCarData.images.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentImageIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index === currentImageIndex ? 'bg-white w-8' : 'bg-white/50'
                  }`}
                />
              ))}
            </div>
          </div>

          <div className="p-8">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="text-4xl mb-2">{mockCarData.name}</h1>
                <p className="text-3xl text-blue-600 font-medium">{formatPrice(currentConfig.price)}</p>
              </div>
            </div>

            {seriesOptions.length > 1 && (
              <div className="mb-8 pb-8 border-b border-gray-200">
                <h3 className="text-xl mb-4">Варианты серии</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {seriesOptions.map((series) => {
                    const isActive = selectedSeries === series.name;
                    return (
                      <button
                        key={series.name}
                        onClick={() => handleSeriesChange(series.name)}
                        className={`flex items-center gap-4 p-3 rounded-xl border-2 transition-colors text-left ${
                          isActive ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <ImageWithFallback
                          src={series.image}
                          alt={series.name}
                          className="w-20 h-14 rounded-lg object-cover"
                        />
                        <div>
                          <div className="text-sm text-gray-500">Series</div>
                          <div className="font-medium">{series.name}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            <div className="mb-8 pb-8 border-b border-gray-200">
              <h3 className="text-xl mb-4">Конфигурация</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                {availableDoors.length > 1 && (
                  <div>
                    <label className="block text-sm text-gray-600 mb-2">Количество дверей</label>
                    <div className="flex space-x-2">
                      {availableDoors.map((doors) => (
                        <button
                          key={doors}
                          onClick={() => handleDoorsChange(doors)}
                          className={`flex-1 px-4 py-3 rounded-lg border-2 transition-colors ${
                            selectedDoors === doors
                              ? 'border-blue-600 bg-blue-50 text-blue-600'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          {doors} дв.
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm text-gray-600 mb-2">Тип двигателя</label>
                  <select
                    value={selectedEngineKey}
                    onChange={(e) => handleEngineChange(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-blue-600 focus:outline-none"
                  >
                    {engineOptions.map((engine) => (
                      <option key={engine.key} value={engine.key}>
                        {engine.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-600 mb-2">Коробка передач</label>
                  {availableGearboxes.length > 1 ? (
                    <select
                      value={selectedGearbox}
                      onChange={(e) => setSelectedGearbox(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-blue-600 focus:outline-none"
                    >
                      {availableGearboxes.map((gearbox) => (
                        <option key={gearbox} value={gearbox}>
                          {gearbox}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="w-full px-4 py-3 rounded-lg border-2 border-gray-200 bg-gray-50 text-gray-700">
                      {availableGearboxes[0] ?? '—'}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm text-gray-600 mb-2">Привод</label>
                  {availableDrives.length > 1 ? (
                    <select
                      value={selectedDrive}
                      onChange={(e) => setSelectedDrive(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-blue-600 focus:outline-none"
                    >
                      {availableDrives.map((drive) => (
                        <option key={drive} value={drive}>
                          {drive}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="w-full px-4 py-3 rounded-lg border-2 border-gray-200 bg-gray-50 text-gray-700">
                      {availableDrives[0] ?? '—'}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-2xl mb-6">Технические характеристики</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Двигатель:</span>
                    <span className="font-medium">{currentConfig.specs.engine}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Мощность:</span>
                    <span className="font-medium">{currentConfig.specs.power}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Привод:</span>
                    <span className="font-medium">{currentConfig.specs.drive}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Тип топлива:</span>
                    <span className="font-medium">{currentConfig.specs.fuelType}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Расход топлива:</span>
                    <span className="font-medium">{currentConfig.specs.consumption}</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Разгон 0-100 км/ч:</span>
                    <span className="font-medium">{currentConfig.specs.acceleration}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Макс. скорость:</span>
                    <span className="font-medium">{currentConfig.specs.maxSpeed}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Габариты (Д×Ш×В):</span>
                    <span className="font-medium">{currentConfig.specs.dimensions}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Объем багажника:</span>
                    <span className="font-medium">{currentConfig.specs.trunk}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">Снаряженная масса:</span>
                    <span className="font-medium">{currentConfig.specs.weight}</span>
                  </div>
                </div>
              </div>

              <div className="mt-8 flex space-x-4">
                <button className="flex-1 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-lg">
                  Оставить заявку
                </button>
                <button
                  onClick={() => handleToggleFavorite(carId)}
                  className={`px-6 py-4 border-2 rounded-lg transition-colors ${
                    isFavorite
                      ? 'border-red-500 bg-red-50'
                      : 'border-gray-300 hover:border-blue-600 hover:text-blue-600'
                  }`}
                >
                  <Heart
                    className={`w-6 h-6 ${
                      isFavorite ? 'text-red-500 fill-red-500' : ''
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
