# Instructions

## How to run

The model consists of a very complex architecture, so detailed instructions are provided to run the sample scene.

### Requirements

You will need a working installation of Rasa and Unity. You can check how to install both

### The movie database account
Since the model uses real data from The Movie Database, you will need an API KEY in order to make successful requests. 

Register the TMDB and get a API KEY one at this link https://developers.themoviedb.org/3/getting-started/introduction.

### Set up Rasa

After you are done installing Rasa, install the other requirements from `server/rasa_movie_bot/actions/short requirements.txt`.
Since this model uses sapcy `en_core_web_lg` you will need to install that as well.

Alternatively you can skip the whole installation of rasa and just create an environment with `server/rasa_movie_bot/actions/requirements.txt`
Once that is done, you can go to `server/rasa_movie_bot`. In a terminal write:
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

### Set up the other servers

Now you will need to run three other servers:
- ASR server
- TTS server
- A server that ties everything toghever

We **HIGHLY** suggest you to run these servers in a different environment from the one you are using Rasa.
In a different python environment install the requirements from:
- `server/asr/requirements.txt`
- `server/tts/requirements.txt` `
- `server/requirements.txt`

You can chose to keep the environment separate or use a single enviroment for all three of them.

Open three terminals and in each type respectively:
```
cd server/asr; python asr_server.py
```
```
cd server/tts; python tts_server.py
```
```
cd server; python server.py
```
by default each server is properly configured to run in `localhost` at different ports, respectively `:8081`, `:8082` and `:8080`. You can change these settings the the configuration of each server at `server/asr/config.toml` `server/tts/config.toml` `server/config.toml`

Now you should have three instances of terminals that each look something like this
![](assets/Screenshot%202023-03-18%20at%2011.03.36.png)

## Unity scene

Open the Unity project in `UnityKumo3D`. The editor version used for this demo is `2022.2.7f1` but it should work with any newer release. It may even work with older releases as there are very few dependencies.

You can start the demo by opening the scene `UnityKumo3D/Assets/Scenes/Demo.unity`

There is a GameObject called `ServerConnection` that handles the connection to the server. There are also many parameters that you may wish to change for a slighty different experience, but by default the scene should work. 

Just press the play button and start talking.

( Check that your Mic is working btw )