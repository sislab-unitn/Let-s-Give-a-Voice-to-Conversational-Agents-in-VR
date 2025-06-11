import io

import torch
import librosa
from datasets import load_dataset
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import soundfile as sf

from speechbrain.inference.ASR import EncoderDecoderASR
from speechbrain.utils import data_utils
from speechbrain.inference.ASR import WhisperASR


class ASRModel:
    """
    This class is used to load the ASR model and perform inference.
    """

    def __init__(self):
        """
        This function is used to load the ASR model
        """
        self.device = 'cuda'
        model_name = "speechbrain/asr-wav2vec2-commonvoice-it"
        self.asr_model = EncoderDecoderASR.from_hparams(source=model_name, savedir="tmpdir", run_opts={"device": self.device})


    def asr_dictation(self, data) -> str:
        """
        This function is used to perform inference on the ASR model
        :param data: The audio data. Any format supported by soundfile SHOULD be supported
        :return: The predicted text
        """
        print("start pred")
        waveform, samplerate = sf.read(file=io.BytesIO(data), dtype="float32")
        sf.write("x.wav", waveform, 16000)
        print("done read")
        
        waveform = torch.tensor(waveform)
        waveform = self.asr_model.audio_normalizer(waveform, samplerate)
        
        speech = waveform.unsqueeze(0).to()
        rel_length = torch.tensor([1.0]).to(self.device)
        predicted_words, _ = self.asr_model.transcribe_batch(speech, rel_length)
        print(predicted_words)
        
        return predicted_words[0].lower()
