"""
Call Serverless LiteLLM Proxy via OpenAI SDK
"""

# Standard imports
import json
import logging

# Library imports
from openai import OpenAI

# (optional) Set logging level
logging.basicConfig()
logging.getLogger('openai').setLevel(logging.DEBUG)

# Initialize client
# Note: Base URL and API are injected via env vars
client = OpenAI()

# Chat Completions
# https://platform.openai.com/docs/api-reference/images/create

with open("chat_completions.json", 'r', encoding="utf-8") as f:
    payload = json.load(f)
    response = client.chat.completions.create(**payload)
    print(response.choices[0].message.content)

# Embeddings
# https://platform.openai.com/docs/api-reference/embeddings/create

with open("embeddings.json", 'r', encoding="utf-8") as f:
    payload = json.load(f)
    response = client.embeddings.create(
        **payload,
        encoding_format=None
    )
    print(response.data[0].embedding)

# Image Generation
# https://platform.openai.com/docs/api-reference/images/create

with open("image_generation.json", 'r', encoding="utf-8") as f:
    payload = json.load(f)
    payload.pop('seed')  # not supported
    response = client.images.generate(**payload)
    print(response.data[0].b64_json)
