# rasa bots

This folder contains a list of rasa bots:
- movie_bot, a movie and tv show recommendation system
- triage_bot, a simple bot that asks a form for a simulated triage
- anamnesis_bot, a similar bot that asks a more detailed form for a simulated amanesis
- operation_bot, a simple rule based chatbot with 1 turn

In order to run it is required to have a working rasa installation. You can either install it from the rasa website or you can simply create a environment using the enviromnent.yml provided here by
`conda env create -f requirements.yml`
After which activate the environment by `conda activate rasa` and install spacy language model by `python -m spacy download en_core_web_lg`
## usage
Every bot in here can be run by using standard rasa practices:

### movie_bot
Train the model and run with one terminal
```
cd rasa_movie_bot
rasa train --domain ./domain --data ./data
rasa shell --enable-api -p 5004
```
Turn on the action server with the other terminal
```
cd rasa_movie_bot
rasa run actions -p 5054
```
### triage_bot
Train the model and run with one terminal
```
cd rasa_triage_bot
rasa train --domain ./domain --data ./data
rasa shell --enable-api -p 5005
```
Turn on the action server with the other terminal
```
cd rasa_triage_bot
rasa run actions -p 5055
```
### anamnesis_bot
Train the model and run with one terminal
```
cd rasa_anamnesis_bot
rasa train --domain ./domain --data ./data
rasa shell --enable-api -p 5006
```
Turn on the action server with the other terminal
```
cd rasa_anamnesis_bot
rasa run actions -p 5056
```
### operation_bot
Train the model and run with one terminal
```
cd rasa_operation_bot
rasa train --domain ./domain --data ./data
rasa shell --enable-api -p 5007
```
Turn on the action server with the other terminal
```
cd rasa_operation_bot
rasa run actions -p 5057
```