conda env remove --name rasa
conda create --name rasa python=3.9
conda activate rasa
pip install rasa
pip install tmdbsimple

# remember to activate the environment and be in the correct rasa folder