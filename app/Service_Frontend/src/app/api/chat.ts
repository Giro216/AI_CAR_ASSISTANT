export interface ChatMessageIn {
  message: string;
  conversation_id: string;
  user_id?: string;
}

export interface ChatMessageOut {
  reply: string;
  conversation_id: string;
}

export interface ConversationOut {
  id: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface HistoryMessageOut {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

const API_BASE = (import.meta.env.VITE_GATEWAY_URL as string | undefined) ?? '';

function buildUrl(path: string) {
  if (!API_BASE) {
    return path;
  }
  return `${API_BASE.replace(/\/$/, '')}${path}`;
}

async function apiFetch<T>(
  path: string,
  options: RequestInit,
  token?: string | null
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(buildUrl(path), {
    ...options,
    headers,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Запрос завершился с кодом: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function sendChatMessage(payload: ChatMessageIn, token?: string | null): Promise<ChatMessageOut> {
  return apiFetch<ChatMessageOut>('/api/v1/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }, token);
}

export async function apiGetConversations(userId?: string, token?: string | null): Promise<ConversationOut[]> {
  const query = userId ? `?user_id=${userId}` : '';
  return apiFetch<ConversationOut[]>(`/api/v1/chat/conversations${query}`, {
    method: 'GET',
  }, token);
}

export async function apiGetChatHistory(
  conversationId: string,
  userId?: string,
  token?: string | null
): Promise<HistoryMessageOut[]> {
  const query = userId ? `?user_id=${userId}` : '';
  return apiFetch<HistoryMessageOut[]>(`/api/v1/chat/conversations/${conversationId}/history${query}`, {
    method: 'GET',
  }, token);
}

export async function apiDeleteConversation(
  conversationId: string,
  userId?: string,
  token?: string | null
): Promise<{ detail: string }> {
  const query = userId ? `?user_id=${userId}` : '';
  return apiFetch<{ detail: string }>(`/api/v1/chat/conversations/${conversationId}${query}`, {
    method: 'DELETE',
  }, token);
}

export async function apiDeleteAllConversations(
  userId?: string,
  token?: string | null
): Promise<{ detail: string }> {
  const query = userId ? `?user_id=${userId}` : '';
  return apiFetch<{ detail: string }>(`/api/v1/chat/conversations${query}`, {
    method: 'DELETE',
  }, token);
}