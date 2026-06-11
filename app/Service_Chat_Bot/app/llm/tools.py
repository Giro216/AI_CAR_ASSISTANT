# app/llm/tools.py

AI_TOOLS = [
	{
		"type": "function",
		"function": {
			"name": "get_user_profile",
			"description": "Получить личную информацию о залогиненном пользователе (имя, фамилия, город, возраст, количество детей). Используй этот инструмент всегда при первом знакомстве или для персонализации автоподбора.",
			"parameters": {
				"type": "object",
				"properties": {},
				"required": []
			}
		}
	},
	{
		"type": "function",
		"function": {
			"name": "search_cars_catalog",
			"description": "Поиск автомобилей в локальной базе данных каталога по бренду (brand) и модели (model). Возвращает список реально существующих моделей авто в системе.",
			"parameters": {
				"type": "object",
				"properties": {
					"brand": {"type": "string", "description": "Бренд автомобиля (например, Audi, BMW, Toyota)"},
					"model": {"type": "string", "description": "Конкретная модель автомобиля (например, A4, X5, Camry)"}
				},
				"required": []
			}
		}
	},
	{
		"type": "function",
		"function": {
			"name": "web_search",
			"description": "Поиск актуальной информации в интернете (цены на авто в РФ на текущий год, отзывы, технические проблемы). Используй его для сверки рыночных цен с бюджетом пользователя перед рекомендацией.",
			"parameters": {
				"type": "object",
				"properties": {
					"query": {"type": "string", "description": "Поисковый запрос (например, 'купить Geely Monjaro цена в России 2024')"}
				},
				"required": ["query"]
			}
		}
	}
]