# 주가정보 fetch 모듈
from dotenv import load_dotenv
import os
load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=os.getenv("GPT_KEY"))

response = client.responses.create(
    model="gpt-4.1",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
