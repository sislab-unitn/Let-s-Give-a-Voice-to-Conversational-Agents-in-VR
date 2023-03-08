import httpx
from fastapi import Request
from typing import AsyncGenerator
import json
class ServerModel:
    '''
        Class to handle the server for asr, rasa and tts
    '''
    def __init__(self,config):
        self.self.config = self.config     
        # create session for rasa and tts in order to reuse the connection and reduce latency for successive connections
        self.rasa_session = httpx.AsyncClient()
        self.asr_session = httpx.AsyncClient()
        self.tts_session = httpx.AsyncClient()
        
    async def speech_to_text(self,request:Request) -> str:
        '''
            Function to handle the speech to text request
            :param request: the a Starlette Request object
            :return: the text extracted from the audio file using asr server
        '''
        # get the audio file from the request and send it to tts.ai
        url_asr_speech_to_text = f'http{"s" if self.config["server"]["asr_SSL"] else ""}://{self.config["server"]["asr_host"]}:{self.config["server"]["asr_port"]}/asr'
        asr_request_header_speech_to_text = dict()
        asr_request_header_speech_to_text['Content-Type'] = 'audio/wav'
        asr_request_header_speech_to_text['Transfer-Encoding'] = 'chunked'
        data = request.stream()
        response_asr_speech_to_text = await self.asr_session.post(url = url_asr_speech_to_text ,data = data ,headers= asr_request_header_speech_to_text,timeout=self.config["settings"]["timeout"])
        response_asr_speech_to_text.raise_for_status()
        # split the response and get the text according to carriage return
        asr_content = response_asr_speech_to_text.content.decode('utf-8').split('\r\n')
        try:
            response_dict = json.loads(asr_content[-2])
        except IndexError:
            response_dict = json.loads(asr_content[-1])
        return response_dict['text']

    async def text_to_text(self, input : str, sender : str) -> str:
        '''
            Function to handle the text to text request for rasa
            :param input: the text to be sent to rasa
            :param sender: the sender id to be sent to rasa
            :return: the response from rasa
        '''
        # forward the request to rasa server
        rasa_body = dict()
        rasa_body['sender'] = sender
        rasa_body['message'] = input
        url_rasa = f'http{"s" if self.config["server"]["rasa_SSL"] else ""}://{self.config["server"]["rasa_host"]}:{self.config["server"]["rasa_port"]}/webhooks/rest/webhook'
        rasa_request_header = dict()
        rasa_request_header['Content-Type'] = 'application/json'
        rasa_body = json.dumps(rasa_body)
        response_rasa = await self.rasa_session.post(url = url_rasa ,data = rasa_body,headers=rasa_request_header)
        response_rasa.raise_for_status()
        response = response_rasa.json()[0]["text"]
        return response

    async def text_to_speech(self, text : str ) -> AsyncGenerator:
        '''
            Function to handle the text to speech request for tts using the tts model
            :param text: the text to be sent to tts
            :return: the audio file from tts
        '''
        # get the audio synthetisite from tts.ai
        url_tts_text_to_speech = f'http{"s" if self.config["server"]["tts_SSL"] else ""}://{self.config["server"]["tts_host"]}:{self.config["server"]["tts_port"]}/tts'
        tts_request_header_text_to_speech = dict()
        tts_request_header_text_to_speech['Content-Type'] = 'application/json'
        tts_request_header_text_to_speech['Accept'] = 'audio/raw'
        tts_request = {
                    "text": text,
                    }
        tts_request_body_text_to_speech = json.dumps(tts_request)
        async with self.tts_session.stream('POST', url_tts_text_to_speech,headers=tts_request_header_text_to_speech,data=tts_request_body_text_to_speech,timeout=self.config["settings"]["timeout"]) as response:
            async for chunk in response.aiter_bytes():
                yield chunk
    
        
    async def get_tracker_data(self, sender : str) -> bytes:
        # forward the request to rasa server
        rasa_request_header = dict()
        rasa_request_header['Content-Type'] = 'application/json'
        url_tracker = f'http{"s" if self.config["server"]["rasa_SSL"] else ""}://{self.config["server"]["rasa_host"]}:{self.config["server"]["rasa_port"]}/conversations/{sender}/tracker'
        response_tracker = await self.rasa_session.get(url = url_tracker)
        response_tracker.raise_for_status()
        
        response = response_tracker.json()
        
        try:
            answer = response['slots']['results_data']
            if answer == None:
                answer = dict()
        except KeyError:
            answer = dict()
        try:
            answer['transcription'] = response['latest_message']['text']
        except KeyError:
            answer['transcription'] = ''
        try:
            answer['response'] = response['events'][-2]['text']
        except KeyError:
            answer['response'] = ''
        return answer
