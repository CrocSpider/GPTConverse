import requests
import json
# Send text to OpenAI API and receive response using ChatGPT-4
url = "https://ollama-test.apps.private.k8s.springernature.io/api/generate"
data = {
        "model": "mistral:7b",
            "prompt": "what is the capital of japan",
            "stream": False
            }
response = requests.post(url, json=data)
parsed_response = json.loads(response.text)
#audio_data = response.response  # Assuming API returns audio data directly
print(response.text)
print(parsed_response["response"])