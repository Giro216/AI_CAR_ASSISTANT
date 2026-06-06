export interface UserProfile {
  email: string;
  firstName: string;
  lastName: string;
  city?: string | null;
  age?: number | null;
  childrenCount?: number | null;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

async function handleResponseError(response: Response, defaultMessage: string) {
  const errData = await response.json().catch(() => ({}));
  const message = errData.detail || defaultMessage;
  throw Object.assign(new Error(message), { status: response.status });
}

/**
 * POST /api/v1/auth/register
 */
export async function apiRegister(email: string, password: string): Promise<{ access_token: string }> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    await handleResponseError(response, 'Ошибка при регистрации пользователя');
  }

  // После успешной регистрации автоматически авторизуем пользователя для получения JWT-токена
  return apiLogin(email, password);
}

/**
 * POST /api/v1/auth/login
 */
export async function apiLogin(email: string, password: string): Promise<{ access_token: string }> {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    await handleResponseError(response, 'Неверный email или пароль');
  }

  const data = await response.json();
  return { access_token: data.access_token };
}

/**
 * GET /api/v1/profiles/me
 */
export async function apiGetProfile(token: string): Promise<UserProfile> {
  const response = await fetch(`${API_BASE_URL}/profiles/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw Object.assign(new Error('Profile not found'), { status: 404 });
    }
    await handleResponseError(response, 'Не удалось загрузить профиль пользователя');
  }

  const data = await response.json();

  return {
    email: localStorage.getItem('as_email') || '',
    firstName: data.first_name || '',
    lastName: data.last_name || '',
    city: data.city || '',
    age: data.age || 0,
    childrenCount: data.children_count || 0,
  };
}

/**
 * PUT /api/v1/profiles/me
 */
export async function apiSaveProfile(
  token: string,
  data: Omit<UserProfile, 'email'>
): Promise<UserProfile> {
  const requestBody = {
    first_name: data.firstName,
    last_name: data.lastName,
    city: data.city,
    age: data.age,
    children_count: data.childrenCount,
  };

  const response = await fetch(`${API_BASE_URL}/profiles/me`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    await handleResponseError(response, 'Ошибка при сохранении личной информации');
  }

  const resData = await response.json();

  return {
    email: localStorage.getItem('as_email') || '',
    firstName: resData.first_name,
    lastName: resData.last_name,
    city: resData.city,
    age: resData.age,
    childrenCount: resData.children_count,
  };
}