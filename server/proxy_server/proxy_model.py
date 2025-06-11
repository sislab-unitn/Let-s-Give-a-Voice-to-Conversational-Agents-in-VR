import json
from typing import AsyncGenerator

import httpx
from fastapi import Request


class ProxyModel:
    """
    Class to handle the server for asr, rasa and tts
    """

    def __init__(self, config):
        self.config = config
        # create session for rasa and tts in order to reuse the connection and reduce latency for successive connections
        self.agent_session = httpx.AsyncClient()
        self.asr_session = httpx.AsyncClient()
        self.tts_session = httpx.AsyncClient()
        
        
    async def speech_to_text(self, request: Request):
        url_asr_speech_to_text = f'http://{self.config["server"]["asr_host"]}:{self.config["server"]["asr_port"]}/asr'
        
        asr_request_header_speech_to_text = dict()
        asr_request_header_speech_to_text["Content-Type"] = "audio/wav"
        asr_request_header_speech_to_text["Transfer-Encoding"] = "chunked"
        
        data = request.stream()
        
        response_asr_speech_to_text = await self.asr_session.post(
            url=url_asr_speech_to_text,
            data=data,
            headers=asr_request_header_speech_to_text,
            timeout=self.config["settings"]["timeout"],
        )
        
        response_asr_speech_to_text.raise_for_status()
        # split the response and get the text according to carriage return
        asr_content = response_asr_speech_to_text.content.decode("utf-8").split("\r\n")
        try:
            response_dict = json.loads(asr_content[-2])
        except IndexError:
            response_dict = json.loads(asr_content[-1])
        return ''.join(response_dict["text"])


    async def text_to_text(self, narrative):
        # forward the request to agent server
        url_agent = f'http://{self.config["server"]["agent_host"]}:{self.config["server"]["agent_port"]}/elicit-question'

        request_header = dict()
        request_header["Content-Type"] = "application/json"

        body = {
            "narrative": narrative
        }

        response_agent = await self.agent_session.post(
            url=url_agent, data=json.dumps(body), headers=request_header
        )
        response_agent.raise_for_status()

        return response_agent.json()


    async def text_to_speech_chunked(self, text) -> AsyncGenerator:
        """
        Function to handle the text to speech request for tts using the tts model
        :param text: the text to be sent to tts
        :return: the audio file from tts
        """
        # get the audio synthetisite from tts.ai
        url_tts_text_to_speech = f'http://{self.config["server"]["tts_host"]}:{self.config["server"]["tts_port"]}/tts'
        
        tts_request_header_text_to_speech = dict()
        tts_request_header_text_to_speech["Content-Type"] = "application/json"
        tts_request_header_text_to_speech["Accept"] = "audio/raw"
        
        tts_request = {
            "text": text,
        }
        
        tts_request_body_text_to_speech = json.dumps(tts_request)
        async with self.tts_session.stream(
            "POST",
            url_tts_text_to_speech,
            headers=tts_request_header_text_to_speech,
            data=tts_request_body_text_to_speech,
            timeout=self.config["settings"]["timeout"],
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk


    async def text_to_speech(self, text):
        tts_request_header_text_to_speech = dict()
        tts_request_header_text_to_speech["Accept"] = "audio/raw"

        url_tts_text_to_speech = f'http://{self.config["server"]["tts_host"]}:{self.config["server"]["tts_port"]}/tts_synthesis_full?text={text}'

        request_header = dict()
        request_header["Content-Type"] = "application/json"
        
        response_tts = await self.tts_session.get(
            url=url_tts_text_to_speech, headers=request_header
        )
        response_tts.raise_for_status()

        return response_tts
