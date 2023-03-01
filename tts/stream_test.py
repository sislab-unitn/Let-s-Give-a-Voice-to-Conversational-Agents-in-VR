import pyaudio
import httpx
from typing import AsyncGenerator
import json
import time
import io



async def text_to_speech( text : str , tts_session) -> AsyncGenerator:
    # get the audio synthetisite from tts.ai
    url_tts_text_to_speech = f'http://localhost:8082/tts'
    tts_request_header_text_to_speech = dict()
    tts_request_header_text_to_speech['Content-Type'] = 'application/json'
    tts_request_header_text_to_speech['Accept'] = 'audio/raw'
    tts_request = {
                "text": text,
                }
    tts_request_body_text_to_speech = json.dumps(tts_request)
    async with tts_session.stream('POST', url_tts_text_to_speech,headers=tts_request_header_text_to_speech,data=tts_request_body_text_to_speech,timeout=10) as response:
        async for chunk in response.aiter_bytes():
            yield chunk
            
            
async def m():
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True)

    tts_session = httpx.AsyncClient()
    text_to_speech_generator = text_to_speech("Hi there, I'm Kumo, your personal movie and tivi, show assistant. What would you like to watch?",tts_session)
    # timer = time.time()
    # buff = io.BytesIO()
    stream.start_stream()
    async for chunk in text_to_speech_generator:
        stream.write(chunk)
        pass
    ## play the audio
    # stream.write(text_to_speech_generator)
        
    stream.stop_stream()
    stream.close()

    p.terminate()



def main():
    import asyncio
    asyncio.run(m())


main()