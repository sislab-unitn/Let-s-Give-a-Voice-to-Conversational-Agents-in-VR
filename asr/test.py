from transformers import SpeechT5Processor, SpeechT5ForSpeechToText
from datasets import load_dataset

dataset = load_dataset("hf-internal-testing/librispeech_asr_demo", "clean", split="validation")
dataset = dataset.sort("id")
sampling_rate = dataset.features["audio"].sampling_rate
example_speech = dataset[0]["audio"]["array"]

processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_asr")
model = SpeechT5ForSpeechToText.from_pretrained("microsoft/speecht5_asr")

inputs = processor(audio=example_speech, sampling_rate=sampling_rate, return_tensors="pt")

predicted_ids = model.generate(**inputs, max_length=100)

transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
print(transcription[0])