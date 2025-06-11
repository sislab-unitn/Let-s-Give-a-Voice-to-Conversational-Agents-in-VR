# Automatic Narratives Elicitation App

This is the application for the automatic collection of personal narratives. The collection of narratives is conducted as an dialogue between a narrator and a conversational agent. 

## Demo
Link to the demo:
```
https://www.youtube.com/watch?v=ozpuoEKsTjs
```

## Architecture
In this section the architecture of the system is described.

The system consists of the following modules:
- Virtual Environment - responsible for handling all the interactions with the user. The component acts as a UI of the system.
- Automatic Speech Recognition (ASR) - responsible for storing the ASR model and transcribing the user’s speech to text.
- Conversational Agent (CA) - responsible for storing the ANE model and generating the eliciting questions.
- Text-To-Speech (TTS) - responsible for storing the Text-To-Speech model and synthesizing the eliciting
questions from text format to speech.
- Connection Server (CS) - acts as a middleware between the virtual environment and the models. Addi-
tionally, it stores the name recognition model and is responsible for detecting the name.

The virtual environment was developed with the Unity framework, which gets connected to the VR headsets. This component plays all the messages to the narrator, records the speech in real-time and sends it to the connection server. The user’s speech is recorded using either a built-in or external microphone.

The CS, ASR, CA and TTS components were developed with FastAPI. All the communications between Unity and other components are passed through the connection server. Once the CS receives a user’s utterance from the Unity component, it sends a request to the ASR service, which transcribes it to text. The CS then sends the transcription to the CA service, which passes it through the model and returns the eliciting question. After that, the CS sends the last request to the TTS server, which in turn synthesizes the question to the speech. Finally, the result is returned to Unity which plays the response to the user.

## How to run

### Requirements

You will need a working installation of Unity. To run the back-end side of the system you will need a machine with at least 48GB of GPU.

## Unity scene

Open the Unity project in `vr_ante`. The editor version used for this demo is `2021.3.14f1`. 

You can start the demo by opening the scene `vr_ante/Assets/Scenes/narratives_scene.unity`

All the connections to the servers are handled by the `Assets/connection.cs` file. You may need to change the `host` and `port` parameters depending on where your `connection server` is run.


## Server components

### Automatic Speech Recognition

The default ASR module runs at `http://localhost:8081` and it is built using FastAPI. The code is located in `server/asr`. You can change the host and port in the `server/asr/config.toml` file. The automatic speech recognition is performed by `speechbrain/asr-wav2vec2-commonvoice-it` model, which is loaded locally.

Example of asr request:
```
curl -X POST --header ’Content-Type: audio/wav’ --header ’Transfer-Encoding: chunked’ --data-binary @speaker.wav http://127.0.0.1:8081/asr
```
The result of the request is `JSON` object:
```json
  {
    "text" : "Hello",
  }
```
It is possible to replace the ASR model with any other model that suits your need.

Run the server with:
```
python asr_server.py
```

### Text-to-Speech
The default TTS module runs at `http://localhost:8082` and it is built using FastAPI. The code is located in `server/tts`. You can change the host and port in the `server/tts/config.toml` file. The text synthesis is performed by `tts_models/multilingual/multi-dataset/xtts_v2` model, which is loaded locally. You will need to provide an sample of the voice that the model should clone and add to the config.toml file path to the file. The file should have .wav format and last 5-20 seconds. 

It is possible to replace the TTS model with any other model that suits your need.

Example of tts request:
```
curl -X POST --header ’Content-Type: application/json’ --header ’Accept: audio/raw’ -d ’{"text": "How is it goind?"}’
http://127.0.0.1:8082/tts
```
The result of the request is an AudioResponse file:

It is possible to replace the TTS model with any other model that suits your need.

Run the server with:
```
python tts_server.py
```

### Conversational Agent
The default Conversational Agent module (CA) runs at `http://localhost:8083` and it is built using FastAPI. The code is located in `server/conv_agent`. You can change the host and port in the `server/conv_agent/config.toml` file. The CA is based on `meta-llama/Meta-Llama-3-8B` model and is loaded locally. To use this model you will need to create a huggingface account and ask to grant the permit to the model. To load the model successfully you need to add your huggingface token_id to the config file. In this repo we load only the pre-pretrained model, without any fine-tuning. You may need to change or adapt the model to suit your needs. 

Example of asr request:
```
curl -X POST -H ’Content-Type: application/json’ -d ’{"narrative": "What a nice weather today."}’ http://127.0.0.1:8083/elicit-question
```
The result of the request is `JSON` object:
```json
  {
    "model_out" : "How are you passing your time?",
  }
```

Run the server with:
```
python agent_server.py
```

### Connection server
This is the main server that handles the communications with Unity and passes the requests to ASR, TTS, CA servers. The default connection module runs at `http://localhost:8080` and it is built using FastAPI. The code is located in `server/proxy_server`. 

The main pipeline of the requests is executed through the /pipeline path. It receives the user utterance sent by the unity as sents it to ASR module. The transcribed speech is then sent to the CA module. Finally, the response of the CA is sent to the TTS module and the synthesized speech is returned to the Unity.

Example of request:
```
curl -X POST --header ’Content-Type: audio/wav’ --header ’Transfer-Encoding: chunked’ --header ’Accept: audio/wav’ --data-binary @speaker.wav http://127.0.0.1:8083/pipeline
```
The result of the request is an AudioResponse file:

Example of the name recognition request:
```
curl -X POST --header ’Content-Type: audio/wav’ --header ’Transfer-Encoding: chunked’ --header ’Accept: audio/wav’ --data-binary @speaker.wav http://127.0.0.1:8083/ner
```

The result of the request is an AudioResponse file:

Run the server with:
```
python proxy_server.py
```

## Credits
- Unity for the engine
- Speechbrain and Huggingface for the ASR model https://huggingface.co/speechbrain/asr-wav2vec2-commonvoice-it
- Coqui for the TTS model 
