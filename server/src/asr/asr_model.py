import io

import soundfile as sf
import torch
from speechbrain.pretrained import EncoderDecoderASR


class ASRModel:
    """
    This class is used to load the ASR model and perform inference.
    """

    def __init__(self, config):
        """
        This function is used to load the ASR model
        :param config: The parsed config file
        """
        self.config = config
        self.model = EncoderDecoderASR.from_hparams(
            source="speechbrain/asr-wav2vec2-commonvoice-en",
            savedir="pretrained_models/asr-wav2vec2-commonvoice-en",
            run_opts={"device": self.config["model"]["device"]},
        )
        if config["model"]["compile"]:
            self.model = torch.compile(self.model)
        self.time = 0
        self.count = 0
        print(f"Running on device: {self.model.device}")

    def asr_dictation(self, data: bytes) -> str:
        """
        This function is used to perform inference on the ASR model
        :param data: The audio data. Any format supported by soundfile SHOULD be supported
        :return: The predicted text
        """
        import time
        t = time.time()
        waveform, samplerate = sf.read(file=io.BytesIO(data), dtype="float32")
        waveform = torch.tensor(waveform)
        waveform = self.model.audio_normalizer(waveform, samplerate)
        batch = waveform.unsqueeze(0)
        rel_length = torch.tensor([1.0])
        predicted_words, _ = self.model.transcribe_batch(batch, rel_length)
        t2 = time.time()
        self.time += t2 - t
        self.count += 1
        print(f"Time taken for inference: {t2 - t}")
        print (f"Average time taken for ASR inference: {self.time/self.count}")
        return predicted_words[0].lower()
