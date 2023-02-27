from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
import time
from datasets import load_dataset

processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")


# load xvector containing speaker's voice characteristics from a dataset
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

timer = time.time()
inputs = processor(text="Hi there,", return_tensors="pt")
speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
timer = time.time() - timer
print(f"Time to generate speech: {timer:.2f} seconds")
sf.write("speech_1.wav", speech.numpy(), samplerate=16000)

timer = time.time()
inputs = processor(text="I’m Kumo, your personal movie and TV show assistant.", return_tensors="pt")
speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
timer = time.time() - timer
print(f"Time to generate speech: {timer:.2f} seconds")
sf.write("speech_2.wav", speech.numpy(), samplerate=16000)

timer = time.time()
inputs = processor(text="What would you like to watch?", return_tensors="pt")
speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
timer = time.time() - timer
print(f"Time to generate speech: {timer:.2f} seconds")
sf.write("speech_3.wav", speech.numpy(), samplerate=16000)