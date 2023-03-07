from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
import time
from datasets import load_dataset
import io
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
# processor = torch.compile(processor)
# model = torch.compile(model)
# vocoder = torch.compile(vocoder)

# load xvector containing speaker's voice characteristics from a dataset
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
text = "I'm thinking"
timer = time.time()
io_buffer = io.BytesIO()
for line in text.split('.'):
    inputs = processor(text=line, return_tensors="pt")
    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    sf.write(io_buffer, speech.numpy(), samplerate=16000,subtype="PCM_16",format = "WAV")
with open("feedback.wav", "wb") as f:
    f.write(io_buffer.getbuffer())
timer = time.time() - timer

print(f"Time to generate speech: {timer:.2f} seconds")
