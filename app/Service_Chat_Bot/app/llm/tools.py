AI_TOOLS = [
	{
		"type": "function",
		"function": {
			"name": "validate_cars_in_catalog",
			"description": "Пакетная проверка наличия списка автомобилей в локальной базе данных каталога за ОДИН вызов. Используй этот инструмент всегда перед выдачей финальной рекомендации, передавая туда сразу весь список подобранных машин.",
			"parameters": {
				"type": "object",
				"properties": {
					"cars": {
						"type": "array",
						"description": "Список автомобилей для проверки",
						"items": {
							"type": "object",
							"properties": {
								"brand": {"type": "string", "description": "Бренд (make), например: Toyota"},
								"model": {"type": "string", "description": "Модель, например: Yaris"}
							},
							"required": ["brand", "model"]
						}
					}
				},
				"required": ["cars"]
			}
		}
	},
	{
		"type": "function",
		"function": {
			"name": "batch_web_search",
			"description": "Пакетный поиск актуальной информации в интернете по списку интересующих автомобилей (сверка цен в РФ, отзывы, проблемы). Передавай сюда список моделей для одновременного поиска.",
			"parameters": {
				"type": "object",
				"properties": {
					"queries": {
						"type": "array",
						"description": "Список поисковых запросов для разных моделей",
						"items": {
							"type": "object",
							"properties": {
								"car_name": {"type": "string", "description": "Название модели автомобиля (например, 'Toyota Yaris')"},
								"query": {"type": "string", "description": "Конкретный поисковый запрос (например, 'Toyota Yaris 2012 цена б/у Россия 2026')"}
							},
							"required": ["car_name", "query"]
						}
					}
				},
				"required": ["queries"]
			}
		}
	}
]