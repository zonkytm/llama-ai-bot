import requests
import json

import requests
import json

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    },
    data=json.dumps({
        "model": "meta-llama/llama-3.1-405b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": "расскажи про искуственный интелект"
            }
        ]
    })
)

# Обрабатываем ответ
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")
