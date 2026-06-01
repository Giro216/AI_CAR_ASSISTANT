import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useOutletContext } from 'react-router';
import { ArrowLeft, Heart, ChevronLeft, ChevronRight } from 'lucide-react';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';
import { CarFullInfoBase, getCarConfig } from '@/app/api/cars';

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
}

const placeholderImages = [
  'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1080&q=80',
  'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1080&q=80',
  'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1080&q=80',
];

export function CarConfiguratorPage() {
  const { id, bodyType, generation } = useParams();
  const navigate = useNavigate();
  const { favoriteCarIds, handleToggleFavorite } = useOutletContext<OutletContext>();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [selectedSeriesKey, setSelectedSeriesKey] = useState('');
  const [configs, setConfigs] = useState<CarFullInfoBase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id || !bodyType || !generation) {
      setConfigs([]);
      setIsLoading(false);
      setError('Не удалось определить параметры конфигурации');
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    // NOTE: Load full configuration rows for the selected model/body type.
    getCarConfig({ brand_model_id: id, body_type: bodyType, generation: generation })
      .then((data) => {
        if (!isMounted) return;
        setConfigs(data ?? []);
      })
      .catch((err) => {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : 'Не удалось загрузить конфигурацию');
      })
      .finally(() => {
        if (!isMounted) return;
        setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [id, bodyType, generation]);

  // NOTE: Series is the primary filter; other selectors depend on it.
  const seriesOptions = useMemo(() => {
    const map = new Map<string, { key: string; label: string; image: string }>();
    configs.forEach((config, index) => {
      const rawSeries = (config.series ?? '').trim();
      const key = rawSeries || '__none__';
      if (!map.has(key)) {
        const image = placeholderImages[index % placeholderImages.length];
        map.set(key, { key, label: rawSeries || 'Без серии', image });
      }
    });
    return Array.from(map.values());
  }, [configs]);

  useEffect(() => {
    setSelectedSeriesKey(seriesOptions[0]?.key ?? '');
  }, [seriesOptions]);

  const configsForSeries = useMemo(() => {
    if (!selectedSeriesKey) return configs;
    return configs.filter((config) => {
      const rawSeries = (config.series ?? '').trim();
      const key = rawSeries || '__none__';
      return key === selectedSeriesKey;
    });
  }, [configs, selectedSeriesKey]);

  const availableDoors = [...new Set(configsForSeries.map(c => c.doors_count).filter(Boolean))] as number[];
  const [selectedDoors, setSelectedDoors] = useState<number | null>(null);

  useEffect(() => {
    setSelectedDoors(availableDoors[0] ?? null);
  }, [availableDoors]);

  const configsForDoors = useMemo(() => {
    if (!selectedDoors) return configsForSeries;
    return configsForSeries.filter(c => c.doors_count === selectedDoors);
  }, [configsForSeries, selectedDoors]);

  const formatLiters = (capacity?: number | null) => {
    if (!capacity) return '';
    return (capacity / 1000).toFixed(1);
  };

  const buildEngineKey = (config: CarFullInfoBase) => {
    return `${config.capacity_cm3 ?? ''}|${config.engine_hp ?? ''}|${config.fuel_grade ?? config.engine_type ?? ''}`;
  };

  const formatEngineLabel = (config: CarFullInfoBase) => {
    const liters = formatLiters(config.capacity_cm3);
    const power = config.engine_hp ? `${config.engine_hp} л.с.` : '';
    const fuel = config.fuel_grade ?? config.engine_type ?? '';
    const volumeLabel = liters ? `${liters} л` : '';
    return [volumeLabel, power, fuel].filter(Boolean).join(', ');
  };

  const engineOptions = useMemo(() => {
    const map = new Map<string, { key: string; label: string }>();
    configsForDoors.forEach((config) => {
      const key = buildEngineKey(config);
      if (!map.has(key)) {
        map.set(key, { key, label: formatEngineLabel(config) || '—' });
      }
    });
    return Array.from(map.values());
  }, [configsForDoors]);

  const [selectedEngineKey, setSelectedEngineKey] = useState(engineOptions[0]?.key ?? '');

  const configsForEngine = useMemo(() => {
    if (!selectedEngineKey) return configsForDoors;
    return configsForDoors.filter((config) => buildEngineKey(config) === selectedEngineKey);
  }, [configsForDoors, selectedEngineKey]);

  const availableGearboxes = [...new Set(configsForEngine.map(c => c.transmission_type).filter(Boolean))] as string[];
  const [selectedGearbox, setSelectedGearbox] = useState(availableGearboxes[0] ?? '');

  const configsForGearbox = useMemo(() => {
    if (!selectedGearbox) return configsForEngine;
    return configsForEngine.filter(c => c.transmission_type === selectedGearbox);
  }, [configsForEngine, selectedGearbox]);

  const availableDrives = [...new Set(configsForGearbox.map(c => c.drive_wheels).filter(Boolean))] as string[];
  const [selectedDrive, setSelectedDrive] = useState(availableDrives[0] ?? '');

  const matchingConfigs = useMemo(() => {
    return configsForGearbox.filter((config) => {
      const matchesDrive = selectedDrive ? config.drive_wheels === selectedDrive : true;
      return matchesDrive;
    });
  }, [configsForGearbox, selectedDrive]);

  useEffect(() => {
    setSelectedEngineKey(engineOptions[0]?.key ?? '');
  }, [engineOptions]);

  useEffect(() => {
    if (!availableGearboxes.length) {
      setSelectedGearbox('');
      return;
    }

    setSelectedGearbox((current) => (availableGearboxes.includes(current) ? current : availableGearboxes[0]));
  }, [availableGearboxes]);

  useEffect(() => {
    setSelectedDrive(availableDrives[0] ?? '');
  }, [availableDrives]);

  const currentConfig = matchingConfigs[0]
    ?? configsForEngine[0]
    ?? configsForDoors[0]
    ?? configsForSeries[0]
    ?? configs[0];

  const handleDoorsChange = (doors: number) => {
    setSelectedDoors(doors);
  };

  const handleSeriesChange = (seriesKey: string) => {
    setSelectedSeriesKey(seriesKey);
  };

  const handleEngineChange = (engineKey: string) => {
    setSelectedEngineKey(engineKey);
  };

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % placeholderImages.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + placeholderImages.length) % placeholderImages.length);
  };

  const displayName = useMemo(() => {
    const item = currentConfig;
    if (!item) return 'Автомобиль';
    return `${item.make ?? ''} ${item.model ?? ''}`.trim() || 'Автомобиль';
  }, [currentConfig]);

  const displayEngine = currentConfig ? formatEngineLabel(currentConfig) : '—';
  const displayPower = currentConfig?.engine_hp ? `${currentConfig.engine_hp} л.с.` : '—';
  const displayDrive = currentConfig?.drive_wheels ?? '—';
  const displayFuel = currentConfig?.fuel_grade ?? currentConfig?.engine_type ?? '—';
  const displayConsumption = currentConfig?.mixed_fuel_consumption_per_100_km_l
    ? `${currentConfig.mixed_fuel_consumption_per_100_km_l} л/100км`
    : '—';
  const displayAcceleration = currentConfig?.acceleration_0_100_km_h_s
    ? `${currentConfig.acceleration_0_100_km_h_s} сек (0-100 км/ч)`
    : '—';
  const displayMaxSpeed = currentConfig?.max_speed_km_per_h
    ? `${currentConfig.max_speed_km_per_h} км/ч`
    : '—';
  const displayDimensions = currentConfig?.length_mm && currentConfig?.width_mm && currentConfig?.height_mm
    ? `${currentConfig.length_mm}×${currentConfig.width_mm}×${currentConfig.height_mm} мм`
    : '—';
  const displayTrunk = currentConfig?.min_trunk_capacity_l && currentConfig?.max_trunk_capacity_l
    ? `${currentConfig.min_trunk_capacity_l}–${currentConfig.max_trunk_capacity_l} л`
    : currentConfig?.min_trunk_capacity_l
      ? `${currentConfig.min_trunk_capacity_l} л`
      : '—';
  const displayWeight = currentConfig?.curb_weight_kg ? `${currentConfig.curb_weight_kg} кг` : '—';

  const sections = useMemo(() => {
    return [
      {
        title: 'Общая информация',
        items: [
          { label: 'ID модели', value: currentConfig?.brand_model_id ?? '—' },
          { label: 'Марка', value: currentConfig?.make ?? '—' },
          { label: 'Модель', value: currentConfig?.model ?? '—' },
          { label: 'Поколение', value: currentConfig?.generation ?? '—' },
          { label: 'Серия', value: currentConfig?.series ?? '—' },
          { label: 'Комплектация', value: currentConfig?.trim ?? '—' },
          { label: 'Год от', value: currentConfig?.year_from ?? '—' },
          { label: 'Год до', value: currentConfig?.year_to ?? '—' },
          { label: 'Тип кузова', value: currentConfig?.body_type ?? '—' },
          { label: 'Количество дверей', value: currentConfig?.doors_count ?? '—' },
          { label: 'Battery ID', value: currentConfig?.battery_id ?? '—' },
        ],
      },
      {
        title: 'Габариты',
        items: [
          { label: 'Длина', value: currentConfig?.length_mm ? `${currentConfig.length_mm} мм` : '—' },
          { label: 'Ширина', value: currentConfig?.width_mm ? `${currentConfig.width_mm} мм` : '—' },
          { label: 'Высота', value: currentConfig?.height_mm ? `${currentConfig.height_mm} мм` : '—' },
          { label: 'Колесная база', value: currentConfig?.wheelbase_mm ? `${currentConfig.wheelbase_mm} мм` : '—' },
          { label: 'Передняя колея', value: currentConfig?.front_track_mm ? `${currentConfig.front_track_mm} мм` : '—' },
          { label: 'Задняя колея', value: currentConfig?.rear_track_mm ? `${currentConfig.rear_track_mm} мм` : '—' },
          { label: 'Клиренс', value: currentConfig?.ground_clearance_mm ? `${currentConfig.ground_clearance_mm} мм` : '—' },
        ],
      },
      {
        title: 'Масса и багажник',
        items: [
          { label: 'Снаряженная масса', value: displayWeight },
          { label: 'Грузоподъемность', value: currentConfig?.payload_kg ? `${currentConfig.payload_kg} кг` : '—' },
          { label: 'Полная масса', value: currentConfig?.full_weight_kg ? `${currentConfig.full_weight_kg} кг` : '—' },
          {
            label: 'Объем багажника',
            value:
              currentConfig?.min_trunk_capacity_l && currentConfig?.max_trunk_capacity_l
                ? `${currentConfig.min_trunk_capacity_l}–${currentConfig.max_trunk_capacity_l} л`
                : currentConfig?.min_trunk_capacity_l
                  ? `${currentConfig.min_trunk_capacity_l} л`
                  : '—',
          },
        ],
      },
      {
        title: 'Двигатель',
        items: [
          { label: 'Engine ID', value: currentConfig?.engine_id_unique ?? '—' },
          { label: 'Тип двигателя', value: currentConfig?.engine_type ?? '—' },
          { label: 'Компоновка цилиндров', value: currentConfig?.cylinder_layout ?? '—' },
          { label: 'Количество цилиндров', value: currentConfig?.number_of_cylinders ?? '—' },
          { label: 'Клапанов на цилиндр', value: currentConfig?.valves_per_cylinder ?? '—' },
          { label: 'Наддув', value: currentConfig?.boost_type ?? '—' },
          { label: 'Объем', value: currentConfig?.capacity_cm3 ? `${currentConfig.capacity_cm3} см³` : '—' },
          { label: 'Мощность кВт', value: currentConfig?.max_power_kw ? `${currentConfig.max_power_kw} кВт` : '—' },
          { label: 'Мощность л.с.', value: displayPower },
          { label: 'Крутящий момент', value: currentConfig?.maximum_torque_n_m ? `${currentConfig.maximum_torque_n_m} Н·м` : '—' },
        ],
      },
      {
        title: 'Трансмиссия',
        items: [
          { label: 'Transmission ID', value: currentConfig?.transmission_id_unique ?? '—' },
          { label: 'Тип коробки', value: currentConfig?.transmission_type ?? '—' },
          { label: 'Число передач', value: currentConfig?.number_of_gears ?? '—' },
          { label: 'Привод', value: displayDrive },
        ],
      },
      {
        title: 'Эксплуатационные показатели',
        items: [
          { label: 'Разгон 0-100', value: displayAcceleration },
          { label: 'Макс. скорость', value: displayMaxSpeed },
          { label: 'Топливо', value: displayFuel },
          {
            label: 'Объем бака',
            value: currentConfig?.fuel_tank_capacity_l ? `${currentConfig.fuel_tank_capacity_l} л` : '—',
          },
          { label: 'Смешанный расход', value: displayConsumption },
          {
            label: 'Городской расход',
            value: currentConfig?.city_fuel_per_100km_l ? `${currentConfig.city_fuel_per_100km_l} л/100км` : '—',
          },
          {
            label: 'Трассовый расход',
            value: currentConfig?.highway_fuel_per_100km_l ? `${currentConfig.highway_fuel_per_100km_l} л/100км` : '—',
          },
          { label: 'Экостандарт', value: currentConfig?.emission_standards ?? '—' },
        ],
      },
      {
        title: 'Подвеска и тормоза',
        items: [
          { label: 'Передняя подвеска', value: currentConfig?.front_suspension ?? '—' },
          { label: 'Задняя подвеска', value: currentConfig?.back_suspension ?? '—' },
          { label: 'Передние тормоза', value: currentConfig?.front_brakes ?? '—' },
          { label: 'Задние тормоза', value: currentConfig?.rear_brakes ?? '—' },
        ],
      },
    ];
  }, [currentConfig, displayAcceleration, displayConsumption, displayDrive, displayFuel, displayMaxSpeed, displayPower, displayWeight]);

  const carId = id ?? '';
  const isFavorite = favoriteCarIds.includes(carId);

  if (isLoading) {
    return <div className="py-16 px-4 text-center text-gray-500">Загрузка конфигурации…</div>;
  }

  if (error) {
    return <div className="py-16 px-4 text-center text-red-600">{error}</div>;
  }

  if (!currentConfig) {
    return <div className="py-16 px-4 text-center text-gray-500">Нет данных по конфигурации</div>;
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
          <div className="relative h-[500px] bg-black">
            <ImageWithFallback
              src={placeholderImages[currentImageIndex]}
              alt={displayName}
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
              {placeholderImages.map((_, index) => (
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
                <h1 className="text-4xl mb-2">{displayName}</h1>
                <p className="text-sm text-gray-500"></p>
              </div>
            </div>

            {seriesOptions.length > 1 && (
              <div className="mb-8 pb-8 border-b border-gray-200">
                <h3 className="text-xl mb-4">Варианты серии</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {seriesOptions.map((series) => {
                    const isActive = selectedSeriesKey === series.key;
                    return (
                      <button
                        key={series.key}
                        onClick={() => handleSeriesChange(series.key)}
                        className={`flex items-center gap-4 p-3 rounded-xl border-2 transition-colors text-left ${
                          isActive ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <ImageWithFallback
                          src={series.image}
                          alt={series.label}
                          className="w-20 h-14 rounded-lg object-cover"
                        />
                        <div>
                          <div className="text-sm text-gray-500">Series</div>
                          <div className="font-medium">{series.label}</div>
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
              <h3 className="text-2xl mb-6">Характеристики</h3>
              <div className="space-y-6">
                {sections.map((section) => (
                  <div key={section.title} className="rounded-2xl border border-gray-200 bg-white">
                    <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 rounded-t-2xl">
                      <h4 className="text-lg font-medium">{section.title}</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-0 px-6 py-4">
                      {section.items
                        .filter((item) => !/id/i.test(String(item.label)))
                        .map((item) => (
                          <div key={item.label} className="flex justify-between gap-4 py-3 border-b border-gray-100 last:border-b-0">
                            <span className="text-gray-600">{item.label}</span>
                            <span className="font-medium text-right">{item.value as string | number}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
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
