# Architecture

![Alt text](assets/model.png)


In here is reported a demo of the architecture so far


It consists of:
- Unity module to record and play audio
- Custom Connection Server implemented in python using FastAPI. This server handles the connection between ASR, Rasa and TTS
- ASR module, using Wav2Vec2
- TTS module, using Speech_T5
- Rasa, custom conversational agent
- The Movie DataBase for query


For now a request consists of the following steps:
- Unity records the audio
- Unity sends the full audio to the connection server
- The connection server sends the audio the ASR server to get the text transcription ( ASR )
- The connection server sends the text transcription received from the ASR server to Rasa server
- Rasa server receives the request and performs the NLU inference, eventually doing custom actions
  - A custom action may require the connection to TheMovieDataBase for the query answer
- The connection server receives the response from Rasa
- The connection server also requests from rasa tracker the current state
- The connection server sends a requests to TTS server for the speech synthesis ( TTS )
- The connection server receives the data and sends it back to Unity, by streaming chunks
- Unity plays the audio file ( with LipSync )