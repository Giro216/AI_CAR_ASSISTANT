TOOLS = [
	{
		"type": "function",
		"function": {
			"name": "search_cars",
			"description": "Search cars in catalog",
			"parameters": {
				"type": "object",
				"properties": {
					"budget": {
						"type": "integer"
					},
					"body_type": {
						"type": "string"
					},
					"fuel_type": {
						"type": "string"
					}
				},
				"required": ["budget"]
			}
		}
	}
]
