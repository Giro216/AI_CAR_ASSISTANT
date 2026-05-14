export interface ChatMessageIn {
  user_id: string;
  message: string;
  conversation_id?: string | null;
}

export interface ChatMessageOut {
  reply: string;
  conversation_id?: string | null;
}

const API_BASE = (import.meta.env.VITE_GATEWAY_URL as string | undefined) ?? '';

function buildUrl(path: string) {
  if (!API_BASE) {
    return path;
  }
  return `${API_BASE.replace(/\/$/, '')}${path}`;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(buildUrl(path), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

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

export async function sendChatMessage(payload: ChatMessageIn): Promise<ChatMessageOut> {
  return postJson<ChatMessageOut>('/api/v1/chat/message', payload);
}
