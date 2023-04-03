# Instructions

## How to run

The model consists of a very complex architecture, so detailed instructions are provided to run the sample scene.

### Requirements

You will need a working installation of Rasa and Unity. You can check how to install both by following these instructions

- https://rasa.com/docs/rasa/installation/installing-rasa-open-source/
- https://unity.com/download

### The movie database account
Since the model uses real data from The Movie Database, you will need an API KEY in order to make successful requests. 

Register the TMDB and get a API KEY one at this link https://developers.themoviedb.org/3/getting-started/introduction.

### Set up Rasa bots

#### Movie Bot

After you are done installing Rasa, install the other requirements from `rasa_bots/rasa_movie_bot/actions/short requirements.txt`.
Since this model uses sapcy `en_core_web_lg` you will need to install that as well.
You can use `python -m spacy download en_core_web_lg` to download that.

Once that is done, you can go to `rasa_bots/rasa_movie_bot/`. In a terminal write:
```
rasa train --domain ./domain --data ./data
```
This will start the training process using the data in the `./data` and `./domain` folders, with the current configuration

Once that is done, you will need to run two servers from the Rasa end:
- rasa action server, that communicates with the tmdb. Paste the API KEY in `server/rasa_movie_bot/actions/config.toml`
- rasa shell, that will perform the inference
In order to do both, open two terminals and in write respectively
```
rasa run actions
```
```
rasa shell --enable-api
```
by default the two servers will run on localhost on the ports `:5055` and `:5005`

Test that the Rasa is working by writing on the second terminal simple questions like `Hello`
![](assets/Screenshot%202023-03-18%20at%2010.53.48.png)


#### Hospital Rasa

For the hospital scene, you can do almost the same instructions, with a few key differences. 
There are three bots
```
    rasa_bots  -- rasa_triage
            \  -- rasa_anamnesis
             \ -- rasa_operation
```
Similarly as before you will need `spacy==3.5.1` and spacy `en_core_web_lg`
You can use 
```
pip install spacy=3.5.1
python -m spacy download en_core_web_lg
``` 
to download those.

Once that is done, you will need to train and activate each bot.
##### rasa_triage
```
cd rasa_bots/rasa_triage
rasa train --domain ./domain --data ./data
```
This will start the training process, which it will take a while
```
rasa shell --enable-api -p 5005
```
This will turn on the shell, with the REST API, on port 5005
Do not close the shell, you will require the shell running in order to accept incoming request

##### rasa_anamnesis
```
cd rasa_bots/rasa_anamnesis

rasa train --domain ./domain --data ./data
```
This will start the training process, which it will take a while
```
rasa shell --enable-api -p 5006
```
This will turn on the shell, with the REST API, on port 5006
Do not close the shell, you will require the shell running in order to accept incoming request
##### rasa_operation
```
cd rasa_bots/rasa_operation
rasa train --domain ./domain --data ./data
```
This will start the training process, which it will take a while
```
rasa shell --enable-api -p 5007
```
This will turn on the shell, with the REST API, on port 5007
Do not close the shell, you will require the shell running in order to accept incoming request
### Set up the server

Now you will need to run three other servers:       
- ASR server
- TTS server
- A server that ties everything toghever

Fortunately by default there is a ready to go solution

We **HIGHLY** suggest you to run these servers in a different environment from the one you are using Rasa.
In a different `python==3.10` environment install the requirements from:
- `server/requirements.txt`

Open a terminal and write:
```
python server/main.py
```

by default each server is properly configured to run in `localhost` at different ports, respectively `:8081`, `:8082` and `:8080`. You can change these settings the the configuration of each server at `server/asr/config.toml` `server/tts/config.toml` `server/config.toml`
Also by default, the `server/config.toml` has communcation in place for port `5005`, `5006`, `5007` for triage, anamnesis and operation respectively

Now you should have a terminal that each looks something like this
![](assets/Screenshot%202023-03-18%20at%2011.03.36.png)

## Unity scene

Open the Unity project in `UnityKumo3D`. The editor version used for this demo is `2022.2.7f1` but it should work with any newer release. It may even work with older releases as there are very few dependencies.

You can start the demo by opening the scene `UnityKumo3D/Assets/Scenes/Demo.unity`

There is a GameObject called `ServerConnection` that handles the connection to the server. There are also many parameters that you may wish to change for a slighty different experience, but by default the scene should work. 

You can change `bot` with the name of the bot specified in `server/config.toml` in order to switch the bot you are talking to

Just press the play button and start talking.

( Check that your Mic is working btw )