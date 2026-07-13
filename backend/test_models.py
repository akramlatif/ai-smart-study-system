import asyncio
import google.generativeai as genai

genai.configure(api_key='AIzaSyAugpyPkiB0tV9RhNw4h3mY91WJWTOWyKg')

models_to_test = [
    'models/gemini-2.0-flash-lite',
    'models/gemini-2.5-flash-lite',
    'models/gemini-2.5-flash',
    'models/gemini-2.0-flash',
]

async def test_model(model_name):
    try:
        m = genai.GenerativeModel(model_name=model_name)
        r = await m.generate_content_async('Reply with the word OK only.')
        print(f'OK  {model_name}: {r.text[:60]}')
    except Exception as e:
        short = str(e)[:120]
        print(f'ERR {model_name}: {short}')

async def main():
    for m in models_to_test:
        await test_model(m)

asyncio.run(main())
