# Chat Bot Service — Техническое задание и базовый skeleton

## 1. Назначение сервиса

`chat-bot-service` — orchestration layer для AI-автоподборщика.

Сервис отвечает за:

- взаимодействие с OpenRouter / GLM 4.5 Air;
- хранение и управление диалогом;
- profile extraction;
- tool calling;
- orchestration внешних сервисов;
- streaming ответов;
- structured outputs;
- memory management;
- prompt construction;
- conversational flow.

Сервис НЕ хранит каталог машин.
Сервис НЕ занимается аутентификацией.
Сервис НЕ занимается бизнес-логикой каталога.

---

# 2. Архитектура

```text
Frontend (React)
        ↓
Gateway API
        ↓
chat-bot-service
        ↓
 ┌───────────────┬───────────────┬───────────────┐
 │ profile       │ catalog       │ search        │
 │ service       │ service       │ service       │
 └───────────────┴───────────────┴───────────────┘
        ↓
OpenRouter (GLM 4.5 Air)
```

---

# 3. Основные задачи сервиса

## 3.1 Conversation Management

Сервис должен:

- хранить историю чата;
- ограничивать размер контекста;
- суммаризировать старые сообщения;
- собирать профиль пользователя;
- поддерживать multi-turn dialogue.

---

## 3.2 Tool Calling

Сервис должен поддерживать:

- вызовы catalog-service;
- вызовы profile-service;
- вызовы ranking-service (в будущем);
- вызовы search-service.

Пример tools:

```python
get_user_profile
update_user_profile
search_cars
compare_cars
rank_cars
```

---

## 3.3 Structured Output

LLM должна возвращать:

- JSON;
- schema-safe ответы;
- profile updates;
- рекомендации.

---

## 3.4 Memory

Сервис хранит:

- user profile;
- conversation history;
- extracted preferences.

---

# 4. Структура проекта

```text
chat-bot-service/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── chat.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── prompts.py
│   │   └── logger.py
│   │
│   ├── llm/
│   │   ├── client.py
│   │   ├── tools.py
│   │   ├── schemas.py
│   │   └── orchestrator.py
│   │
│   ├── services/
│   │   ├── catalog_service.py
│   │   ├── profile_service.py
│   │   └── memory_service.py
│   │
│   ├── models/
│   │   └── conversation.py
│   │
│   ├── repositories/
│   │   └── conversation_repository.py
│   │
│   └── main.py
│
├── requirements.txt
├── Dockerfile
└── .env
```

# 6. API контракты

## 6.1 POST /chat/message

### Request

```json
{
  "user_id": "123",
  "message": "Мне нужна семейная машина до 25 тысяч"
}
```

---

### Response

```json
{
  "reply": "Для начала уточню несколько моментов...",
  "conversation_id": "conv_123"
}
```