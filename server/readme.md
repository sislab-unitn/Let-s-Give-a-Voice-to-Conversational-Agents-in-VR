# server

Install the requirements from the `requirements.txt` file or create an environment with the bundled `environment.yml` file

configure the `config.toml` file using the correct port and address you want for this server and the other asr and tts servers

run using `python server.py`

by default the rasa servers are not run automatically, therefore you should start them manually


You can debug by running `python text_talker.py` as it provides the same interface as the standard server, but without `ASR` and `TTS`, by allowing a text based conversation.