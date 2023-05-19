import json
from typing import AsyncGenerator

import httpx
from fastapi import Request


class ServerModel:
    """
    Class to handle the server for asr, rasa and tts
    """

    def __init__(self, config):
        self.config = config
        # create session for rasa and tts in order to reuse the connection and reduce latency for successive connections
        self.rasa_session = httpx.AsyncClient()
        self.asr_session = httpx.AsyncClient()
        self.tts_session = httpx.AsyncClient()
        self.bots = dict()
        for bot in self.config["bots"]:
            self.bots[bot["name"]] = bot
        # stores the latest input response from each bot for each sender
        self.bots_responses = dict()
        for bot in self.bots.keys():
            self.bots_responses[bot] = dict()
        print(f"ServerModel initialized with {self.bots.keys()}")
        
    async def speech_to_text(self, request: Request) -> str:
        """speech_to_text gets the audio file from the request and sends it to the asr server
        :param Request request: the request from the client
        :return str: the text from the audio file
        """
        # get the audio file from the request and send it to tts.ai
        url_asr_speech_to_text = f'http{"s" if self.config["server"]["asr_SSL"] else ""}://{self.config["server"]["asr_host"]}:{self.config["server"]["asr_port"]}/asr'
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
        return response_dict["text"]

    async def text_to_text(self, bot: str, input: str, sender: str) -> str:
        """
        Function to handle the text to text request for rasa
        :param bot: the bot to be used
        :param input: the text to be sent to rasa
        :param sender: the sender id to be sent to rasa
        :return: the response from rasa
        """
        # forward the request to rasa server
        rasa_body = dict()
        rasa_body["sender"] = sender
        rasa_body["message"] = input
        try:
            bot_config = self.bots[bot]
        except KeyError:
            return f"{bot} is not a valid bot"
        url_rasa = f'http{"s" if bot_config["rasa_SSL"] else ""}://{bot_config["rasa_host"]}:{bot_config["rasa_port"]}/webhooks/rest/webhook'
        rasa_request_header = dict()
        rasa_request_header["Content-Type"] = "application/json"
        rasa_body = json.dumps(rasa_body)
        response_rasa = await self.rasa_session.post(
            url=url_rasa, data=rasa_body, headers=rasa_request_header
        )
        response_rasa.raise_for_status()
        # response = ""
        # for item in response_rasa.json():
        #     response += item["text"]
        response = '. '.join([item["text"] for item in response_rasa.json()])
        self.bots_responses[sender] = {"transcription":input,"response":response}
        return response

    async def text_to_speech(self,speaker:str, text: str) -> AsyncGenerator:
        """
        Function to handle the text to speech request for tts using the tts model
        :param text: the text to be sent to tts
        :return: the audio file from tts
        """
        # get the audio synthetisite from tts.ai
        url_tts_text_to_speech = f'http{"s" if self.config["server"]["tts_SSL"] else ""}://{self.config["server"]["tts_host"]}:{self.config["server"]["tts_port"]}/tts?speaker={speaker}'
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

    async def get_tracker_data(self, bot: str, sender: str) -> bytes:
        # forward the request to rasa server
        rasa_request_header = dict()
        rasa_request_header["Content-Type"] = "application/json"
        try:
            bot_config = self.bots[bot]
        except KeyError:
            return f"{bot} is not a valid bot"
        url_tracker = f'http{"s" if bot_config["rasa_SSL"] else ""}://{bot_config["rasa_host"]}:{bot_config["rasa_port"]}/conversations/{sender}/tracker'
        response_tracker = await self.rasa_session.get(url=url_tracker)
        response_tracker.raise_for_status()

        response = response_tracker.json()
        try :
            answer = self.bots_responses[sender] | response["slots"]["results_data"] if response["slots"]["results_data"] is not None else self.bots_responses[sender]
        except KeyError:
            answer = self.bots_responses[sender] 
        from pprint import pprint
        pprint (answer) 
        return answer
