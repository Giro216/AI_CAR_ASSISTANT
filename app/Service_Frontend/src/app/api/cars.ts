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
  brand?: string;
  model?: string;
  sort?: string;
  limit?: number;
  page?: number;
}): Promise<CatalogData> {
  const search = new URLSearchParams();
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
