import os
from openai import OpenAI
import base64
import requests

api_key = 'key'


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


image_path = r"你的文件路径"
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

client = OpenAI(
    api_key=api_key,
    base_url='https://api.gptniux.com/v1/chat/completions'
)

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What’s in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ],
    "max_tokens": 300
}

try:
    response = requests.post(client.base_url, headers=headers, json=payload)
    response_json = response.json()
    assistant_message = response_json['choices'][0]['message']['content']
    print("返回结果:", assistant_message)
except Exception as ex:
    print("Exception:", ex)
