import os
import time
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_completion(prompt, model="gpt-3.5-turbo"):
    # TODO: catch error: "openai.error.ServiceUnavailableError: The server is overloaded or not ready yet."
    messages = [{"role": "user", "content": prompt}]
    delay = 1
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0,  # this is the degree of randomness of the model's output
            )
            message = response.choices[0].message["content"]  # type: ignore
            return message.strip()
        except Exception as e:
            print(f'{e}, retrying...')
            time.sleep(delay)
            delay *= 2
