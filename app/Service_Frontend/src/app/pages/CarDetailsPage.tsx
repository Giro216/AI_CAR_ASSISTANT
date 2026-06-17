import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useOutletContext } from 'react-router';
import { ArrowLeft, Heart, Calendar, Gauge, Settings, ChevronDown, ChevronUp } from 'lucide-react';
import { ImageWithFallback } from '@/app/components/figma/ImageWithFallback';
import { CarDto, GenerationDto, getCars, getGenerations } from '@/app/api/cars';

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
}

export function CarDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { favoriteCarIds, handleToggleFavorite } = useOutletContext<OutletContext>();
  const [car, setCar] = useState<CarDto | null>(null);
  const [generations, setGenerations] = useState<GenerationDto[]>([]);
  const [expandedGenerationKey, setExpandedGenerationKey] = useState<string | null>(null);
  const [expandedBodyKey, setExpandedBodyKey] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerationsLoading, setIsGenerationsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generationsError, setGenerationsError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);
    setCar(null);
    setGenerations([]);
    setGenerationsError(null);
    setExpandedGenerationKey(null);
    setExpandedBodyKey(null);

    getCars({ brand_model_id: id })
      .then((data) => {
        if (!isMounted) return;
        if (id == null) {
          setError('Некорректный идентификатор автомобиля');
          return;
        }
        const found = (data.founded_cars ?? []).find(item => item.brand_model_id === id) ?? null;
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

  useEffect(() => {
    if (!car?.brand || !car?.model) {
      setGenerations([]);
      setIsGenerationsLoading(false);
      return;
    }

    let isMounted = true;
    setIsGenerationsLoading(true);
    setGenerationsError(null);

    getGenerations({ brand: car.brand, model: car.model, brand_model_id: car.brand_model_id })
      .then((data) => {
        if (!isMounted) return;
        setGenerations(data ?? []);
      })
      .catch((err) => {
        if (!isMounted) return;
        setGenerationsError(
          err instanceof Error ? err.message : 'Не удалось загрузить поколения'
        );
      })
      .finally(() => {
        if (!isMounted) return;
        setIsGenerationsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [car?.brand, car?.model]);

  useEffect(() => {
    setExpandedGenerationKey(null);
    setExpandedBodyKey(null);
  }, [id, car?.brand, car?.model]);

  const generationSections = useMemo(() => {
    if (!generations.length) return [] as Array<{
      key: string;
      label: string;
      yearFrom?: number | null;
      yearTo?: number | null;
      bodyTypes: Array<{ key: string; label: string; id?: string | null }>;
    }>;

    const map = new Map<string, {
      label: string;
      yearFrom?: number | null;
      yearTo?: number | null;
      bodyTypes: Map<string, { label: string; id?: string | null }>;
    }>();

    generations.forEach((item) => {
      const raw = (item.generation ?? '').trim();
      const key = raw || '__none__';
      const label = raw || 'Без поколения';
      const bodyRaw = (item.bodyType ?? '').trim();
      const bodyKey = bodyRaw || '__none__';
      const bodyLabel = bodyRaw || 'Без кузова';

      const entry = map.get(key);
      const yearFrom = item.year_from ?? null;
      const yearTo = item.year_to ?? null;

      if (!entry) {
        map.set(key, {
          label,
          yearFrom,
          yearTo,
          bodyTypes: new Map([[bodyKey, { label: bodyLabel, id: item.id }]]),
        });
        return;
      }

      const mergedFrom =
        entry.yearFrom == null ? yearFrom : yearFrom == null ? entry.yearFrom : Math.min(entry.yearFrom, yearFrom);
      const mergedTo =
        entry.yearTo == null ? yearTo : yearTo == null ? entry.yearTo : Math.max(entry.yearTo, yearTo);
      entry.yearFrom = mergedFrom;
      entry.yearTo = mergedTo;

      if (!entry.bodyTypes.has(bodyKey)) {
        entry.bodyTypes.set(bodyKey, { label: bodyLabel, id: item.id });
      }
    });

    return Array.from(map.entries()).map(([key, value]) => ({
      key,
      label: value.label,
      yearFrom: value.yearFrom,
      yearTo: value.yearTo,
      bodyTypes: Array.from(value.bodyTypes.entries()).map(([bodyKey, body]) => ({
        key: bodyKey,
        label: body.label,
        id: body.id,
      })),
    }));
  }, [generations]);

  const availableBodies = useMemo(() => {
    const bodies = new Set<string>();
    generations.forEach((item) => {
      if (item.bodyType && item.bodyType.trim()) {
        bodies.add(item.bodyType.trim());
      }
    });
    return Array.from(bodies);
  }, [generations]);

  const displayBodies = useMemo(() => {
    if (!availableBodies.length) return '—';
    return availableBodies.join(', ');
  }, [availableBodies]);

  const toggleGeneration = (key: string) => {
    setExpandedGenerationKey(expandedGenerationKey === key ? null : key);
    setExpandedBodyKey(null);
  };

  const toggleBodyType = (body_key: string, gen_label: string, body_label: string, brand_model_id?: string | null) => {
    const nextKey = expandedBodyKey === body_key ? null : body_key;
    setExpandedBodyKey(nextKey);
    if (id) {
      navigate(`/catalog/${brand_model_id}/${gen_label}/${body_label}`);
    }
  };

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

  const isFavorite = car ? favoriteCarIds.includes(car.brand_model_id) : false;

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
              onClick={() => handleToggleFavorite(car.brand_model_id)}
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
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* 1. Года производства */}
                <div className="flex items-center space-x-3">
                  <Calendar className="w-5 h-5 text-blue-600 shrink-0" />
                  <div>
                    <p className="text-sm text-gray-500">Годы выпуска</p>
                    <p className="font-medium">{displayYear}</p>
                  </div>
                </div>

                {/* 2. Количество поколений */}
                <div className="flex items-center space-x-3">
                  <Settings className="w-5 h-5 text-blue-600 shrink-0" />
                  <div>
                    <p className="text-sm text-gray-500">Количество поколений</p>
                    <p className="font-medium">
                      {isGenerationsLoading ? 'Загрузка...' : `${generationSections.length}`}
                    </p>
                  </div>
                </div>

                {/* 3. Возможные кузова (мелкий шрифт) */}
                <div className="flex items-center space-x-3 min-w-0">
                  <Gauge className="w-5 h-5 text-blue-600 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-gray-500">Типы кузова</p>
                    <p className="text-sm font-medium text-gray-800 truncate" title={displayBodies}>
                      {isGenerationsLoading ? 'Загрузка...' : displayBodies}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-2xl mb-6">Поколения и комплектации</h3>
              <div className="space-y-4">
                {isGenerationsLoading ? (
                  <div className="text-gray-500">Загрузка поколений…</div>
                ) : generationsError ? (
                  <div className="text-red-600">{generationsError}</div>
                ) : generationSections.length === 0 ? (
                  <div className="text-gray-500">Нет данных по поколениям</div>
                ) : (
                  generationSections.map((generation) => (
                    <div key={generation.key} className="border border-gray-200 rounded-xl overflow-hidden">
                      <button
                        onClick={() => toggleGeneration(generation.key)}
                        className="w-full px-6 py-5 bg-white hover:bg-gray-50 transition-colors flex items-center justify-between"
                      >
                        <div className="text-left">
                          <h4 className="font-medium text-lg">
                            {generation.label}
                            {(generation.yearFrom || generation.yearTo) && (
                              <span className="text-gray-500 text-sm">{
                                ` (${generation.yearFrom ?? '—'}–${generation.yearTo ?? '—'})`
                              }</span>
                            )}
                          </h4>
                          <p className="text-sm text-gray-500">
                            {generation.bodyTypes.length} кузова
                          </p>
                        </div>
                        {expandedGenerationKey === generation.key ? (
                          <ChevronUp className="w-6 h-6 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-6 h-6 text-gray-400" />
                        )}
                      </button>

                      {expandedGenerationKey === generation.key && (
                        <div className="bg-gray-50 border-t border-gray-200">
                          {generation.bodyTypes.map((body) => {
                            const bodyKey = `${generation.key}::${body.key}`;
                            return (
                              <div key={bodyKey} className="border-b border-gray-200 last:border-b-0">
                                <button
                                  onClick={() => toggleBodyType(bodyKey, generation.key, body.key, id)}
                                  className="w-full px-6 py-4 hover:bg-gray-100 transition-colors flex items-center justify-between"
                                >
                                  <div className="text-left">
                                    <h5 className="font-medium text-lg">{body.label}</h5>
                                    <p className="text-blue-600 font-medium">Перейти к карточке</p>
                                  </div>
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
