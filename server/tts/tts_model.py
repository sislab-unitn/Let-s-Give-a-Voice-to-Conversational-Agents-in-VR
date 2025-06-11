import io
import re
import time
from typing import AsyncGenerator

import soundfile as sf
import torch
from datasets import load_dataset
from transformers import SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Processor

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig


class TTSModel:
    """
    Class that wraps the TTS model and provides the inference method for the server
    """

    def __init__(self, config):
        """
        Initialize the TTS model
        :param config: the parsed configuration file
        """
        device = config['model']['device']

        self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        self.config = config
  
    
    async def tts_synthesis_chunked(self, data: str) -> AsyncGenerator:
        """
        Performs the inference on the TTS model, by chunking the input text and returning the audio in chunks according to punctuation marks
        :param data: the input text
        :return: the audio in chunks in PCM_16 format
        """

        io_buffer = io.BytesIO()
        data = data.replace('.', ',')
        print(data)
        lines = [data]
        for line in lines:
            line = line.strip()
            if line != "":
                timer = time.time()

                out = self.tts.tts(text=line.strip(), language="it", speaker_wav=self.config["audio"]["speaker_wav"])

                cursor = io_buffer.tell()
                sf.write(
                    io_buffer,
                    out,
                    samplerate=self.config["audio"]["sample_rate"],
                    subtype="PCM_16",
                    format="RAW",
                )
                end = io_buffer.tell()
                io_buffer.seek(cursor)

                yield io_buffer.read(end - cursor) + b"\x00\x00" * self.config["audio"]["pause_length"]


    async def tts_synthesis(self, data: str) -> bytes:
        """
        Performs the inference on the TTS model and returns the audio in WAV format in a single chunk
        :data: the input text
        :return: the audio in WAV format
        """
        out = self.tts.tts(text=data, language="it", speaker_wav=self.config["audio"]["speaker_wav"])
        io_buffer = io.BytesIO()

        sf.write(
            io_buffer,
            out,
            samplerate=self.config["audio"]["sample_rate"],
            subtype="PCM_16",
            format="WAV",
        )
        
        return io_buffer.getbuffer().tobytes()
