from together import Together
from services.config import TOKEN_AI, MODEL_AI

client = Together(api_key=TOKEN_AI)

def get_gpt_response(prompt: str, user_message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_AI,
        messages=[{"role": "system", "content": prompt + user_message}],
    )
    return response.choices[0].message.content