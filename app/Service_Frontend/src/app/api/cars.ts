export interface CarDto {
  id: string;
  brand_model_id: string;
  brand: string;
  model: string;
  start_year?: number | null;
  end_year?: number | null;
  imageUrl?: string | null;
  isPopular?: boolean;
}

export interface CatalogData {
  cars_count: number;
  founded_cars: CarDto[];
}

export interface GenerationDto {
  id: string;
  brand_model_id: string;
  brand: string;
  model: string;
  generation?: string | null;
  gen_comment?: string | null;
  year_from?: number | null;
  year_to?: number | null;
  bodyType?: string | null;
  imageUrl?: string | null;
}

export interface CarFullInfoBase {
  brand_model_id: number;
  make?: string | null;
  model?: string | null;
  generation?: string | null;
  series?: string | null;
  trim?: string | null;
  year_from?: number | null;
  year_to?: number | null;
  body_type?: string | null;
  doors_count?: number | null;
  battery_id?: number | null;
  length_mm?: number | null;
  width_mm?: number | null;
  height_mm?: number | null;
  wheelbase_mm?: number | null;
  front_track_mm?: number | null;
  rear_track_mm?: number | null;
  ground_clearance_mm?: number | null;
  curb_weight_kg?: number | null;
  payload_kg?: number | null;
  full_weight_kg?: number | null;
  min_trunk_capacity_l?: number | null;
  max_trunk_capacity_l?: number | null;
  engine_id_unique?: number | null;
  engine_type?: string | null;
  cylinder_layout?: string | null;
  number_of_cylinders?: number | null;
  valves_per_cylinder?: number | null;
  boost_type?: string | null;
  capacity_cm3?: number | null;
  max_power_kw?: number | null;
  engine_hp?: number | null;
  maximum_torque_n_m?: number | null;
  transmission_id_unique?: number | null;
  transmission_type?: string | null;
  number_of_gears?: number | null;
  drive_wheels?: string | null;
  acceleration_0_100_km_h_s?: number | null;
  max_speed_km_per_h?: number | null;
  fuel_grade?: string | null;
  fuel_tank_capacity_l?: number | null;
  mixed_fuel_consumption_per_100_km_l?: number | null;
  city_fuel_per_100km_l?: number | null;
  highway_fuel_per_100km_l?: number | null;
  emission_standards?: string | null;
  front_suspension?: string | null;
  back_suspension?: string | null;
  front_brakes?: string | null;
  rear_brakes?: string | null;
}

const API_BASE = (import.meta.env.VITE_GATEWAY_URL as string | undefined) ?? '';

function buildUrl(path: string) {
  if (!API_BASE) {
    return path;
  }
  return `${API_BASE.replace(/\/$/, '')}${path}`;
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(buildUrl(path));
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  const contentType = response.headers.get('content-type') ?? '';
  if (!contentType.includes('application/json')) {
    const text = await response.text();
    const preview = text.slice(0, 140).replace(/\s+/g, ' ').trim();
    throw new Error(
      `Expected JSON but received ${contentType || 'unknown content type'}: ${preview}`
    );
  }
  return response.json() as Promise<T>;
}

export async function getCars(params?: {
  brand_model_id?: string;
  brand?: string;
  model?: string;
  sort?: string;
  limit?: number;
  page?: number;
}): Promise<CatalogData> {
  const search = new URLSearchParams();
  if (params?.brand_model_id) search.set('brand_model_id', params.brand_model_id);
  if (params?.brand) search.set('brand', params.brand);
  if (params?.model) search.set('model', params.model);
  if (params?.sort) search.set('sort', params.sort);
  if (params?.limit) search.set('limit', String(params.limit));
  if (params?.page) search.set('page', String(params.page));

  const query = search.toString();
  const path = query ? `/api/v1/cars?${query}` : '/api/v1/cars';
  return fetchJson<CatalogData>(path);
}

export async function getPopularCars(limit = 3): Promise<CarDto[]> {
  return fetchJson<CarDto[]>(`/api/v1/cars/popular?limit=${limit}`);
}

export async function searchCars(params: {
  q: string;
  limit?: number;
}): Promise<CatalogData> {
  const search = new URLSearchParams();
  search.set('q', params.q);
  if (params.limit) search.set('limit', String(params.limit));
  return fetchJson<CatalogData>(`/api/v1/cars/search?${search.toString()}`);
}

export async function getGenerations(params: {
  brand?: string;
  model?: string;
  brand_model_id: string;
}): Promise<GenerationDto[]> {
  const search = new URLSearchParams();
  if (params.brand) search.set('brand', params.brand);
  if (params.model) search.set('model', params.model);

  const query = search.toString();
  const path = query ? `/api/v1/cars/${params.brand_model_id}/generations?${query}` : `/api/v1/cars/${params.brand_model_id}/generations`;
  return fetchJson<GenerationDto[]>(path);
}

export async function getCarConfig(params: {
  brand_model_id: string;
  generation: string;
  body_type: string;
}): Promise<CarFullInfoBase[]> {
    const brandModelId = encodeURIComponent(params.brand_model_id);
   const generation = encodeURIComponent(params.generation);
   const bodyType = encodeURIComponent(params.body_type);
  return fetchJson<CarFullInfoBase[]>(
    `/api/v1/cars/${brandModelId}/${generation}/${bodyType}/config`
  );
}

/**
 * POST /api/v1/cars/favorites/{car_id}
 * Добавить автомобиль в избранное (требуется JWT)
 */
export async function apiAddFavorite(carId: string, token: string): Promise<void> {
  const response = await fetch(buildUrl(`/api/v1/cars/favorites/${carId}`), {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Не удалось добавить автомобиль в избранное');
  }
}

/**
 * DELETE /api/v1/cars/favorites/{car_id}
 * Удалить автомобиль из избранного (требуется JWT)
 */
export async function apiRemoveFavorite(carId: string, token: string): Promise<void> {
  const response = await fetch(buildUrl(`/api/v1/cars/favorites/${carId}`), {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Не удалось удалить автомобиль из избранного');
  }
}

/**
 * GET /api/v1/cars/favorites
 * Получить список всех избранных автомобилей пользователя (требуется JWT)
 */
export async function apiGetFavorites(token: string): Promise<CarDto[]> {
  const response = await fetch(buildUrl('/api/v1/cars/favorites'), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Не удалось загрузить список избранных автомобилей');
  }

  return response.json() as Promise<CarDto[]>;
}
