import io
import re
import time
from typing import AsyncGenerator

import soundfile as sf
import torch
from datasets import load_dataset
from transformers import SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Processor


class TTSModel:
    """
    Class that wraps the TTS model and provides the inference method for the server
    """

    def __init__(self, config):
        """
        Initialize the TTS model
        :param config: the parsed configuration file
        """
        self.config = config
        # load xvector containing speaker's voice characteristics from a dataset
        embeddings_dataset = load_dataset(
            "Matthijs/cmu-arctic-xvectors", split="validation"
        )
        self.speaker_embeddings = torch.tensor(
            embeddings_dataset[7306]["xvector"]
        ).unsqueeze(0)

        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

        if config["model"]["compile"]:
            self.processor = torch.compile(self.processor)
            self.model = torch.compile(self.model)
            self.vocoder = torch.compile(self.vocoder)

        print(f"Running on device: {self.model.device}")

    # streaming for tts synthesis in chunks
    async def tts_synthesis_chunked(self, data: str) -> AsyncGenerator:
        """
        Performs the inference on the TTS model, by chunking the input text and returning the audio in chunks according to punctuation marks
        :param data: the input text
        :return: the audio in chunks in PCM_16 format
        """
        io_buffer = io.BytesIO()
        lines = re.split(r"[;,\*\n\\\/\?\.\=\+\!\:\"]", data)
        for line in lines:
            line = line.strip()
            if line != "":
                print(line)
                timer = time.time()
                inputs = self.processor(text=line, return_tensors="pt")
                speech = self.model.generate_speech(
                    inputs["input_ids"], self.speaker_embeddings, vocoder=self.vocoder
                )
                # current position in the file
                cursor = io_buffer.tell()
                sf.write(
                    io_buffer,
                    speech.numpy(),
                    samplerate=self.config["audio"]["sample_rate"],
                    subtype="PCM_16",
                    format="RAW",
                )
                end = io_buffer.tell()
                io_buffer.seek(cursor)
                timer = time.time() - timer
                print(f"Time taken for inference: {timer}")
                yield io_buffer.read(end - cursor)

            # do something with the chunk

    async def tts_synthesis(self, data: str) -> AsyncGenerator:
        """
        Performs the inference on the TTS model and returns the audio in WAV format in a single chunk
        :data: the input text
        :return: the audio in WAV format
        """
        io_buffer = io.BytesIO()
        inputs = self.processor(text=data, return_tensors="pt")
        speech = self.model.generate_speech(
            inputs["input_ids"], self.speaker_embeddings, vocoder=self.vocoder
        )
        sf.write(
            io_buffer,
            speech.numpy(),
            samplerate=self.config["audio"]["sample_rate"],
            subtype="PCM_16",
            format="WAV",
        )
        return io_buffer.getbuffer()
